"""Authenticated friend-only WebRTC signalling for one-to-one calls.

No audio, video or SDP is stored in SQLite. Signalling is process-local;
production multi-replica deployments need a shared signalling broker.
"""
import asyncio
import os
import re
import time
from uuid import uuid4

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from ..auth.routes import get_current_user
from .routes import validate_chat_target

router = APIRouter(tags=["Friends call signalling"])
_sockets = {}
_calls = {}
_last_invite = {}

_ORIGIN_RE = re.compile(r"^https?://(?:localhost|127\.0\.0\.1|10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}|tralalerotralala2011\.github\.io)(?::\d+)?$", re.I)


def _allowed_origin(websocket):
    origin = websocket.headers.get('origin')
    extras = {s.strip().rstrip('/') for s in os.getenv('MATHWEB_CALL_ORIGINS', '').split(',') if s.strip()}
    return not origin or bool(_ORIGIN_RE.fullmatch(origin)) or origin in extras


async def _notify(user_id, event):
    ws = _sockets.get(user_id)
    if ws:
        try:
            await ws.send_json(event)
            return True
        except Exception:
            if _sockets.get(user_id) is ws:
                _sockets.pop(user_id, None)
    return False


def _call_for_user(user_id):
    return next(((cid, call) for cid, call in _calls.items() if user_id in (call['caller'], call['callee'])), None)


async def _expire_ring(call_id):
    await asyncio.sleep(50)
    call = _calls.get(call_id)
    if call and call['status'] == 'ringing':
        await _end_call(call_id, call['caller'], 'no-answer')


async def _end_call(call_id, who, reason='ended'):
    call = _calls.pop(call_id, None)
    if not call:
        return
    other = call['callee'] if who == call['caller'] else call['caller']
    await _notify(other, {'type': 'call-ended', 'call_id': call_id, 'reason': reason})


@router.websocket('/api/live/calls')
async def friend_calls(ws: WebSocket):
    if not _allowed_origin(ws):
        await ws.close(code=1008, reason='Origin not allowed')
        return
    await ws.accept()
    user_id = None
    try:
        first = await asyncio.wait_for(ws.receive_json(), timeout=8)
        if not isinstance(first, dict) or first.get('type') != 'auth' or not isinstance(first.get('token'), str):
            await ws.close(code=1008, reason='Login required')
            return
        try:
            user = get_current_user('Bearer ' + first['token'])
            user_id = int(user['id'])
        except (HTTPException, ValueError, KeyError, TypeError):
            await ws.close(code=1008, reason='Invalid login')
            return
        previous = _sockets.get(user_id)
        if previous and previous is not ws:
            try:
                await previous.close(code=1000, reason='Another tab opened calls')
            except Exception:
                pass
        _sockets[user_id] = ws
        await ws.send_json({'type': 'ready'})
        while True:
            packet = await ws.receive_json()
            if not isinstance(packet, dict):
                continue
            kind = packet.get('type')
            if kind == 'ping':
                await ws.send_json({'type': 'pong'})
                continue
            if kind == 'call-request':
                try:
                    peer = int(packet.get('peer_id'))
                except (ValueError, TypeError):
                    await ws.send_json({'type':'call-error', 'detail':'Người nhận không hợp lệ.'})
                    continue
                mode = packet.get('mode')
                if mode not in ('audio', 'video') or peer == user_id or peer <= 0:
                    await ws.send_json({'type':'call-error','detail':'Cuộc gọi không hợp lệ.'})
                    continue
                try:
                    validate_chat_target(user_id, peer)
                except HTTPException:
                    await ws.send_json({'type':'call-error','detail':'Chỉ gọi được cho bạn bè đã chấp nhận.'})
                    continue
                now = time.monotonic()
                if now - _last_invite.get(user_id, 0) < 3:
                    await ws.send_json({'type':'call-error','detail':'Vui lòng đợi trước khi gọi lại.'})
                    continue
                _last_invite[user_id] = now
                if _call_for_user(user_id) or _call_for_user(peer):
                    await ws.send_json({'type':'call-error','detail':'Một trong hai người đang có cuộc gọi.'})
                    continue
                if peer not in _sockets:
                    await ws.send_json({'type':'call-error','detail':'Bạn bè cần mở Chat để nhận cuộc gọi.'})
                    continue
                cid = uuid4().hex
                _calls[cid] = {'caller':user_id, 'callee':peer, 'mode':mode, 'status':'ringing'}
                asyncio.create_task(_expire_ring(cid))
                delivered = await _notify(peer, {'type':'incoming-call','call_id':cid,'peer_id':user_id,'mode':mode, 'username':str(user['username'])[:90]})
                if delivered:
                    await ws.send_json({'type':'call-ringing','call_id':cid,'peer_id':peer,'mode':mode})
                else:
                    _calls.pop(cid,None)
                    await ws.send_json({'type':'call-error','detail':'Không thể kết nối tới người nhận.'})
                continue
            if kind == 'call-cancel':
                current = _call_for_user(user_id)
                if current and current[1]['caller'] == user_id and current[1]['status'] == 'ringing':
                    await _end_call(current[0], user_id, 'cancelled')
                continue
            cid = packet.get('call_id')
            call = _calls.get(cid) if isinstance(cid, str) and len(cid) == 32 else None
            if not call or user_id not in (call['caller'], call['callee']):
                await ws.send_json({'type':'call-error','detail':'Cuộc gọi không còn tồn tại.'})
                continue
            other = call['callee'] if user_id == call['caller'] else call['caller']
            if kind == 'call-accept' and user_id == call['callee'] and call['status'] == 'ringing':
                try:
                    validate_chat_target(user_id, other)
                except HTTPException:
                    await _end_call(cid,user_id,'not-friends')
                    continue
                call['status'] = 'accepted'
                await _notify(other, {'type':'call-accepted','call_id':cid})
            elif kind == 'call-reject' and call['status'] == 'ringing':
                await _end_call(cid,user_id,'rejected')
            elif kind == 'call-end':
                await _end_call(cid,user_id,'ended')
            elif kind in ('call-offer','call-answer','call-ice') and call['status'] == 'accepted':
                # The caller originates the offer; the callee answers. ICE is bidirectional.
                if kind == 'call-offer' and user_id != call['caller']:
                    continue
                if kind == 'call-answer' and user_id != call['callee']:
                    continue
                payload = packet.get('payload')
                limit = 128000 if kind in ('call-offer','call-answer') else 8000
                if not isinstance(payload, dict) or len(str(payload)) > limit:
                    continue
                if kind == 'call-ice':
                    if not isinstance(payload.get('candidate'), str) or len(payload['candidate']) > 4096:
                        continue
                elif payload.get('type') != ('offer' if kind == 'call-offer' else 'answer') or not isinstance(payload.get('sdp'), str):
                    continue
                await _notify(other, {'type':kind, 'call_id':cid, 'payload':payload})
    except (WebSocketDisconnect, asyncio.TimeoutError, ValueError, TypeError):
        pass
    finally:
        if user_id is not None and _sockets.get(user_id) is ws:
            _sockets.pop(user_id,None)
            current = _call_for_user(user_id)
            if current:
                await _end_call(current[0], user_id, 'disconnected')
