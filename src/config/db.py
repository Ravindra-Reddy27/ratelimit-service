import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient
import os

# We will use environment variables later, but default to localhost for now
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
MONGO_URL = os.getenv("DATABASE_URL", "mongodb://mongo:27017")

# Initialize connections
redis_client = redis.from_url(REDIS_URL, decode_responses=True)
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client.ratelimitdb
clients_collection = db.clients