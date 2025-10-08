# PostPilot Quick Start Guide

## 🚀 Get PostPilot Running in 5 Minutes

### 1. Get Your Fireworks API Key
- Go to [Fireworks AI](https://fireworks.ai/)
- Sign up and get your API key
- Copy the key (starts with `fw_`)

### 2. Start the Backend
```bash
# Navigate to server directory
cd server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pydantic pydantic-settings structlog aiohttp langdetect redis python-multipart

# Configure environment
cp env.example .env
# Edit .env and add your FIREWORKS_API_KEY

# Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8787 --reload
```

### 3. Install Extension
1. Open Chrome → `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" → Select `extension` folder
4. Done! 🎉

### 4. Use PostPilot
1. Go to [x.com](https://x.com)
2. Find any post
3. Click the "PP" button
4. Choose Summary, Context, or Replies
5. Copy and use the generated content

---

## 🔧 Quick Troubleshooting

**Backend not starting?**
```bash
# Check if port is free
lsof -i :8787
# Kill process if needed
kill -9 <PID>
```

**Extension not working?**
- Refresh the X/Twitter page
- Check browser console for errors
- Reload extension in `chrome://extensions/`

**API errors?**
- Verify your Fireworks API key in `server/.env`
- Check backend logs for error messages

---

## 📝 What You Need

- **Python 3.8+**
- **Chrome browser**
- **Fireworks API key** (free tier available)

That's it! PostPilot is ready to enhance your X/Twitter experience. 🚀
