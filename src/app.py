from fastapi import FastAPI
from src.routes import api

app = FastAPI(title="Rate Limiting Microservice")

# Include our routes
app.include_router(api.router)

@app.get("/health")
async def health_check():
    # We will use this later for Docker's healthcheck!
    return {"status": "healthy"}