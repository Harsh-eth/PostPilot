# PostPilot Extension Configuration

## Quick Setup

1. **Edit Configuration**: Open `src/config.js` and modify the settings:

```javascript
const EXTENSION_CONFIG = {
  // Backend server URL
  BACKEND_URL: 'http://127.0.0.1:8787',
  
  // API key for backend authentication (leave empty if no auth required)
  API_KEY: 'your-api-key-here',
  
  // Default persona for AI responses
  DEFAULT_PERSONA: 'human',
  
  // Privacy settings
  PRIVACY_STRIP_URLS: false,
  PRIVACY_STRIP_MENTIONS: false,
  
  // Debug mode
  DEBUG_MODE: false
};
```

2. **Reload Extension**: After making changes, reload the extension in Chrome:
   - Go to `chrome://extensions`
   - Find PostPilot extension
   - Click the reload button (🔄)

## Configuration Options

### Backend URL
- **Default**: `http://127.0.0.1:8787`
- **Description**: URL of your PostPilot backend server
- **Example**: `https://your-domain.com` for production

### API Key
- **Default**: Empty (no authentication)
- **Description**: API key for backend authentication
- **Example**: `fw_3Zd6KUHb3tiiUAXGRdLygqJv`

### Persona
- **Options**: `human`, `hardcore`, `curator`
- **Description**: Default AI response style
- **Default**: `human`

### Privacy Settings
- **PRIVACY_STRIP_URLS**: Remove URLs from text before processing
- **PRIVACY_STRIP_MENTIONS**: Remove @mentions from text before processing

### Debug Mode
- **DEBUG_MODE**: Enable console logging for debugging
- **Default**: `false`

## Backend Setup

Make sure your backend is running on the configured URL:

```bash
cd server
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8787
```

## Troubleshooting

1. **"Failed to fetch"**: Check if backend is running and URL is correct
2. **"Text too short"**: Enter at least 10 characters
3. **Settings not saving**: This is now handled via config.js file
4. **Extension not working**: Reload the extension after changing config.js
