<div align="center">

**English** • [Русский](README.md)

</div>

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
