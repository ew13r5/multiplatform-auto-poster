import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.deps import verify_api_key
from app.api.routes import health, pages, posts, schedule, images, publish, analytics
from app.api.websocket import manager
from app.config import get_settings
from app.exceptions import PostNotEditableError, PageNotFoundError, InvalidFileError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


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

# Exception handlers
@app.exception_handler(PostNotEditableError)
async def post_not_editable_handler(request: Request, exc: PostNotEditableError):
    return JSONResponse(status_code=403, content={"error": "post_not_editable", "detail": str(exc)})


@app.exception_handler(PageNotFoundError)
async def page_not_found_handler(request: Request, exc: PageNotFoundError):
    return JSONResponse(status_code=404, content={"error": "page_not_found", "detail": str(exc)})


@app.exception_handler(InvalidFileError)
async def invalid_file_handler(request: Request, exc: InvalidFileError):
    return JSONResponse(status_code=400, content={"error": "invalid_file", "detail": str(exc)})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"error": "internal_error", "detail": "An unexpected error occurred"})


# Public routes (no auth)
app.include_router(health.router, prefix="/api")

# Protected routes
app.include_router(pages.router, prefix="/api", dependencies=[Depends(verify_api_key)])
app.include_router(posts.router, prefix="/api", dependencies=[Depends(verify_api_key)])
app.include_router(schedule.router, prefix="/api", dependencies=[Depends(verify_api_key)])
app.include_router(images.router, prefix="/api", dependencies=[Depends(verify_api_key)])
app.include_router(publish.router, prefix="/api", dependencies=[Depends(verify_api_key)])
app.include_router(analytics.router, prefix="/api", dependencies=[Depends(verify_api_key)])


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connected = await manager.connect(websocket)
    if not connected:
        return
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
