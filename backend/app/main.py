from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import verify_api_key
from app.api.routes import health, pages, posts, schedule, images
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: placeholder for MinIO bucket ensure + DB check
    yield
    # Shutdown: cleanup


app = FastAPI(
    title="Facebook Auto-Poster",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
settings = get_settings()
cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public routes (no auth)
app.include_router(health.router, prefix="/api")

# Protected routes
app.include_router(pages.router, prefix="/api", dependencies=[Depends(verify_api_key)])
app.include_router(posts.router, prefix="/api", dependencies=[Depends(verify_api_key)])
app.include_router(schedule.router, prefix="/api", dependencies=[Depends(verify_api_key)])
app.include_router(images.router, prefix="/api", dependencies=[Depends(verify_api_key)])
