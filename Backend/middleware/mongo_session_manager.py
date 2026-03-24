from datetime import datetime, timedelta

from config.settings import settings
from core.mongo_store import messages_collection, sessions_collection


class MongoSessionManager:
    def __init__(self):
        self.expiry_time = settings.chat_expiry_time

    def _expiry(self) -> datetime:
        return datetime.utcnow() + timedelta(seconds=self.expiry_time)

    def create_session(self, token: str):
        sessions_collection.update_one(
            {"token": token},
            {
                "$setOnInsert": {
                    "token": token,
                    "created_at": datetime.utcnow(),
                },
                "$set": {
                    "updated_at": datetime.utcnow(),
                    "expires_at": self._expiry(),
                },
            },
            upsert=True,
        )
        return {"status": "created", "token": token}

    def delete_session(self, token: str):
        result = sessions_collection.delete_one({"token": token})
        if result.deleted_count > 0:
            return {"status": "deleted", "token": token}
        return {"status": "not_found", "token": token}

    def store_message(self, token: str, role: str, message: str):
        now = datetime.utcnow()

        sessions_collection.update_one(
            {"token": token},
            {
                "$setOnInsert": {
                    "token": token,
                    "created_at": now,
                },
                "$set": {
                    "updated_at": now,
                    "expires_at": self._expiry(),
                },
            },
            upsert=True,
        )

        messages_collection.insert_one(
            {
                "token": token,
                "role": role,
                "message": message,
                "timestamp": now,
            }
        )

        history = self.get_history(token)
        return {"status": "message_stored", "count": len(history)}

    def get_history(self, token: str):
        cursor = messages_collection.find(
            {"token": token},
            {"_id": 0, "role": 1, "message": 1, "timestamp": 1},
        ).sort("timestamp", 1)
        return list(cursor)


mongo_session_manager = MongoSessionManager()