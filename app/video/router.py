from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.video.hls import process_video_to_hls
from app.video.s3 import upload_hls_to_s3, build_hls_url
import uuid
import shutil

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/upload", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    movie_id = str(uuid.uuid4())
    hls_dir = process_video_to_hls(file, movie_id)
    upload_hls_to_s3(hls_dir, movie_id)
    shutil.rmtree(hls_dir)

    return {
        "message": "Video uploaded successfully",
        "hls_url": build_hls_url(movie_id),
        "movie_id": movie_id
    }

@router.get("/video/{movie_id}", response_class=HTMLResponse)
async def video_player(request: Request, movie_id: str):
    return templates.TemplateResponse(
        "video.html",
        {"request": request, "hls_path": build_hls_url(movie_id)}
    )
