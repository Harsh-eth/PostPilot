const EXTENSION_CONFIG = {
  BACKEND_URL: 'http://127.0.0.1:8787',
  API_KEY: 'fw_3Zd6KUHb3tiiUAXGRdLygqJv',
  DEFAULT_PERSONA: 'human',
  PRIVACY_STRIP_URLS: false,
  PRIVACY_STRIP_MENTIONS: false,
  DEBUG_MODE: false
};

class PostPilotPopup {
  constructor() {
    this.currentResult = null;
    this.init();
  }

  async init() {
    await this.loadSettings();
    this.setupEventListeners();
    this.updateCharCount();
    this.updateUI();
  }

  async loadSettings() {
    try {
      const personaSelect = document.getElementById('personaSelect');
      personaSelect.value = EXTENSION_CONFIG.DEFAULT_PERSONA;
      
      if (!EXTENSION_CONFIG.BACKEND_URL) {
        this.showStatus('Please configure backend URL in config.js', 'error');
        return false;
      }
      
      return true;
    } catch (error) {
      console.error('Error loading settings:', error);
      this.showStatus('Error loading settings', 'error');
      return false;
    }
  }

  setupEventListeners() {
    document.getElementById('runBtn').addEventListener('click', () => {
      this.runAnalysis();
    });

    document.getElementById('copyBtn').addEventListener('click', () => {
      this.copyResult();
    });

    document.getElementById('copyHooksBtn').addEventListener('click', () => {
      this.copyHooks();
    });



    document.getElementById('textInput').addEventListener('keydown', (e) => {
      if (e.ctrlKey && e.key === 'Enter') {
        this.runAnalysis();
      }
    });

    document.getElementById('modeSelect').addEventListener('change', (e) => {
      this.updateUI();
    });

    document.getElementById('textInput').addEventListener('input', () => {
      this.updateCharCount();
    });

    document.getElementById('modeSelect').addEventListener('change', () => {
      this.updateUI();
    });
  }

  async runAnalysis() {
    const textInput = document.getElementById('textInput');
    const modeSelect = document.getElementById('modeSelect');
    const personaSelect = document.getElementById('personaSelect');
    
    const text = textInput.value.trim();
    if (!text) {
      this.showStatus('Please enter some text', 'error');
      return;
    }

    if (text.length < 10) {
      this.showStatus('Text too short. Please enter at least 10 characters.', 'error');
      return;
    }

    const mode = modeSelect.value;
    const persona = personaSelect.value;

    this.showStatus('Processing...', 'loading');
    this.setLoading(true);

    try {
      console.log('Popup config:', EXTENSION_CONFIG);
      
      if (!EXTENSION_CONFIG.BACKEND_URL) {
        throw new Error('Backend URL not configured. Please check config.js.');
      }
      
      const response = await fetch(`${EXTENSION_CONFIG.BACKEND_URL}/${mode}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(EXTENSION_CONFIG.API_KEY && { 'x-api-key': EXTENSION_CONFIG.API_KEY })
        },
        body: JSON.stringify({
          text,
          persona,
          url: null,
          author: null
        })
      });

      if (!response.ok) {
        let errorMessage = `Server error: ${response.status}`;
        try {
          const errorData = await response.json();
          if (errorData.error) {
            errorMessage = errorData.error;
          }
        } catch (e) {
          const errorText = await response.text();
          if (errorText) {
            errorMessage = errorText;
          }
        }
        throw new Error(errorMessage);
      }

      const result = await response.json();
      this.currentResult = result;
      this.showResult(result, mode);
      this.showStatus('Success', 'success');
      
    } catch (error) {
      console.error('Analysis error:', error);
      let errorMessage = error.message;
      
      if (error.message.includes('Failed to fetch')) {
        errorMessage = 'Cannot connect to backend. Please check your backend URL and ensure the server is running.';
      } else if (error.message.includes('Invalid or too short text')) {
        errorMessage = 'Text is too short. Please enter at least 10 characters.';
      }
      
      this.showStatus(errorMessage, 'error');
    } finally {
      this.setLoading(false);
    }
  }

  showResult(result, mode) {
    const outputSection = document.getElementById('outputSection');
    const outputContent = document.getElementById('outputContent');
    const copyHooksBtn = document.getElementById('copyHooksBtn');
    
    outputSection.style.display = 'block';
    
    let html = '';
    
    switch (mode) {
      case 'summarize':
        html = this.formatSummary(result);
        copyHooksBtn.style.display = 'none';
        break;
        
      case 'context':
        html = this.formatContext(result);
        copyHooksBtn.style.display = 'none';
        break;
        
      case 'replies':
        html = this.formatReplies(result);
        copyHooksBtn.style.display = 'inline-block';
        break;
    }
    
    outputContent.innerHTML = html;
  }

  formatSummary(result) {
    const summary = result.summary || result.text || 'No summary available';
    return `<div class="result-summary">${summary}</div>`;
  }

  formatContext(result) {
    const context = result.context || result.text || 'No context available';
    const bullets = context.split('\n').filter(line => line.trim());
    
    let html = '<div class="result-context">';
    bullets.forEach(bullet => {
      if (bullet.trim()) {
        html += `<div class="context-bullet">• ${bullet.trim()}</div>`;
      }
    });
    html += '</div>';
    
    return html;
  }

  formatReplies(result) {
    const replies = result.replies || result.text || [];
    const replyArray = Array.isArray(replies) ? replies : [replies];
    
    let html = '<div class="result-replies">';
    replyArray.forEach((reply, index) => {
      html += `<div class="reply-item">
        <div class="reply-number">${index + 1}</div>
        <div class="reply-text">${reply}</div>
      </div>`;
    });
    html += '</div>';
    
    return html;
  }

  copyResult() {
    if (!this.currentResult) return;
    
    const mode = document.getElementById('modeSelect').value;
    let text = '';
    
    switch (mode) {
      case 'summarize':
        text = this.currentResult.summary || this.currentResult.text || '';
        break;
      case 'context':
        text = this.currentResult.context || this.currentResult.text || '';
        break;
      case 'replies':
        const replies = this.currentResult.replies || this.currentResult.text || [];
        text = Array.isArray(replies) ? replies.join('\n') : replies;
        break;
    }
    
    navigator.clipboard.writeText(text).then(() => {
      this.showStatus('Copied to clipboard', 'success');
    }).catch(err => {
      console.error('Copy failed:', err);
      this.showStatus('Copy failed', 'error');
    });
  }

  copyHooks() {
    if (!this.currentResult) return;
    
    const replies = this.currentResult.replies || this.currentResult.text || [];
    const replyArray = Array.isArray(replies) ? replies : [replies];
    const text = replyArray.join('\n');
    
    navigator.clipboard.writeText(text).then(() => {
      this.showStatus('Hooks copied to clipboard', 'success');
    }).catch(err => {
      console.error('Copy failed:', err);
      this.showStatus('Copy failed', 'error');
    });
  }


  updateUI() {
    const mode = document.getElementById('modeSelect').value;
    const copyHooksBtn = document.getElementById('copyHooksBtn');
    const personaGroup = document.getElementById('personaGroup');
    
    if (mode === 'replies') {
      copyHooksBtn.style.display = 'inline-block';
      personaGroup.style.display = 'block';
    } else {
      copyHooksBtn.style.display = 'none';
      personaGroup.style.display = 'none';
    }
  }

  updateCharCount() {
    const textInput = document.getElementById('textInput');
    const charCount = document.getElementById('charCount');
    const length = textInput.value.length;
    
    charCount.textContent = `(${length}/10 min)`;
    
    if (length < 10) {
      charCount.className = 'char-count char-count-warning';
    } else {
      charCount.className = 'char-count char-count-ok';
    }
  }

  setLoading(loading) {
    const runBtn = document.getElementById('runBtn');
    runBtn.disabled = loading;
    runBtn.textContent = loading ? 'Processing...' : 'Run';
  }

  showStatus(message, type = 'info') {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = `status status-${type}`;
    
    if (type === 'success' || type === 'error') {
      setTimeout(() => {
        status.textContent = 'Ready';
        status.className = 'status';
      }, 3000);
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new PostPilotPopup();
});
