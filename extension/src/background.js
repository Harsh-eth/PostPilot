const EXTENSION_CONFIG = {
  BACKEND_URL: 'http://127.0.0.1:8787',
  API_KEY: 'fw_3Zd6KUHb3tiiUAXGRdLygqJv',
  DEFAULT_PERSONA: 'human',
  PRIVACY_STRIP_URLS: false,
  PRIVACY_STRIP_MENTIONS: false,
  DEBUG_MODE: false
};

class PostPilotBackground {
  constructor() {
    this.cache = new Map();
    this.maxCacheSize = 100;
    this.retryAttempts = 3;
    this.retryDelay = 1000;
    this.setupMessageListener();
  }

  setupMessageListener() {
    if (chrome.runtime && chrome.runtime.onMessage) {
      chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        this.handleMessage(request, sender, sendResponse);
        return true;
      });
    }
  }

  async handleMessage(request, sender, sendResponse) {
    try {
      console.log('Background script received message:', request);
      switch (request.action) {
        case 'processPost':
          console.log('Processing post with data:', request.data);
          const result = await this.processPost(request.data);
          console.log('Process post result:', result);
          sendResponse(result);
          break;
        
        case 'openPopup':
          chrome.action.openPopup();
          sendResponse({ success: true });
          break;
        
        default:
          sendResponse({ success: false, error: 'Unknown action' });
      }
    } catch (error) {
      console.error('Background error:', error);
      sendResponse({ success: false, error: error.message });
    }
  }

  async processPost(data) {
    const { text, author, url, mode, persona, backendUrl } = data;
    
    const cacheKey = this.createCacheKey(text, mode, persona);
    
    if (this.cache.has(cacheKey)) {
      return { success: true, data: this.cache.get(cacheKey) };
    }

    const requestData = {
      text: this.normalizeText(text),
      author: author || null,
      url: url || null,
      persona: persona || 'human'
    };

    const response = await this.makeApiCall(backendUrl, mode, requestData);
    
    if (response.success) {
      this.cacheResult(cacheKey, response.data);
      
      await this.storeInHistory({
        mode,
        text: text.substring(0, 100) + '...',
        result: response.data,
        timestamp: Date.now()
      });
    }

    return response;
  }

  createCacheKey(text, mode, persona) {
    const normalized = this.normalizeText(text);
    return `${mode}:${persona}:${this.hashString(normalized)}`;
  }

  normalizeText(text) {
    return text
      .trim()
      .replace(/\s+/g, ' ')
      .toLowerCase();
  }

  hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return hash.toString();
  }

  async makeApiCall(backendUrl, mode, data) {
    const url = `${backendUrl}/${mode}`;
    const headers = {
      'Content-Type': 'application/json'
    };

    const settings = await this.getSettings();
    if (settings.apiKey) {
      headers['x-api-key'] = settings.apiKey;
    }

    for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers,
          body: JSON.stringify(data)
        });

        if (response.ok) {
          const result = await response.json();
          return { success: true, data: result };
        } else if (response.status === 429) {
          const delay = this.retryDelay * Math.pow(2, attempt);
          await this.sleep(delay);
          continue;
        } else {
          const errorText = await response.text();
          return { 
            success: false, 
            error: `API error: ${response.status} - ${errorText}` 
          };
        }
      } catch (error) {
        if (attempt === this.retryAttempts) {
          return { 
            success: false, 
            error: `Network error: ${error.message}` 
          };
        }
        
        const delay = this.retryDelay * Math.pow(2, attempt - 1);
        await this.sleep(delay);
      }
    }

    return { success: false, error: 'Max retries exceeded' };
  }

  async getSettings() {
    return {
      backendUrl: EXTENSION_CONFIG.BACKEND_URL,
      apiKey: EXTENSION_CONFIG.API_KEY,
      persona: EXTENSION_CONFIG.DEFAULT_PERSONA
    };
  }

  cacheResult(key, data) {
    if (this.cache.size >= this.maxCacheSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    
    this.cache.set(key, data);
  }

  async storeInHistory(entry) {
    try {
      if (!chrome.storage || !chrome.storage.sync) {
        return;
      }
      
      const result = await chrome.storage.sync.get(['history']);
      const history = result.history || [];

      const newEntry = {
        ...entry,
        id: Math.random().toString(36).substr(2, 9)
      };
      
      const updatedHistory = [newEntry, ...history].slice(0, 5);
      
      await chrome.storage.sync.set({ history: updatedHistory });
    } catch (error) {
      console.warn('Storage quota exceeded, skipping history storage');
    }
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

new PostPilotBackground();