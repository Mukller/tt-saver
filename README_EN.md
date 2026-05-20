# TT Saver

Telegram bot for downloading TikTok videos

## Features

- Download TikTok videos by link
- Support for yt-dlp backend
- WebApp integration with Telegram
- Handle authentication restrictions with cookie-based access
- Video format support

## Requirements

- Python 3.8+
- pip or Poetry
- Redis (for caching)
         - FFmpeg (for video processing)

                   ## Installation

                   1. Clone the repository:
                   ```bash
                   git clone https://github.com/Mukller/tt-saver.git
                   cd tt-saver
                   ```

                   2. Install dependencies:
                   ```bash
                   pip install -r requirements.txt
                   ```

                   3. Configure environment variables:
                   ```bash
                   cp .env.example .env
                   # Edit .env with your configuration
                   ```

                   4. Run the bot:
                   ```bash
                   python -m backend.app.bot.bot
                   ```

                   ## Usage

                   1. Start the bot: `/start`
                   2. Send a TikTok video link
                   3. The bot will download and send you the video
                   4. For restricted videos, enable cookie-based authentication using the `/cookies` command

                   ## Architecture

                   - **Backend**: FastAPI for API endpoints
                   - **Bot**: Telegram bot with WebApp support
                   - **Download Engine**: yt-dlp for video downloads
                   - **Cache**: Redis for session management
                   - **Chess Engine**: Stockfish for game analysis

                   ## Configuration

                   Key environment variables:
                   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
                   - `REDIS_URL`: Redis connection URL
                   - `STOCKFISH_PATH`: Path to Stockfish executable

                   ## Contributing

                   See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

                   ## Code of Conduct

                   We are committed to providing a welcoming and inspiring community. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

                   ## License

                   MIT License - see [LICENSE](LICENSE) for details.

                   ## Author

                   Anton Petnitsky (@Mukller)
                   
