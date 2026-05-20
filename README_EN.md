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
