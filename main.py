# 🚀 Main Application Entry Point

"""
Main application entry point for AI Benchmark Service
"""

import uvicorn
from fastapi import FastAPI
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from benchmark_service.api.routes import router as api_router

app = FastAPI(
    title="AI Benchmark Service",
    description="Service for evaluating AI agents performance",
    version="1.2.0",
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {"status": "ready"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
