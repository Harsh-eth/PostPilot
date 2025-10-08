const EXTENSION_CONFIG = {
  BACKEND_URL: 'http://127.0.0.1:8787',
  API_KEY: 'fw_3Zd6KUHb3tiiUAXGRdLygqJv',
  DEFAULT_PERSONA: 'human',
  PRIVACY_STRIP_URLS: false,
  PRIVACY_STRIP_MENTIONS: false,
  DEBUG_MODE: false
};

class PostPilotOptions {
  constructor() {
    this.init();
  }

  async init() {
    await this.loadSettings();
    this.setupEventListeners();
  }

  async loadSettings() {
    try {
      document.getElementById('backendUrl').value = EXTENSION_CONFIG.BACKEND_URL;
      document.getElementById('apiKey').value = EXTENSION_CONFIG.API_KEY;
      document.getElementById('persona').value = EXTENSION_CONFIG.DEFAULT_PERSONA;
      document.getElementById('privacyStripUrls').checked = EXTENSION_CONFIG.PRIVACY_STRIP_URLS;
      document.getElementById('privacyStripMentions').checked = EXTENSION_CONFIG.PRIVACY_STRIP_MENTIONS;
      document.getElementById('debugMode').checked = EXTENSION_CONFIG.DEBUG_MODE;
      
      this.showStatus('Configuration loaded from config.js', 'success');
    } catch (error) {
      console.error('Error loading settings:', error);
      this.showStatus('Error loading configuration', 'error');
    }
  }

  setupEventListeners() {
    document.getElementById('settingsForm').addEventListener('submit', (e) => {
      e.preventDefault();
      this.saveSettings();
    });

    document.getElementById('resetBtn').addEventListener('click', () => {
      this.resetSettings();
    });

    document.getElementById('testConnectionBtn').addEventListener('click', () => {
      this.testConnection();
    });

    document.getElementById('backBtn').addEventListener('click', () => {
      window.close();
    });

    document.getElementById('backendUrl').addEventListener('input', (e) => {
      this.validateBackendUrl(e.target.value);
    });
  }

  async saveSettings() {
    this.showStatus('Settings are configured in config.js file. Please edit that file and reload the extension.', 'info');
  }

  async resetSettings() {
    this.showStatus('Settings are configured in config.js file. Please edit that file and reload the extension.', 'info');
  }

  async testConnection() {
    this.showStatus('Testing connection...', 'loading');

    try {
      const headers = {
        'Content-Type': 'application/json'
      };
      
      if (EXTENSION_CONFIG.API_KEY) {
        headers['x-api-key'] = EXTENSION_CONFIG.API_KEY;
      }

      const response = await fetch(`${EXTENSION_CONFIG.BACKEND_URL}/health`, {
        method: 'GET',
        headers
      });

      if (response.ok) {
        this.showStatus('Connection successful!', 'success');
      } else {
        const errorText = await response.text();
        this.showStatus(`Connection failed: ${response.status} - ${errorText}`, 'error');
      }
    } catch (error) {
      console.error('Connection test error:', error);
      this.showStatus(`Connection failed: ${error.message}`, 'error');
    }
  }

  validateBackendUrl(url) {
    const urlPattern = /^https?:\/\/.+/;
    const isValid = urlPattern.test(url);
    const input = document.getElementById('backendUrl');
    
    if (url && !isValid) {
      input.style.borderColor = '#e74c3c';
    } else {
      input.style.borderColor = '';
    }
    
    return isValid;
  }

  showStatus(message, type = 'info') {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = `status status-${type}`;
    
    if (type === 'success' || type === 'error') {
      setTimeout(() => {
        status.textContent = '';
        status.className = 'status';
      }, 5000);
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new PostPilotOptions();
});
