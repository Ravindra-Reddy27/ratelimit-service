from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.routes import api
import uuid
import logging

# Set up basic structured logging (Fixing Gap 3!)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Rate Limiting Microservice")

# --- FIX 1: Override 422 errors to be 400 Bad Request ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "clientId or apiKey already exists.", "errors": exc.errors()},
    )

app.include_router(api.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# --- FIX 2: Structured Logging Middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Generate a unique ID for this specific request
    request_id = str(uuid.uuid4())
    
    logger.info(f"Incoming Request | ID: {request_id} | Method: {request.method} | Path: {request.url.path}")
    
    # Process the request
    response = await call_next(request)
    
    logger.info(f"Completed Request | ID: {request_id} | Status: {response.status_code}")
    
    # Send the ID back in the headers just in case the client needs it
    response.headers["X-Request-ID"] = request_id
    return response