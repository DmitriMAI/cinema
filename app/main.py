from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.search.router import router as search_router
from app.video.router import router as video_router

from app.logging.config import setup_logging
from app.logging.middleware import RequestIdMiddleware

setup_logging()

app = FastAPI(title="Movie Platform")

app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)
app.include_router(video_router)
