"""Authenticated, friends-only live chat notifications, REST send is source of truth.

Single-process fanout only; frontend automatically falls back to REST polling.
Scale-out deployments should replace this hub with Redis pub/sub.
"""
import asyncio
import json
from collections import defaultdict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from ..auth.routes import get_current_user
from .routes import validate_chat_target

router=APIRouter(tags=['Chat realtime'])
_clients=defaultdict(set)
_loop=None


@router.websocket('/api/live/chat/{friend_id}')
async def live_chat(websocket:WebSocket,friend_id:int):
    global _loop
    await websocket.accept()
    try:
        first=await asyncio.wait_for(websocket.receive_json(), timeout=8)
        if not isinstance(first,dict) or first.get('type')!='auth' or not isinstance(first.get('token'),str):
            await websocket.close(code=1008,reason='Authentication required');return
        try:
            user=get_current_user('Bearer '+first['token'])
            validate_chat_target(int(user['id']),friend_id)
        except HTTPException:
            await websocket.close(code=1008,reason='Not authorized');return
        user_id=int(user['id']);_loop=asyncio.get_running_loop()
        # The chosen conversation is explicitly scoped to an accepted friendship.
        _clients[user_id].add((websocket,friend_id))
        await websocket.send_json({'type':'ready','friend_id':friend_id})
        while True:
            message=await websocket.receive_json()
            if isinstance(message,dict) and message.get('type')=='ping':
                await websocket.send_json({'type':'pong'})
            # No arbitrary client event broadcasting. All messages are validated
            # and persisted by the existing authenticated REST endpoint.
    except (WebSocketDisconnect,asyncio.TimeoutError,ValueError,json.JSONDecodeError):
        pass
    finally:
        # A handshake failure has no user_id or registered client.
        if 'user_id' in locals():
            _clients[user_id].discard((websocket,friend_id))
            if not _clients[user_id]:_clients.pop(user_id,None)


async def _publish(sender,receiver,message):
    for recipient,partner in ((sender,receiver),(receiver,sender)):
        for ws,friend_id in list(_clients.get(recipient,())):
            if friend_id!=partner:continue
            try:await ws.send_json({'type':'message','message':message})
            except Exception:
                _clients[recipient].discard((ws,friend_id))


def push_chat_message(sender,receiver,message):
    """Call safely from a synchronous FastAPI REST endpoint after COMMIT."""
    if _loop and _loop.is_running():
        try:_loop.call_soon_threadsafe(lambda:asyncio.create_task(_publish(sender,receiver,message)))
        except RuntimeError:pass
