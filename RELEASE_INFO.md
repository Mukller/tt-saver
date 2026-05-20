# TT Saver Release Information

## Version 1.0.0
**Release Date:** May 20, 2026

### Overview
First stable release of TT Saver - a Telegram bot for downloading TikTok videos.

### Features
- Download TikTok videos using yt-dlp backend
- Support for video links and direct sharing via Telegram
- Cookie-based authentication for restricted content
- Telegram WebApp integration for seamless user experience
- Redis-based caching for improved performance
- Support for multiple video formats and qualities

### Requirements
- Python 3.8 or higher
- Redis server
- FFmpeg (for video processing)
- yt-dlp (dependency for video downloading)

### Installation
```bash
pip install -r requirements.txt
```

### Configuration
Set the following environment variables:
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `REDIS_URL`: Redis connection URL (default: redis://localhost:6379)

### Usage
1. Start the bot: `python -m backend.app.bot.bot`
2. Send a TikTok video link to the bot
3. The bot will download and send the video to you

### Known Issues
- Some restricted TikTok videos may require cookies from a browser with a valid session
- Video download speed depends on the source TikTok server and internet connection

### Fixed Issues from Previous Versions
- Improved TikTok authentication using --cookies-from-browser flag
- Enhanced error handling for invalid video links
- Better memory management for concurrent downloads

### Documentation
For more information, see:
- [README.md](README.md) - Russian language documentation
- [README_EN.md](README_EN.md) - English language documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) - Community standards
- [LICENSE.md](LICENSE.md) - MIT License

### Future Plans
- Playlist support
- Better video quality options
- Batch download functionality
- Advanced analytics and statistics

### Support
For issues and feature requests, please open an issue on GitHub.
