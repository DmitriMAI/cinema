from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import subprocess
import os
import uvicorn

app = FastAPI()

# Создаем директории для хранения файлов
VIDEO_DIR = "videos"
HLS_DIR = "hls"
FFMPEG_PATH = "ffmpeg"

os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(HLS_DIR, exist_ok=True)

# Монтируем статические директории
app.mount("/videos", StaticFiles(directory=VIDEO_DIR), name="videos")
app.mount("/hls", StaticFiles(directory=HLS_DIR), name="hls")

# Настраиваем шаблоны
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    video_files = [f for f in os.listdir(VIDEO_DIR)]
    return templates.TemplateResponse("index.html", {"request": request, "video_files": video_files})


@app.get("/upload", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    # Сохраняем загруженный файл
    video_path = os.path.join(VIDEO_DIR, file.filename)
    with open(video_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Конвертируем в HLS формат
    hls_filename = f"{os.path.splitext(file.filename)[0]}.m3u8"
    hls_path = os.path.join(HLS_DIR, hls_filename)
    
    subprocess.run([
        FFMPEG_PATH,
        "-i", video_path,
        "-hls_time", "10",
        "-hls_list_size", "0",
        "-c:v", "h264",
        "-flags", "+cgop",
        "-g", "30",
        "-sc_threshold", "0",
        "-f", "hls",
        hls_path
    ])

    return "Video uploaded and segmented successfully"


@app.get("/video/{filename}", response_class=HTMLResponse)
async def video_player(request: Request, filename: str):
    video_path = os.path.join(VIDEO_DIR, filename)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    hls_path = f"/hls/{os.path.splitext(filename)[0]}.m3u8"
    return templates.TemplateResponse("video.html", {
        "request": request,
        "hls_path": hls_path
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)