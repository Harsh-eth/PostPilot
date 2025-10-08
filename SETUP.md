# PostPilot Setup Guide

## Complete Step-by-Step Installation

### Prerequisites
- Python 3.8+ installed
- Chrome/Chromium browser
- Fireworks API key (get from [Fireworks AI](https://fireworks.ai/))

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/Harsh-eth/PostPilot.git
cd PostPilot
```

---

## Step 2: Backend Setup

### 2.1 Navigate to Server Directory
```bash
cd server
```

### 2.2 Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2.3 Install Dependencies
```bash
pip install fastapi uvicorn pydantic pydantic-settings structlog aiohttp langdetect redis python-multipart
```

### 2.4 Configure Environment Variables
```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file with your settings
nano .env  # or use your preferred editor
```

**Required .env settings:**
```bash
# Server Configuration
BACKEND_PORT=8787
DEBUG=false

# Fireworks API Configuration (REQUIRED)
FIREWORKS_API_KEY=your_fireworks_api_key_here
DEFAULT_MODEL=accounts/fireworks/models/dobby-7b-v2
MAX_TOKENS=500
TEMPERATURE=0.7

# Rate Limiting
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=300
```

### 2.5 Start the Backend Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8787 --reload
```

**✅ Backend is now running on http://localhost:8787**

---

## Step 3: Extension Setup

### 3.1 Configure Extension (Optional)
If you want to customize settings, edit `extension/src/config.js`:

```javascript
const EXTENSION_CONFIG = {
  BACKEND_URL: 'http://127.0.0.1:8787',  // Your backend URL
  API_KEY: '',                           // Leave empty (uses backend)
  DEFAULT_PERSONA: 'human',              // Default persona
  PRIVACY_STRIP_URLS: false,             // Remove URLs from tweets
  PRIVACY_STRIP_MENTIONS: false,         // Remove @mentions
  DEBUG_MODE: false                      // Enable debug logging
};
```

### 3.2 Install Extension in Chrome

1. **Open Chrome** and go to `chrome://extensions/`

2. **Enable Developer Mode**:
   - Toggle the "Developer mode" switch in the top right

3. **Load the Extension**:
   - Click "Load unpacked"
   - Navigate to the `PostPilot/extension` folder
   - Select the folder and click "Select Folder"

4. **Verify Installation**:
   - You should see "PostPilot" in your extensions list
   - The extension icon should appear in your browser toolbar

---

## Step 4: Usage

### 4.1 Navigate to X/Twitter
- Go to [x.com](https://x.com) or [twitter.com](https://twitter.com)
- Find any post you want to analyze

### 4.2 Use PostPilot
1. **Look for the "PP" button** next to the like/retweet buttons
2. **Click the "PP" button** to open the PostPilot panel
3. **Choose your action**:
   - **Summary**: Get a concise summary of the post
   - **Context**: Get background information and context
   - **Replies**: Generate reply suggestions with different personas

### 4.3 For Reply Suggestions
1. Click "Replies" in the PostPilot panel
2. Select your preferred persona:
   - **Human**: Friendly, conversational responses
   - **Hardcore**: Direct, no-nonsense responses  
   - **Curator**: Thoughtful, analytical responses
3. Copy the generated reply and use it

---

## Step 5: Troubleshooting

### Backend Issues
- **Port already in use**: Change the port in `.env` file
- **API key errors**: Verify your Fireworks API key is correct
- **Import errors**: Make sure all dependencies are installed

### Extension Issues
- **Extension not loading**: Check that you selected the `extension` folder (not `src`)
- **PP button not appearing**: Refresh the X/Twitter page
- **Backend connection failed**: Ensure the backend server is running

### Common Solutions
```bash
# Check if backend is running
curl http://localhost:8787/health

# Restart backend server
# Press Ctrl+C to stop, then restart with:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8787 --reload

# Reload extension in Chrome
# Go to chrome://extensions/ and click the reload button
```

---

## Step 6: Advanced Configuration

### Custom Personas
Edit `server/app/services/prompts.py` to add custom personas:

```python
def _load_personas(self) -> Dict[str, Dict[str, str]]:
    return {
        "human": {
            "name": "Human",
            "description": "Friendly, conversational responses",
            "style": "conversational",
            "tone": "warm and friendly"
        },
        "your_custom_persona": {
            "name": "Your Custom Persona",
            "description": "Your custom description",
            "style": "your style",
            "tone": "your tone"
        }
    }
```

### Rate Limiting
Adjust rate limiting in `server/.env`:
```bash
RATE_LIMIT_REQUESTS=100  # Requests per window
RATE_LIMIT_WINDOW=300    # Window in seconds
```

---

## Step 7: Production Deployment

### Backend Deployment
1. Set up a production server (AWS, DigitalOcean, etc.)
2. Update `BACKEND_URL` in extension config
3. Use environment variables for production settings
4. Set up proper SSL certificates

### Extension Distribution
1. Package the extension: `zip -r postpilot-extension.zip extension/`
2. Submit to Chrome Web Store (if desired)
3. Or distribute the zip file for manual installation

---

## Support

If you encounter issues:
1. Check the browser console for errors
2. Check the backend server logs
3. Verify all environment variables are set correctly
4. Ensure the backend server is accessible from your browser

**Happy PostPiloting! 🚀**
