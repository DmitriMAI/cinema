import os, boto3, logging

logger = logging.getLogger(__name__)

S3_ENDPOINT = os.getenv("S3_ENDPOINT")
PUBLIC_S3_ENDPOINT = os.getenv("S3_PUBLIC_ENDPOINT")
S3_BUCKET = os.getenv("S3_BUCKET")

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
)

def upload_hls_to_s3(hls_output_dir, movie_id):
    logger.info("Загрузка в S3 HLS файлов фильма", extra={"movie_id": movie_id})
    for filename in os.listdir(hls_output_dir):
        local_path = os.path.join(hls_output_dir, filename)
        content_type = (
            "application/vnd.apple.mpegurl"
            if filename.endswith(".m3u8")
            else "video/MP2T"
        )
        
        try:
            s3.upload_file(
                local_path,
                S3_BUCKET,
                f"{movie_id}/{filename}",
                ExtraArgs={"ContentType": content_type}
            )
            logger.info("Загружен HLS файл фильма в S3", extra={"movie_id": movie_id, "filename": filename})
        except Exception:
            logger.error("Ошибка загрузки HLS файла фильма в S3", extra={"movie_id": movie_id, "filename": filename}, exc_info=True)
            raise

def build_hls_url(movie_id):
    return f"{PUBLIC_S3_ENDPOINT}/{S3_BUCKET}/{movie_id}/index.m3u8"
