"""
Ponto de entrada principal do serviço de benchmark
"""
import uvicorn
from fastapi import FastAPI
from benchmark_service.api.routes import router as api_router

app = FastAPI(
    title="AI Benchmark Service",
    description="Serviço para avaliação de agents de IA",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check():
    return {"status": "ready"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
