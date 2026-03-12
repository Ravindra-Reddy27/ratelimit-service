import os
from pydantic import BaseModel, Field
from typing import Optional

# 1. Pull the default values from the environment variables.
# If they aren't set in the .env file, we fallback to 100 and 60.
DEFAULT_MAX = int(os.getenv("DEFAULT_RATE_LIMIT_MAX_REQUESTS", 100))
DEFAULT_WINDOW = int(os.getenv("DEFAULT_RATE_LIMIT_WINDOW_SECONDS", 60))

class ClientRegisterRequest(BaseModel):
    clientId: str
    apiKey: str
    
    # 2. Make these fields Optional, and set their default values to the environment variables!
    maxRequests: Optional[int] = Field(
        default=DEFAULT_MAX, 
        gt=0, 
        description="Must be at least 1"
    )
    windowSeconds: Optional[int] = Field(
        default=DEFAULT_WINDOW, 
        gt=0, 
        description="Must be at least 1 second"
    )

class RateLimitCheckRequest(BaseModel):
    clientId: str
    path: str