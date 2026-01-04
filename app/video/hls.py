import os, subprocess, logging

logger = logging.getLogger(__name__)

FFMPEG_PATH = "ffmpeg"
TEMP_VIDEO_DIR = "tmp_videos"
TEMP_HLS_DIR = "tmp_hls"

os.makedirs(TEMP_VIDEO_DIR, exist_ok=True)
os.makedirs(TEMP_HLS_DIR, exist_ok=True)

def process_video_to_hls(file, movie_id):
    logger.info("Преобразование файла фильма в HLS", extra={"movie_id": movie_id})
    
    video_path = f"{TEMP_VIDEO_DIR}/{movie_id}.mp4"
    hls_dir = f"{TEMP_HLS_DIR}/{movie_id}"
    os.makedirs(hls_dir, exist_ok=True)

    with open(video_path, "wb") as f:
        f.write(file.file.read())

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
        f"{hls_dir}/index.m3u8"
    ], check=True)

    os.remove(video_path)
    return hls_dir
