"""Optional real-TCP smoke test: two independent clients, Chat and Battle.

Run: python tools/test_live_realtime_tcp.py
This is not a two-physical-device certification.
"""
import asyncio
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx
import websockets

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'backend'


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


async def main():
    port = free_port()
    with tempfile.TemporaryDirectory(prefix='mathweb-tcp-') as tmp:
        env = {**os.environ, 'MATHWEB_DB_PATH':str(Path(tmp)/'users.db')}
        process = subprocess.Popen(
            [sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port',str(port),'--log-level','error'],
            cwd=BACKEND,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        try:
            async with httpx.AsyncClient(base_url=f'http://127.0.0.1:{port}',timeout=8) as http:
                for _ in range(70):
                    if process.poll() is not None:
                        raise RuntimeError('Backend stopped unexpectedly')
                    try:
                        r=await http.get('/health')
                        if r.status_code==200:break
                    except httpx.TransportError:
                        pass
                    await asyncio.sleep(.15)
                else:raise RuntimeError('Backend did not become ready')
                users=[]
                for name in ('TCPStudentA','TCPStudentB'):
                    r=await http.post('/api/auth/register',json={'username':name,'password':'SafePass1234!'})
                    r.raise_for_status()
                    users.append(r.json())
                a,b=users
                ha={'Authorization':'Bearer '+a['token']}
                hb={'Authorization':'Bearer '+b['token']}
                r=await http.post('/api/friends/request',json={'player_id':b['user']['player_id']},headers=ha)
                r.raise_for_status()
                req=(await http.get('/api/friends/requests',headers=hb)).json()[0]
                r=await http.post(f"/api/friends/accept/{req['id']}",headers=hb)
                r.raise_for_status()
                uri_a=f"ws://127.0.0.1:{port}/api/live/chat/{b['user']['id']}"
                uri_b=f"ws://127.0.0.1:{port}/api/live/chat/{a['user']['id']}"
                async with websockets.connect(uri_a,open_timeout=8) as wa:
                    await wa.send(json.dumps({'type':'auth','token':a['token']}))
                    assert json.loads(await asyncio.wait_for(wa.recv(),5))['type']=='ready'
                    async with websockets.connect(uri_b,open_timeout=8) as wb:
                        await wb.send(json.dumps({'type':'auth','token':b['token']}))
                        assert json.loads(await asyncio.wait_for(wb.recv(),5))['type']=='ready'
                        await wa.send(json.dumps({'type':'ping'}))
                        assert json.loads(await asyncio.wait_for(wa.recv(),5))['type']=='pong'
                        r=await http.post(f"/api/chat/{b['user']['id']}/messages",headers=ha,json={'content':'Tin nhắn từ thiết bị giả lập A'})
                        r.raise_for_status()
                        packet_a=json.loads(await asyncio.wait_for(wa.recv(),5))
                        packet_b=json.loads(await asyncio.wait_for(wb.recv(),5))
                        assert packet_a['message']['id']==packet_b['message']['id']==r.json()['id']
                        assert packet_b['message']['content']=='Tin nhắn từ thiết bị giả lập A'
                    # Reconnect after the other client has left.
                    async with websockets.connect(uri_b,open_timeout=8) as wb2:
                        await wb2.send(json.dumps({'type':'auth','token':b['token']}))
                        assert json.loads(await asyncio.wait_for(wb2.recv(),5))['type']=='ready'
                        r=await http.post(f"/api/chat/{a['user']['id']}/messages",headers=hb,json={'content':'Tin nhắn sau kết nối lại'})
                        r.raise_for_status()
                        assert json.loads(await asyncio.wait_for(wb2.recv(),5))['message']['id']==r.json()['id']
                        assert json.loads(await asyncio.wait_for(wa.recv(),5))['message']['id']==r.json()['id']
                print('PASS: Chat 2 TCP clients, persistence, ping/pong and reconnect')
                # Battle uses a different authenticated WS endpoint with
                # authoritative SQLite match state, not client-supplied scores.
                invite=await http.post('/api/matchmaking/invite',headers=ha,
                                       json={'player_id':b['user']['player_id']})
                invite.raise_for_status()
                match_id=invite.json()['match_id']
                battle_a=f"ws://127.0.0.1:{port}/api/ai/battle/ws/{match_id}/{a['user']['id']}?token={a['token']}"
                battle_b=f"ws://127.0.0.1:{port}/api/ai/battle/ws/{match_id}/{b['user']['id']}?token={b['token']}"
                async with websockets.connect(battle_a,open_timeout=8) as wa:
                    state=json.loads(await asyncio.wait_for(wa.recv(),5))
                    assert state['type']=='state' and state['progress']['correct']==0
                    async with websockets.connect(battle_b,open_timeout=8) as wb:
                        state=json.loads(await asyncio.wait_for(wb.recv(),5))
                        assert state['type']=='state'
                        assert json.loads(await asyncio.wait_for(wa.recv(),5))['type']=='player_joined'
                        await wa.send(json.dumps({'type':'progress','correct':999,'winner_id':a['user']['id']}))
                        state=json.loads(await asyncio.wait_for(wa.recv(),5))
                        assert state['type']=='state' and state['progress']['correct']==0
                        assert json.loads(await asyncio.wait_for(wb.recv(),5))['type']=='sync'
                    assert json.loads(await asyncio.wait_for(wa.recv(),5))['type']=='player_left'
                    async with websockets.connect(battle_b,open_timeout=8) as wb2:
                        state=json.loads(await asyncio.wait_for(wb2.recv(),5))
                        assert state['type']=='state'
                        assert json.loads(await asyncio.wait_for(wa.recv(),5))['type']=='player_joined'
                print('PASS: Battle 2 TCP clients, server-authoritative state, reconnect')
        finally:
            process.terminate()
            try:process.communicate(timeout=8)
            except subprocess.TimeoutExpired:process.kill();process.communicate()


if __name__=='__main__':
    asyncio.run(main())
