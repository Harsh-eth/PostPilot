# PostPilot Build Instructions

## Environment Variables Setup

1. Copy the environment variables from `server/env.example` to `server/.env`
2. Set your Fireworks API key in the `.env` file:
   ```
   FIREWORKS_API_KEY=your_fireworks_api_key_here
   ```

## Building the Extension

1. Install dependencies:
   ```bash
   npm install
   ```

2. Build the extension with environment variables:
   ```bash
   npm run build
   ```

3. Or for development:
   ```bash
   npm run dev
   ```

## Manual Configuration

If you prefer to set the API key manually, edit `extension/src/config.js`:

```javascript
const EXTENSION_CONFIG = {
  BACKEND_URL: 'http://127.0.0.1:8787',
  API_KEY: 'fw_your_fireworks_api_key_here', // Set your key here
  DEFAULT_PERSONA: 'human',
  PRIVACY_STRIP_URLS: false,
  PRIVACY_STRIP_MENTIONS: false,
  DEBUG_MODE: false
};
```

## Running the Backend

```bash
npm start
```

This will start the backend server on port 8787.
