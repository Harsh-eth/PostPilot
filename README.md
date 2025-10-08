# PostPilot v1.0.0

AI-powered X/Twitter post summarization and reply suggestions Chrome extension.

## Features

- **Smart Summarization**: Break down long posts into digestible takeaways
- **Context Generation**: Provide background insights for better understanding  
- **Reply Suggestions**: Generate engaging responses with different personas
- **Clean UI**: Minimal, non-intrusive interface that integrates seamlessly with X/Twitter
- **Multiple Personas**: Human, Hardcore, and Curator response styles

## Installation

### Backend Setup

1. Navigate to the server directory:
```bash
cd server
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install fastapi uvicorn pydantic pydantic-settings structlog aiohttp langdetect redis python-multipart
```

4. Configure environment:
```bash
cp env.example .env
# Edit .env with your API keys
```

5. Start the server:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8787 --reload
```

### Extension Setup

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `extension` folder
4. The PostPilot extension will be installed and ready to use

## Usage

1. Navigate to any X/Twitter post
2. Look for the "PP" button next to the like/retweet buttons
3. Click the button to open PostPilot panel
4. Choose from Summary, Context, or Replies
5. For Replies, select your preferred persona
6. Copy the generated content and use it as needed

## Configuration

### Backend Configuration

1. **Environment Variables** (`server/.env`):
```bash
# Copy example file
cp server/env.example server/.env

# Edit with your settings
nano server/.env
```

Key settings:
- `FIREWORKS_API_KEY`: Your Fireworks API key
- `BACKEND_PORT`: Server port (default: 8787)
- `RATE_LIMIT_REQUESTS`: Rate limiting settings
- `DEBUG`: Enable debug mode

### Extension Configuration

2. **Extension Settings** (`extension/src/content.js` and `extension/src/background.js`):
```javascript
const EXTENSION_CONFIG = {
  BACKEND_URL: 'http://127.0.0.1:8787',    // Your backend URL
  API_KEY: 'your-api-key-here',            // Your API key
  DEFAULT_PERSONA: 'human',                // Default persona
  PRIVACY_STRIP_URLS: false,               // Remove URLs from tweets
  PRIVACY_STRIP_MENTIONS: false,           // Remove @mentions
  DEBUG_MODE: false                        // Enable debug logging
};
```

### Persona Customization

3. **AI Personas** (`server/app/services/prompts.py`):
```python
def _load_personas(self) -> Dict[str, Dict[str, str]]:
    return {
        "human": {
            "name": "Human",
            "description": "Friendly, conversational responses",
            "style": "conversational",
            "tone": "warm and friendly"
        },
        # Add custom personas here
    }
```

### Detailed Configuration

For comprehensive configuration options, see [CONFIG.md](extension/CONFIG.md).

**Quick Setup:**
1. Edit `server/.env` with your API keys
2. Edit `extension/src/content.js` with your backend URL
3. Reload the extension in Chrome
4. Start the backend server

## API Endpoints

- `POST /summarize` - Generate post summaries
- `POST /context` - Generate contextual information
- `POST /replies` - Generate reply suggestions
- `GET /health` - Health check endpoint

## Requirements

- Python 3.8+
- Chrome/Chromium browser
- FastAPI backend server
- Fireworks API key (for AI functionality)

## License

MIT License - see LICENSE file for details.

## Version History

### v1.0.0
- Initial release
- Core summarization, context, and reply features
- Multiple persona support
- Clean UI integration with X/Twitter
- Backend API with rate limiting and caching