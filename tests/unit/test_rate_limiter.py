import pytest
import time
from unittest.mock import AsyncMock, patch
from src.services.rate_limiter import check_limit

pytestmark = pytest.mark.asyncio

@patch("src.services.rate_limiter.clients_collection")
@patch("src.services.rate_limiter.redis_client")
async def test_client_not_found(mock_redis, mock_mongo):
    """Test that an unknown client is immediately blocked"""
    mock_mongo.find_one = AsyncMock(return_value=None)
    
    result = await check_limit("unknown-client", "/api/test")
    
    assert result["allowed"] == False
    assert result["retryAfter"] == 60

@patch("src.services.rate_limiter.clients_collection")
@patch("src.services.rate_limiter.redis_client")
async def test_token_bucket_allowed(mock_redis, mock_mongo):
    """Test that a client with a full bucket is allowed"""
    mock_mongo.find_one = AsyncMock(return_value={
        "clientId": "test-client",
        "maxRequests": 5,
        "windowSeconds": 60
    })
    
    current_time = str(time.time()).encode()
    mock_redis.hmget = AsyncMock(return_value=[b"5", current_time])
    
    result = await check_limit("test-client", "/api/test")
    
    assert result["allowed"] == True
    assert result["remainingRequests"] == 4