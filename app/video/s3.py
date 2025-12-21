import os, boto3

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
    for filename in os.listdir(hls_output_dir):
        local_path = os.path.join(hls_output_dir, filename)
        content_type = (
            "application/vnd.apple.mpegurl"
            if filename.endswith(".m3u8")
            else "video/MP2T"
        )

        s3.upload_file(
            local_path,
            S3_BUCKET,
            f"{movie_id}/{filename}",
            ExtraArgs={"ContentType": content_type}
        )

def build_hls_url(movie_id):
    return f"{PUBLIC_S3_ENDPOINT}/{S3_BUCKET}/{movie_id}/index.m3u8"
