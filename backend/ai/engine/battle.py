import time
import uuid


class BattleManager:
    """Coordinator trong một process. Production nhiều worker nên dùng Redis."""

    def __init__(self):
        self.rooms = {}

    def create(self, player1, player2, topics, grade=10):
        room_id = uuid.uuid4().hex
        room = {
            "id": room_id,
            "players": {player1: None, player2: None},
            "topics": topics[:5],
            "grade": grade,
            "created_at": time.time(),
            "status": "waiting",
        }
        self.rooms[room_id] = room
        return room

    def get(self, room_id):
        return self.rooms.get(room_id)

    def attach(self, room_id, user_id, websocket):
        room = self.rooms.get(room_id)
        if not room or user_id not in room["players"]:
            return False
        room["players"][user_id] = websocket
        if all(room["players"].values()):
            room["status"] = "running"
        return True

    async def broadcast(self, room_id, payload):
        room = self.rooms.get(room_id)
        if not room:
            return
        dead = []
        for user_id, websocket in room["players"].items():
            if websocket:
                try:
                    await websocket.send_json(payload)
                except Exception:
                    dead.append(user_id)
        for user_id in dead:
            room["players"][user_id] = None


battle_manager = BattleManager()
