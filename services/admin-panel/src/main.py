from fastapi import FastAPI
from src.presentation.routers import router
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI(title="Admin Panel", version="0.1.0")
app.include_router(router)

Instrumentator().instrument(app).expose(app)

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "service": "admin"}
