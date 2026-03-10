from fastapi import APIRouter, Response, HTTPException, status
from src.models.schemas import ClientRegisterRequest, RateLimitCheckRequest
from src.config.db import clients_collection
from src.services.rate_limiter import check_limit
import hashlib
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/api/v1")

@router.post("/clients", status_code=status.HTTP_201_CREATED)
async def register_client(request: ClientRegisterRequest):
    # 1. Check if client or apiKey already exists (Requirement: HTTP 409)
    existing_client = await clients_collection.find_one({
        "$or": [{"clientId": request.clientId}, {"apiKey": request.apiKey}]
    })
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="clientId or apiKey already exists"
        )
    
    # 2. Hash the API Key for security (Requirement: Secure Storage)
    hashed_key = hashlib.sha256(request.apiKey.encode()).hexdigest()
    
    # 3. Save the new client to MongoDB
    new_client = {
        "clientId": request.clientId,
        "hashedApiKey": hashed_key,
        "maxRequests": request.maxRequests,
        "windowSeconds": request.windowSeconds,
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc)
    }
    await clients_collection.insert_one(new_client)
    
    # 4. Return success response (excluding the hashed key!)
    return {
        "clientId": request.clientId,
        "maxRequests": request.maxRequests,
        "windowSeconds": request.windowSeconds
    }

@router.post("/ratelimit/check")
async def check_rate_limit(request: RateLimitCheckRequest, response: Response):
    # 1. Ask the Brain (Token Bucket Algorithm) if the request is allowed
    result = await check_limit(request.clientId, request.path)
    
    # 2. Calculate the ISO 8601 reset time string
    retry_seconds = result.get("retryAfter", 0)
    reset_time = (datetime.now(timezone.utc) + timedelta(seconds=retry_seconds)).isoformat()
    
    # 3. Handle the "Too Many Requests" scenario (Requirement: HTTP 429)
    if not result["allowed"]:
        response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
        return {
            "allowed": False,
            "retryAfter": result["retryAfter"],
            "resetTime": reset_time
        }
        
    # 4. Handle the "Allowed" scenario (Requirement: HTTP 200)
    return {
        "allowed": True,
        "remainingRequests": result["remainingRequests"],
        "resetTime": reset_time
    }