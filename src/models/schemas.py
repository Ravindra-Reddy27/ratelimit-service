from pydantic import BaseModel

# Schema for POST /api/v1/clients
class ClientRegisterRequest(BaseModel):
    clientId: str
    apiKey: str
    maxRequests: int
    windowSeconds: int

# Schema for POST /api/v1/ratelimit/check
class RateLimitCheckRequest(BaseModel):
    clientId: str
    path: str