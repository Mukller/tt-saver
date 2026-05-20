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

async def download_photos(url, folder):
    """Download photos from TikTok using yt-dlp."""
    output_template = os.path.join(folder, "photo_%(autonumber)d.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        "format": "best[ext=mp4]/mp4[height<=1080]/mp4",
        "concurrent_fragment_downloads": 4,
        "quiet": False,
        "noplaylist": True,
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

    photos = []
    audio_path = None

    def _do_download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=True)

    try:
        info = await asyncio.to_thread(_do_download)
    except Exception as e:
        print(f"Error downloading photos with yt-dlp: {e}")
        return photos, audio_path

    # ищем скачанные файлы
    for root, dirs, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(root, file)
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".mp4")):
                if file.lower().endswith(".mp4"):
                    # это может быть видео или фото в mp4 формате
                    photos.append(full_path)
                else:
                    photos.append(full_path)
            elif file.lower().endswith(".mp3"):
                audio_path = full_path

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

    list_file = os.path.join(
        folder,
        "slides.txt"
    )

    with open(list_file, "w") as f:

        for photo in photos:

            f.write(
                f"file '{photo}'\n"
            )

            f.write(
                "duration 2\n"
            )

    slideshow_path = os.path.join(
        folder,
        "slideshow.mp4"
    )

    # =========================================
    # WITH AUDIO
    # =========================================

    if audio_path and os.path.exists(audio_path):

        command = [

            "ffmpeg",

            "-f",
            "concat",

            "-safe",
            "0",

            "-i",
            list_file,

            "-i",
            audio_path,

            "-vf",
            "fps=25,format=yuv420p",

            "-shortest",

            "-pix_fmt",
            "yuv420p",

            "-c:v",
            "libx264",

            "-c:a",
            "aac",

            slideshow_path,

            "-y"
        ]

    # =========================================
    # WITHOUT AUDIO
    # =========================================

    else:

        command = [

            "ffmpeg",

            "-f",
            "concat",

            "-safe",
            "0",

            "-i",
            list_file,

            "-vf",
            "fps=25,format=yuv420p",

            "-pix_fmt",
            "yuv420p",

            slideshow_path,

            "-y"
        ]

    await asyncio.to_thread(
        subprocess.run,
        command,
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

    matches = re.findall(
        TIKTOK_REGEX,
        text
    )

    if not matches:
        return

    original_url = matches[0]

    try:
        status_message = await message.reply(
            "📥 Скачиваю TikTok..."
        ,
            request_timeout=15
        )
    except Exception as reply_error:
        print(f"Reply failed: {reply_error}")
        status_message = await message.answer(
            "📥 Скачиваю TikTok..."
        ,
            request_timeout=15
        )

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
