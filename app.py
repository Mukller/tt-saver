import asyncio
import logging
import re
import os
import shutil
import subprocess
import uuid
import requests

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    FSInputFile,
    InputMediaPhoto
)

from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from dotenv import load_dotenv

import yt_dlp

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()

TEMP_DIR = "./temp"

TIKTOK_REGEX = r'(https?://[^\s]*tiktok\.com/[^\s]+)'


# =====================================================
# HELPERS
# =====================================================

def create_folder():

    request_id = str(uuid.uuid4())

    folder = os.path.join(
        TEMP_DIR,
        request_id
    )

    os.makedirs(folder, exist_ok=True)

    return request_id, folder


# =====================================================
# VIDEO DOWNLOADER
# =====================================================

def _download_video_sync(url, folder):
    """Синхронная загрузка видео (без блокировки event loop)"""
    output_template = os.path.join(folder, "video.%(ext)s")
    
    ydl_opts = {
        "outtmpl": output_template,
        "format": "best[ext=mp4]/mp4[height<=1080]/mp4",
        "concurrent_fragment_downloads": 4,
        "quiet": True,
        "noplaylist": True,
        "merge_output_format": "mp4",
        "socket_timeout": 30,
        "http_chunk_size": 10485760,
        "retries": 3,
        "fragment_retries": 3,
        "skip_unavailable_fragments": True,
        "extractor_args": {
            "tiktok": {
                "api_hostname": "api.tiktok.com"
            }
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info)
    return video_path

async def download_video(url, folder):
    """Асинхронная обертка - не блокирует event loop"""
    return await asyncio.to_thread(_download_video_sync, url, folder)


# =====================================================
# AUDIO EXTRACTION
# =====================================================

async def extract_audio(video_path, folder):

    audio_path = os.path.join(
        folder,
        "audio.mp3"
    )

    command = [
        "ffmpeg",
        "-i",
        video_path,
        "-q:a",
        "0",
        "-map",
        "a",
        audio_path,
        "-y"
    ]

    await asyncio.to_thread(
        subprocess.run,
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if os.path.exists(audio_path):
        return audio_path

    return None


# =====================================================
# PHOTO DOWNLOADER
# =====================================================

def _fetch_photo_data_sync(url):
    """Fetch photo post data via tikwm.com API (blocking)."""
    api_url = "https://www.tikwm.com/api/"
    r = requests.post(
        api_url,
        data={"url": url, "hd": "1"},
        timeout=15,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    return r.json()


def _download_file_sync(url, dest_path):
    """Download a single file (blocking)."""
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"}, stream=True)
    r.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
    return dest_path


async def download_photos(url, folder):
    """Download photos from TikTok using tikwm.com API."""
    photos = []
    audio_path = None

    try:
        data = await asyncio.to_thread(_fetch_photo_data_sync, url)
    except Exception as e:
        print(f"Error fetching photo data: {e}")
        return photos, audio_path

    if data.get("code") != 0:
        print(f"tikwm API error: {data.get("msg")}")
        return photos, audio_path

    item = data.get("data", {})
    image_urls = item.get("images", []) or []
    music_url = item.get("music")

    # Download photos in parallel
    download_tasks = []
    for i, img_url in enumerate(image_urls, start=1):
        photo_path = os.path.join(folder, f"photo_{i:03d}.jpg")
        download_tasks.append(asyncio.to_thread(_download_file_sync, img_url, photo_path))

    if download_tasks:
        results = await asyncio.gather(*download_tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, str) and os.path.exists(res):
                photos.append(res)

    # Download audio
    if music_url:
        audio_path_candidate = os.path.join(folder, "audio.mp3")
        try:
            await asyncio.to_thread(_download_file_sync, music_url, audio_path_candidate)
            if os.path.exists(audio_path_candidate):
                audio_path = audio_path_candidate
        except Exception as e:
            print(f"Error downloading audio: {e}")

    photos.sort()
    return photos, audio_path

# =====================================================
# SLIDESHOW CREATOR
# =====================================================

async def create_slideshow(
    photos,
    folder,
    audio_path=None
):
    if not photos:
        return None

    # Duration rules: 1 photo -> 15s, multiple -> 5s each
    if len(photos) == 1:
        per_photo = 15.0
    else:
        per_photo = 5.0

    total_duration = per_photo * len(photos)

    slideshow_path = os.path.join(folder, "slideshow.mp4")
    has_audio = audio_path and os.path.exists(audio_path)

    # ----- Single photo: loop with -t -----
    if len(photos) == 1:
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", photos[0]]
        if has_audio:
            cmd += ["-stream_loop", "-1", "-i", audio_path]
        cmd += [
            "-t", str(total_duration),
            "-vf", "fps=25,format=yuv420p,scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
        ]
        if has_audio:
            cmd += ["-c:a", "aac", "-shortest"]
        cmd.append(slideshow_path)

    # ----- Multiple photos: concat demuxer -----
    else:
        list_file = os.path.join(folder, "slides.txt")
        with open(list_file, "w") as f:
            for photo in photos:
                f.write(f"file '{photo}'\n")
                f.write(f"duration {per_photo}\n")
            # ffmpeg concat: last duration is ignored, so repeat last file
            f.write(f"file '{photos[-1]}'\n")

        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file]
        if has_audio:
            cmd += ["-stream_loop", "-1", "-i", audio_path]
        cmd += [
            "-t", str(total_duration),
            "-vf", "fps=25,format=yuv420p,scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
        ]
        if has_audio:
            cmd += ["-c:a", "aac", "-shortest"]
        cmd.append(slideshow_path)

    await asyncio.to_thread(
        subprocess.run,
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if os.path.exists(slideshow_path):
        return slideshow_path

    return None

# =====================================================
# MESSAGE HANDLER
# =====================================================

@dp.message(F.text)
async def handle_message(message: Message):
    text = message.text
    if not text:
        return

    matches = re.findall(TIKTOK_REGEX, text)
    if not matches:
        return

    # Spawn background task so dispatcher can process other messages immediately
    asyncio.create_task(process_tiktok(message, matches[0]))


async def process_tiktok(message: Message, original_url: str):
    try:
        status_message = await message.reply("📥 Скачиваю TikTok...")
    except Exception as reply_error:
        print(f"Reply failed: {reply_error}")
        try:
            status_message = await message.answer("📥 Скачиваю TikTok...")
        except Exception as e:
            print(f"Answer also failed: {e}")
            return

    request_id, folder = create_folder()

    try:

        # ============================================
        # EXPAND SHORT URL
        # ============================================

        response = await asyncio.to_thread(requests.get, original_url, allow_redirects=True, timeout=15, headers={"User-Agent": "Mozilla/5.0"})

        final_url = response.url

        print("FINAL URL:", final_url)

        # ============================================
        # PHOTO POSTS
        # ============================================

        if "/photo/" in final_url:

            photos, audio_path = await download_photos(
                final_url,
                folder
            )

            if not photos:

                await status_message.edit_text(
                    "❌ Не удалось скачать фото"
                )

                return

            media = []

            for photo_path in photos[:10]:

                media.append(
                    InputMediaPhoto(
                        media=FSInputFile(photo_path)
                    )
                )

            await message.answer_media_group(
                media
            )

            slideshow = await create_slideshow(
                photos,
                folder,
                audio_path
            )

            if slideshow:

                video = FSInputFile(
                    slideshow
                )

                await message.answer_video(
                    video,
                    caption="🎞 Slideshow"
                )

            if audio_path:

                audio = FSInputFile(
                    audio_path
                )

                await message.answer_audio(
                    audio,
                    caption="🎵 Аудио"
                )

        # ============================================
        # VIDEO POSTS
        # ============================================

        else:

            video_path = await download_video(
                final_url,
                folder
            )

            if not os.path.exists(video_path):

                await status_message.edit_text(
                    "❌ Видео не скачалось"
                )

                return

            video = FSInputFile(
                video_path
            )

            await message.answer_video(
                video,
                caption="✨ Видео"
            )

            audio_path = await extract_audio(
                video_path,
                folder
            )

            if audio_path:

                audio = FSInputFile(
                    audio_path
                )

                await message.answer_audio(
                    audio,
                    caption="🎵 Аудио"
                )

        shutil.rmtree(
            folder,
            ignore_errors=True
        )

        await status_message.delete()

    except Exception as e:

        print(e)

        shutil.rmtree(
            folder,
            ignore_errors=True
        )

        await status_message.edit_text(
            f"❌ Ошибка:\n{str(e)}"
        )


# =====================================================
# MAIN
# =====================================================

async def main():

    print("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
