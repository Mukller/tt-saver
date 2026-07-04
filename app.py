import asyncio
import json
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
    InputMediaPhoto,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery
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
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "audio_video": True,
    "audio_photos": True,
}


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                return {**DEFAULT_SETTINGS, **data}
        except Exception as e:
            print(f"Failed to load settings: {e}")
    return DEFAULT_SETTINGS.copy()


def save_settings(s):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(s, f)
    except Exception as e:
        print(f"Failed to save settings: {e}")


SETTINGS = load_settings()


def settings_keyboard():
    av = "✅" if SETTINGS.get("audio_video") else "❌"
    ap = "✅" if SETTINGS.get("audio_photos") else "❌"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🎬 Аудио для видео: {av}", callback_data="toggle_audio_video")],
        [InlineKeyboardButton(text=f"🖼 Аудио для фото: {ap}", callback_data="toggle_audio_photos")],
    ])


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

    cookies_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")

    ydl_opts = {
        "outtmpl": output_template,
        "format": "best[ext=mp4]/mp4[height<=1080]/mp4",
        "concurrent_fragment_downloads": 8,
        "buffersize": 1048576,
        "quiet": True,
        "noplaylist": True,
        "merge_output_format": "mp4",
        "socket_timeout": 20,
        "http_chunk_size": 10485760,
        "retries": 3,
        "fragment_retries": 3,
        "skip_unavailable_fragments": True,
        "extractor_args": {
            "tiktok": {
                "api_hostname": "api16-normal-c-useast1a.tiktokv.com"
            }
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        }
    }

    if os.path.exists(cookies_file):
        ydl_opts["cookiefile"] = cookies_file

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
        for chunk in r.iter_content(chunk_size=1048576):
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
        print(f"tikwm API error: {data.get('msg')}")
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


async def _photos_from_item(item, folder):
    """Скачать фото/аудио из уже полученного tikwm item (без повторного API-запроса)."""
    photos = []
    audio_path = None
    image_urls = item.get("images", []) or []
    music_url = item.get("music")

    download_tasks = []
    for i, img_url in enumerate(image_urls, start=1):
        photo_path = os.path.join(folder, f"photo_{i:03d}.jpg")
        download_tasks.append(asyncio.to_thread(_download_file_sync, img_url, photo_path))

    if download_tasks:
        results = await asyncio.gather(*download_tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, str) and os.path.exists(res):
                photos.append(res)

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

@dp.message(F.text, F.text.startswith("/settings"))
async def cmd_settings(message: Message):
    if message.chat.type != "private":
        await message.reply("⚙️ Настройки доступны только в личных сообщениях.")
        return
    await message.answer(
        "⚙️ <b>Общие настройки</b> (для всех пользователей):\nНажми кнопку, чтобы переключить.",
        reply_markup=settings_keyboard()
    )


@dp.callback_query(F.data.in_({"toggle_audio_video", "toggle_audio_photos"}))
async def cb_toggle(query: CallbackQuery):
    key = "audio_video" if query.data == "toggle_audio_video" else "audio_photos"
    SETTINGS[key] = not SETTINGS.get(key, True)
    save_settings(SETTINGS)
    try:
        await query.message.edit_reply_markup(reply_markup=settings_keyboard())
    except Exception as e:
        print(f"edit_reply_markup failed: {e}")
    state = "включено" if SETTINGS[key] else "выключено"
    label = "Аудио для видео" if key == "audio_video" else "Аудио для фото"
    await query.answer(f"{label}: {state}")


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
        # ОПРЕДЕЛЯЕМ ТИП (один API-запрос вместо двух)
        # ============================================

        tikwm_data = await asyncio.to_thread(_fetch_photo_data_sync, original_url)
        item = tikwm_data.get("data", {}) if tikwm_data.get("code") == 0 else {}
        is_photo = bool(item.get("images"))

        # ============================================
        # PHOTO POSTS
        # ============================================

        if is_photo:

            photos, audio_path = await _photos_from_item(
                item,
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

            # Слайдшоу создаём в фоне пока Telegram принимает фото
            slideshow_task = asyncio.create_task(
                create_slideshow(photos, folder, audio_path)
            )

            await message.answer_media_group(
                media
            )

            slideshow = await slideshow_task

            if slideshow:

                video = FSInputFile(
                    slideshow
                )

                await message.answer_video(
                    video,
                    caption="🎞 Slideshow"
                )

            if audio_path and SETTINGS.get("audio_photos", True):

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

            # Быстрый путь: видео + аудио с tikwm CDN параллельно, без ffmpeg
            play_url = item.get("hdplay") or item.get("play")
            music_url = item.get("music") if SETTINGS.get("audio_video", True) else None
            video_path = os.path.join(folder, "video.mp4")
            audio_path = None
            used_ytdlp = False

            if play_url:
                try:
                    music_dest = os.path.join(folder, "audio.mp3")
                    dl_tasks = [asyncio.to_thread(_download_file_sync, play_url, video_path)]
                    if music_url:
                        dl_tasks.append(asyncio.to_thread(_download_file_sync, music_url, music_dest))
                    results = await asyncio.gather(*dl_tasks, return_exceptions=True)
                    if isinstance(results[0], Exception):
                        raise results[0]
                    if music_url and not isinstance(results[1], Exception) and os.path.exists(music_dest):
                        audio_path = music_dest
                except Exception as e:
                    print(f"tikwm CDN failed: {e}, fallback to yt-dlp")
                    play_url = None

            if not play_url or not os.path.exists(video_path):
                # Fallback: yt-dlp + ffmpeg аудио
                used_ytdlp = True
                video_path = await download_video(original_url, folder)

            if not os.path.exists(video_path):

                await status_message.edit_text(
                    "❌ Видео не скачалось"
                )

                return

            # Для yt-dlp пути — ffmpeg аудио параллельно с отправкой в Telegram
            audio_task = (
                asyncio.create_task(extract_audio(video_path, folder))
                if used_ytdlp and SETTINGS.get("audio_video", True) else None
            )

            video = FSInputFile(
                video_path
            )

            await message.answer_video(
                video,
                caption="✨ Видео"
            )

            if SETTINGS.get("audio_video", True):
                final_audio = audio_path  # tikwm CDN (уже готов)
                if audio_task:
                    final_audio = await audio_task  # yt-dlp + ffmpeg
                if final_audio and os.path.exists(final_audio):
                    audio = FSInputFile(
                        final_audio
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

        err = str(e)
        if 'permission' in err.lower() or 'not have permission' in err.lower():
            text = '❌ Видео ограничено — требуется вход в TikTok. Попробуй другое видео.'
        elif 'not available' in err.lower() or 'removed' in err.lower():
            text = '❌ Видео удалено или недоступно в твоём регионе.'
        elif 'Unable to download' in err or 'HTTP Error' in err:
            text = '❌ Ошибка сети при скачивании. Попробуй ещё раз.'
        else:
            text = '❌ Ошибка:' + chr(10) + err[:300]
        await status_message.edit_text(text)


# =====================================================
# MAIN
# =====================================================

async def main():

    print("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
