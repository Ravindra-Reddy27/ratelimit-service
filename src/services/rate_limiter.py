import time
import math
from src.config.db import redis_client, clients_collection

async def check_limit(client_id: str, path: str) -> dict:
    # 1. Fetch the client's rules from MongoDB
    client = await clients_collection.find_one({"clientId": client_id})
    if not client:
        # If client doesn't exist, block them safely
        return {"allowed": False, "retryAfter": 60, "resetTime": ""}

    max_requests = client["maxRequests"]
    window_seconds = client["windowSeconds"]

    # 2. Create a unique Redis key for this exact client and path combination
    redis_key = f"rate_limit:{client_id}:{path}"
    
    # 3. Get the current time in seconds
    now = time.time()
    
    # 4. Use a Redis Pipeline to get the current state
    # We store "tokens" (how many requests left) and "last_refill" (timestamp)
    bucket = await redis_client.hmget(redis_key, ["tokens", "last_refill"])
    tokens = bucket[0]
    last_refill = bucket[1]

    if tokens is None or last_refill is None:
        # First time seeing this client/path! Give them a full bucket.
        tokens = float(max_requests)
        last_refill = now
    else:
        # Convert Redis strings back to numbers
        tokens = float(tokens)
        last_refill = float(last_refill)
        
        # Calculate how much time passed since they last made a request
        time_passed = now - last_refill
        
        # Calculate how many tokens to add back based on time passed
        refill_rate = max_requests / window_seconds
        tokens_to_add = time_passed * refill_rate
        
        # Add tokens, but don't exceed their maximum limit
        tokens = min(max_requests, tokens + tokens_to_add)

    # 5. Make the decision
    if tokens >= 1:
        # ALLOWED: Subtract 1 token and update Redis
        tokens -= 1
        await redis_client.hset(redis_key, mapping={
            "tokens": tokens,
            "last_refill": now
        })
        # Set an expiration so Redis doesn't fill up with old data forever
        await redis_client.expire(redis_key, int(window_seconds) * 2)
        
        return {
            "allowed": True,
            "remainingRequests": int(tokens),
            "resetTime": "Calculating..." # We will format this properly later
        }
    else:
        # BLOCKED: Bucket is empty
        # Calculate how many seconds until 1 full token regenerates
        retry_after = math.ceil((1 - tokens) / (max_requests / window_seconds))
        
        return {
            "allowed": False,
            "retryAfter": retry_after,
            "resetTime": "Calculating..."
        }