from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from src.infrastructure.database import init_db
from src.infrastructure import models  # noqa: F401
from src.infrastructure.events import consume_appointment_completed
from src.presentation.routers import router
from prometheus_fastapi_instrumentator import Instrumentator

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    asyncio.create_task(consume_appointment_completed())
    yield

app = FastAPI(title="Billing Service", version="0.1.0", lifespan=lifespan)
app.include_router(router)

Instrumentator().instrument(app).expose(app)

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "service": "billing"}
