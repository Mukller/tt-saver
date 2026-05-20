# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-05-20

### Added
- Initial release of TikTok Telegram Bot
- Bot can download TikTok videos via Telegram
- Support for direct TikTok URLs
- Async processing with aiogram framework
- yt-dlp integration for reliable video downloading
- Systemd service for auto-start
- Docker support for easy deployment
- Environment-based configuration

### Features
- Download TikTok videos by sending URL to bot
- Automatic video conversion and compression
- Error handling and user-friendly messages
- Logging for debugging and monitoring
- Multi-threaded video processing

### Technical
- Built with Python 3.10+
- Uses aiogram 3.x for Telegram Bot API
- yt-dlp for video downloading
- Redis for potential caching (optional)
