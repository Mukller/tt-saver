<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-purple?style=flat-square)](LICENSE.md)
[![maintained](https://img.shields.io/badge/maintained%3F-yes-green?style=flat-square)](https://github.com/Mukller/tt-saver)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

### 🌐 Язык / Language

**Нажми, чтобы развернуть нужный язык · Click to expand your language**

</div>

<details open>
<summary><b>🇬🇧 English</b></summary>

<br>

# TikTok Telegram Bot

A Telegram bot for downloading TikTok videos straight into the messenger.

## Features

- 📥 Download TikTok videos by link
- ⚡ Fast processing via yt-dlp
- 🤖 Asynchronous handling of many requests
- 🔧 Simple configuration via .env
- 📦 Docker support
- 🚀 Automatic startup via systemd

## Requirements

- Python 3.10+
- pip (Python package manager)
- Telegram Bot Token (get one from @BotFather)

## Installation

### Locally

1. Clone the repository:


2. Create a virtual environment:


3. Install dependencies:


4. Create a .env file:


5. Run the bot:


### Docker



## Usage

1. Find the bot in Telegram by its name
2. Send a TikTok video link
3. The bot downloads and sends the video back

Supported formats:
- Direct video links
- Short TikTok links
- Links via vm.tiktok.com

## Configuration

### Environment variables

| Variable | Description | Required |
|-----------|---------|-----------|
| BOT_TOKEN | Telegram bot token | ✓ |
| LOG_LEVEL | Logging level (DEBUG/INFO/WARNING) | ✗ |
| REDIS_URL | Redis URL (if used) | ✗ |

## Project structure



## Development

Want to help? See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

This project is distributed under the [MIT](LICENSE.md) license.

## Contacts

- GitHub Issues for bugs and suggestions
- Telegram for quick communication

## Acknowledgements

- [aiogram](https://github.com/aiogram/aiogram) - Telegram Bot API for Python
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloader

</details>

<details>
<summary><b>🇷🇺 Русский</b></summary>

<br>

# TikTok Telegram Bot

Telegram бот для скачивания видео с TikTok прямо в мессенджер.

## Возможности

- 📥 Скачивание видео с TikTok по ссылке
- ⚡ Быстрая обработка через yt-dlp
- 🤖 Асинхронная обработка множества запросов
- 🔧 Простая конфигурация через .env
- 📦 Docker поддержка
- 🚀 Автоматический запуск через systemd

## Требования

- Python 3.10+
- pip (Python package manager)
- Telegram Bot Token (получить от @BotFather)

## Установка

### Локально

1. Клонируйте репозиторий:


2. Создайте виртуальное окружение:


3. Установите зависимости:


4. Создайте файл .env:


5. Запустите бота:


### Docker



## Использование

1. Найдите бота в Telegram по имени
2. Отправьте ссылку на видео TikTok
3. Бот скачает и отправит видео

Поддерживаемые форматы:
- Прямые ссылки на видео
- Короткие ссылки TikTok
- Ссылки через vm.tiktok.com

## Конфигурация

### Переменные окружения

| Переменная | Описание | Обязательно |
|-----------|---------|-----------|
| BOT_TOKEN | Токен Telegram бота | ✓ |
| LOG_LEVEL | Уровень логирования (DEBUG/INFO/WARNING) | ✗ |
| REDIS_URL | URL для Redis (если используется) | ✗ |

## Структура проекта



## Разработка

Хотите помочь? Смотрите [CONTRIBUTING.md](CONTRIBUTING.md)

## Лицензия

Проект распространяется под лицензией [MIT](LICENSE.md)

## Контакты

- GitHub Issues для багов и предложений
- Telegram для быстрой коммуникации

## Благодарности

- [aiogram](https://github.com/aiogram/aiogram) - Telegram Bot API для Python
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Загрузчик видео

</details>
