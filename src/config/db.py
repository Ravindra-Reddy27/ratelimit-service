import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient
import os

REDIS_URL = os.getenv("REDIS_URL")
MONGO_URL = os.getenv("DATABASE_URL")

# Initialize connections
redis_client = redis.from_url(REDIS_URL, decode_responses=True)
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client.ratelimitdb
clients_collection = db.clients