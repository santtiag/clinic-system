import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.infrastructure.database import init_db
from src.infrastructure import models  # noqa: F401 - registra tablas
from src.infrastructure.consumers import consume_doctor_events
from src.presentation.routers import router
from prometheus_fastapi_instrumentator import Instrumentator


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    consumer_task = asyncio.create_task(consume_doctor_events())
    yield
    consumer_task.cancel()

app = FastAPI(title="Scheduling Service", version="0.1.0", lifespan=lifespan)
app.include_router(router)

Instrumentator().instrument(app).expose(app)

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "service": "scheduling"}
