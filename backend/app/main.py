"""FastAPI application entry point."""

import contextlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router
from app.core.config import settings
from app.graph.workflow import init_chat_graph, shutdown_chat_graph


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    """Open the checkpoint database on startup, close it on shutdown."""
    await init_chat_graph()
    yield
    await shutdown_chat_graph()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Allow the Next.js frontend (browser) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/")
def root_check()->dict:
    return {"success" : "ok"}
    

@app.get("/health")
def health_check() -> dict:
    """Liveness probe."""
    return {"status": "ok"}
