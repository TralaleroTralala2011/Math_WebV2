import asyncio, uuid, time

class BattleManager:
    """Single-process realtime battle coordinator. For multi-worker production, replace storage with Redis."""
    def __init__(self): self.rooms={}
    def create(self, p1, p2, topics, grade=12):
        room_id=uuid.uuid4().hex
        self.rooms[room_id]={"id":room_id,"players":{p1:None,p2:None},"topics":topics[:5],"grade":grade,"created_at":time.time(),"status":"waiting"}
        return self.rooms[room_id]
    def get(self,rid): return self.rooms.get(rid)
    def attach(self,rid,user_id,ws):
        room=self.rooms.get(rid)
        if not room or user_id not in room["players"]: return False
        room["players"][user_id]=ws
        if all(room["players"].values()): room["status"]="running"
        return True
    async def broadcast(self,rid,payload):
        room=self.rooms.get(rid)
        if not room: return
        dead=[]
        for uid,ws in room["players"].items():
            if ws:
                try: await ws.send_json(payload)
                except Exception: dead.append(uid)
        for uid in dead: room["players"][uid]=None

battle_manager=BattleManager()
