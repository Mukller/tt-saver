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