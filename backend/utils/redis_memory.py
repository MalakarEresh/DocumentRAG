import redis.asyncio as redis
from config import settings
import json

redis_client = redis.from_url(settings.REDIS_URL)

TTL_SECONDS = 86400  

async def get_chat_history(session_id: str, limit: int = 10):
    key = f"chat:{session_id}"
    raw = await redis_client.lrange(key, -limit, -1)
    return [json.loads(msg.decode()) for msg in raw]

async def add_to_history(session_id: str, role: str, content: str):
    key = f"chat:{session_id}"

   
    message = json.dumps({"role": role, "content": content})

 
    await redis_client.rpush(key, message)

    await redis_client.expire(key, TTL_SECONDS)
