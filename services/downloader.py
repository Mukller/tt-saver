import yt_dlp
import uuid
import os
import subprocess
import requests
import shutil

TEMP_DIR = "./temp"

MAX_FILE_SIZE = 50 * 1024 * 1024


async def download_tiktok(url: str):

    request_id = str(uuid.uuid4())

    download_path = os.path.join(
        TEMP_DIR,
        request_id
    )

    os.makedirs(download_path, exist_ok=True)

    video_template = os.path.join(
        download_path,
        "video.%(ext)s"
    )

    ydl_opts = {

        "outtmpl": video_template,

        "format": (
            "bestvideo[filesize<50M]+bestaudio/"
            "best[filesize<50M]/best"
        ),

        "quiet": True,

        "noplaylist": True,

        "merge_output_format": "mp4",

        "socket_timeout": 30,

        "retries": 10,

        "fragment_retries": 10,

        "extractor_args": {
            "tiktok": {
                "api_hostname":
                "api16-normal-c-useast1a.tiktokv.com"
            }
        },

        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0"
            )
        }
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

    except Exception as e:

        shutil.rmtree(
            download_path,
            ignore_errors=True
        )

        raise Exception(
            f"Ошибка yt-dlp: {str(e)}"
        )

    files = []

    # -------------------
    # VIDEO FILES
    # -------------------

    for file in os.listdir(download_path):

        full_path = os.path.join(
            download_path,
            file
        )

        if not os.path.isfile(full_path):
            continue

        # file size limit
        if os.path.getsize(full_path) > MAX_FILE_SIZE:
            continue

        if file.endswith(".mp4"):

            files.append(full_path)

    # -------------------
    # AUDIO EXTRACTION
    # -------------------

    video_file = None

    for f in files:

        if f.endswith(".mp4"):
            video_file = f
            break

    if video_file:

        audio_path = os.path.join(
            download_path,
            "audio.mp3"
        )

        command = [
            "ffmpeg",
            "-i",
            video_file,
            "-q:a",
            "0",
            "-map",
            "a",
            audio_path,
            "-y"
        ]

        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if os.path.exists(audio_path):

            if os.path.getsize(
                audio_path
            ) < MAX_FILE_SIZE:

                files.append(audio_path)

    # -------------------
    # PHOTO SLIDESHOW
    # -------------------

    images = info.get(
        "thumbnails",
        []
    )

    image_index = 0

    for image in images:

        image_url = image.get("url")

        if not image_url:
            continue

        try:

            response = requests.get(
                image_url,
                timeout=15
            )

            if response.status_code != 200:
                continue

            image_path = os.path.join(
                download_path,
                f"photo_{image_index}.jpg"
            )

            with open(image_path, "wb") as f:
                f.write(response.content)

            if os.path.getsize(
                image_path
            ) < MAX_FILE_SIZE:

                files.append(image_path)

            image_index += 1

        except:
            pass

    return {
        "request_id": request_id,
        "files": files,
        "info": info,
    }
