<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-purple?style=flat-square)](LICENSE.md)
[![maintained](https://img.shields.io/badge/maintained%3F-yes-green?style=flat-square)](https://github.com/Mukller/tt-saver)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

---

## Language / Язык

</div>

| **📖 English** | **📖 Русский** |
|:---:|:---:|
| Scroll down / Листай вниз | Листай вниз / Scroll down |

---

## English Version




# TikTok Telegram Bot

A Telegram bot for downloading TikTok videos directly to your messenger.

## Features

- 📥 Download TikTok videos by link
- ⚡ Fast processing with yt-dlp
- 🤖 Asynchronous handling of multiple requests
- 🔧 Simple configuration via .env
- 📦 Docker support
- 🚀 Auto-start with systemd

## Requirements

- Python 3.10+
- pip (Python package manager)
- Telegram Bot Token (get from @BotFather)

## Installation

### Local Setup

1. Clone the repository:


2. Create a virtual environment:


3. Install dependencies:


4. Create .env file:


5. Run the bot:


### Docker



## Usage

1. Find the bot in Telegram
2. Send a TikTok video link
3. Bot downloads and sends the video

Supported formats:
- Direct video links
- Short TikTok URLs
- vm.tiktok.com links

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| BOT_TOKEN | Telegram bot token | ✓ |
| LOG_LEVEL | Log level (DEBUG/INFO/WARNING) | ✗ |
| REDIS_URL | Redis URL (if used) | ✗ |

## Project Structure



## Development

Want to contribute? See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

This project is licensed under the [MIT License](LICENSE.md)

## Support

- GitHub Issues for bugs and features
- Telegram for quick communication

## Acknowledgments

- [aiogram](https://github.com/aiogram/aiogram) - Telegram Bot API for Python
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloader

---

## Русская версия




# TikTok Telegram Bot

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-purple?style=flat-square)](LICENSE.md)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![maintained](https://img.shields.io/badge/maintained%3F-yes-green?style=flat-square)](https://github.com/Mukller/tt-saver)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

[English](README_EN.md) • Русский

</div>

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