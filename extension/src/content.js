const EXTENSION_CONFIG = {
  BACKEND_URL: 'http://127.0.0.1:8787',
  API_KEY: 'fw_3Zd6KUHb3tiiUAXGRdLygqJv',
  DEFAULT_PERSONA: 'human',
  PRIVACY_STRIP_URLS: false,
  PRIVACY_STRIP_MENTIONS: false,
  DEBUG_MODE: false
};

class PostPilotContent {
  constructor() {
    this.buttons = new Map();
    this.currentPost = null;
    this.observer = null;
    this.currentPanel = null;
    this.init();
  }

  init() {
    this.setupObserver();
    this.setupMessageListener();
    this.addButtonsToExistingTweets();
  }

  setupObserver() {
    this.observer = new MutationObserver((mutations) => {
      let shouldAddButtons = false;
      
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              const tweets = node.querySelectorAll ? 
                node.querySelectorAll('[data-testid="tweet"]') : [];
              if (tweets.length > 0) {
                shouldAddButtons = true;
              }
            }
          });
        }
      });

      if (shouldAddButtons) {
        setTimeout(() => this.addButtonsToExistingTweets(), 100);
      }
    });

    this.observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  setupMessageListener() {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === 'insertText') {
        this.insertTextIntoReplyBox(request.text);
        sendResponse({ success: true });
      }
    });
  }

  addButtonsToExistingTweets() {
    const tweetSelectors = [
      '[data-testid="tweet"]',
      'article[role="article"]',
      '[data-testid="primaryColumn"] article'
    ];

    tweetSelectors.forEach(selector => {
      const tweets = document.querySelectorAll(selector);
      tweets.forEach(tweet => {
        this.addButtonToTweet(tweet);
      });
    });
  }

  addButtonToTweet(tweetElement) {
    const tweetId = this.getTweetId(tweetElement);
    if (this.buttons.has(tweetId)) {
      return;
    }

    const actionContainer = tweetElement.querySelector('[role="group"]') ||
                           tweetElement.querySelector('[data-testid="reply"]')?.parentElement ||
                           tweetElement.querySelector('[data-testid="like"]')?.parentElement;

    if (!actionContainer) {
      return;
    }

    const ppButton = this.createPostPilotButton(tweetElement);
    
    const lastButton = actionContainer.lastElementChild;
    if (lastButton) {
      actionContainer.insertBefore(ppButton, lastButton);
    } else {
      actionContainer.appendChild(ppButton);
    }

    this.buttons.set(tweetId, ppButton);
  }

  createPostPilotButton(tweetElement) {
    const button = document.createElement('button');
    button.className = 'postpilot-tweet-button';
    button.innerHTML = `
      <div class="postpilot-button-content">
        <span class="postpilot-button-text">PP</span>
      </div>
    `;
    
    button.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.handlePostPilotClick(tweetElement);
    });

    return button;
  }

  getTweetId(tweetElement) {
    const tweetLink = tweetElement.querySelector('a[href*="/status/"]');
    if (tweetLink) {
      const href = tweetLink.getAttribute('href');
      const match = href.match(/\/status\/(\d+)/);
      if (match) {
        return match[1];
      }
    }
    return Math.random().toString(36).substr(2, 9);
  }

  handlePostPilotClick(tweetElement) {
    console.log('PP button clicked!');
    const tweetData = this.extractTweetData(tweetElement);
    console.log('Extracted tweet data:', tweetData);
    
    if (!tweetData.text) {
      console.error('Could not extract tweet text');
      return;
    }

    this.currentPost = tweetData;
    this.showPostPilotPanel(tweetData);
  }

  extractTweetData(tweetElement) {
    const textElement = tweetElement.querySelector('[data-testid="tweetText"]');
    const text = textElement ? textElement.textContent.trim() : '';
    
    const authorElement = tweetElement.querySelector('[data-testid="User-Name"]');
    const author = authorElement ? authorElement.textContent.trim() : '';
    
    const tweetLink = tweetElement.querySelector('a[href*="/status/"]');
    const url = tweetLink ? `https://x.com${tweetLink.getAttribute('href')}` : '';

    return {
      text,
      author,
      url,
      element: tweetElement
    };
  }

  showPostPilotPanel(tweetData) {
    console.log('Creating PostPilot panel...');
    alert('PostPilot panel should appear now!');
    this.hideExistingPanel();
    
    const panel = document.createElement('div');
    panel.className = 'postpilot-panel';
    console.log('Panel created:', panel);
    panel.innerHTML = `
      <div class="postpilot-panel-header">
        <div class="postpilot-panel-title">
          <svg class="postpilot-icon" viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          <span>PostPilot</span>
        </div>
        <button class="postpilot-panel-close">×</button>
      </div>
      <div class="postpilot-panel-content">
        <div class="postpilot-tweet-preview">
          <strong>Tweet:</strong> ${tweetData.text.substring(0, 100)}${tweetData.text.length > 100 ? '...' : ''}
      </div>
        <div class="postpilot-actions">
          <button class="postpilot-action" data-action="summary">
            <span>Summary</span>
        </button>
          <button class="postpilot-action" data-action="context">
            <span>Context</span>
        </button>
          <button class="postpilot-action" data-action="replies">
            <span>Replies</span>
        </button>
      </div>
        <div class="postpilot-persona-selector" id="persona-selector" style="display: none;">
        <label>Persona:</label>
        <select class="postpilot-persona-select">
          <option value="human">Human</option>
          <option value="hardcore">Hardcore</option>
          <option value="curator">Curator</option>
        </select>
      </div>
        <div class="postpilot-result" style="display: none;">
        <div class="result-content"></div>
        <div class="result-actions">
            <button class="copy-result-btn">Copy</button>
          <button class="close-result-btn">Close</button>
          </div>
        </div>
      </div>
    `;

    // Try different insertion methods
    try {
      // Create shadow DOM to isolate from X/Twitter CSS
      const shadowHost = document.createElement('div');
      shadowHost.style.cssText = 'position: fixed !important; top: 0 !important; left: 0 !important; z-index: 2147483647 !important; pointer-events: none !important;';
      document.body.appendChild(shadowHost);
      
      const shadowRoot = shadowHost.attachShadow({ mode: 'open' });
      shadowRoot.appendChild(panel);
      
      console.log('Panel added to shadow DOM');
    } catch (e) {
      console.error('Failed to create shadow DOM:', e);
      // Fallback to regular DOM
      try {
        document.body.appendChild(panel);
        console.log('Panel added to document body');
      } catch (e2) {
        console.error('Failed to append to body:', e2);
        tweetData.element.appendChild(panel);
        console.log('Panel added to tweet element');
      }
    }
    
    console.log('Panel element:', panel);
    console.log('Panel styles:', window.getComputedStyle(panel));
    
    // Force make panel visible with maximum priority
    panel.setAttribute('style', `
      position: fixed !important;
      top: 50px !important;
      left: 50px !important;
      z-index: 2147483647 !important;
      background-color: white !important;
      border: 3px solid red !important;
      padding: 20px !important;
      display: block !important;
      width: 400px !important;
      height: 300px !important;
      font-size: 18px !important;
      color: black !important;
      box-shadow: 0 0 20px rgba(255,0,0,0.8) !important;
      font-family: Arial, sans-serif !important;
      line-height: 1.4 !important;
    `);
    
    // Add a simple test message with inline styles
    panel.innerHTML = `
      <div style="color: black !important; font-size: 18px !important; font-weight: bold !important;">
        🚀 PostPilot Panel Test
      </div>
      <div style="color: black !important; font-size: 14px !important; margin-top: 10px !important;">
        This panel should be visible now!
      </div>
      <div style="color: black !important; font-size: 12px !important; margin-top: 10px !important;">
        Tweet: ${tweetData.text.substring(0, 50)}...
      </div>
    `;
    
    this.currentPanel = panel;
    this.setupPanelEventListeners(panel, tweetData);
  }

  setupPanelEventListeners(panel, tweetData) {
    console.log('Setting up panel event listeners...');
    
    // For now, just add a simple close button to the test panel
    const closeBtn = document.createElement('button');
    closeBtn.textContent = 'Close Panel';
    closeBtn.style.cssText = `
      position: absolute !important;
      top: 10px !important;
      right: 10px !important;
      background: red !important;
      color: white !important;
      border: none !important;
      padding: 5px 10px !important;
      cursor: pointer !important;
      font-size: 12px !important;
    `;
    
    closeBtn.addEventListener('click', () => {
      console.log('Close button clicked');
      this.closeCurrentPanel();
    });
    
    panel.appendChild(closeBtn);
    console.log('Close button added to panel');
  }

  handleAction(action, tweetData, panel) {
    const actionBtns = panel.querySelectorAll('.postpilot-action');
    const personaSelector = panel.querySelector('#persona-selector');
    const resultDiv = panel.querySelector('.postpilot-result');
    const resultContent = panel.querySelector('.result-content');

    actionBtns.forEach(btn => btn.classList.remove('active'));
    panel.querySelector(`[data-action="${action}"]`).classList.add('active');

    if (action === 'replies') {
      personaSelector.style.display = 'block';
    } else {
      personaSelector.style.display = 'none';
    }

    resultDiv.style.display = 'block';
    resultContent.innerHTML = '<div class="loading">Processing...</div>';

    const persona = personaSelector.querySelector('.postpilot-persona-select').value;
    
    this.processPost(tweetData, action, persona).then(result => {
      if (result.success) {
        this.displayResult(result.data, action, resultContent);
      } else {
        resultContent.innerHTML = `<div class="error">Error: ${result.error}</div>`;
      }
    });
  }

  displayResult(data, action, resultContent) {
    let content = '';
    
    if (action === 'summary') {
      content = data.summary;
    } else if (action === 'context') {
      content = data.context;
    } else if (action === 'replies') {
      content = data.replies.map((reply, index) => `${index + 1}. ${reply}`).join('\n\n');
    }
    
    resultContent.innerHTML = `<div class="result-text">${content}</div>`;
  }

  async processPost(tweetData, mode, persona) {
    try {
      console.log('Sending message to background script:', {
        action: 'processPost',
        data: {
          text: tweetData.text,
          author: tweetData.author,
          url: tweetData.url,
          mode: mode,
          persona: persona,
          backendUrl: EXTENSION_CONFIG.BACKEND_URL
        }
      });
      
      const response = await chrome.runtime.sendMessage({
        action: 'processPost',
        data: {
          text: tweetData.text,
          author: tweetData.author,
          url: tweetData.url,
          mode: mode,
          persona: persona,
          backendUrl: EXTENSION_CONFIG.BACKEND_URL
        }
      });
      
      console.log('Background script response:', response);
      return response;
    } catch (error) {
      console.error('Error processing post:', error);
      return { success: false, error: error.message };
    }
  }

  hideExistingPanel() {
    console.log('Hiding existing panel...');
    
    // Try to find panel in regular DOM
    const existingPanel = document.querySelector('.postpilot-panel');
    if (existingPanel) {
      console.log('Found panel in regular DOM, removing...');
      existingPanel.remove();
      return;
    }
    
    // Try to find panel in shadow DOM
    const shadowHosts = document.querySelectorAll('div[style*="position: fixed"]');
    shadowHosts.forEach(host => {
      if (host.shadowRoot) {
        const shadowPanel = host.shadowRoot.querySelector('.postpilot-panel');
        if (shadowPanel) {
          console.log('Found panel in shadow DOM, removing...');
          host.remove();
          return;
        }
      }
    });
    
    // Fallback: remove all shadow hosts that look like our panel
    const allShadowHosts = document.querySelectorAll('div');
    allShadowHosts.forEach(host => {
      if (host.style.cssText.includes('z-index: 2147483647')) {
        console.log('Removing shadow host by style...');
        host.remove();
      }
    });
    
    console.log('Panel hiding complete');
  }

  closeCurrentPanel() {
    console.log('Closing current panel...');
    if (this.currentPanel) {
      // Try to remove the panel directly
      if (this.currentPanel.parentNode) {
        this.currentPanel.parentNode.remove();
        console.log('Panel removed from parent');
      }
      // Try to remove the shadow host
      const shadowHosts = document.querySelectorAll('div');
      shadowHosts.forEach(host => {
        if (host.style.cssText.includes('z-index: 2147483647')) {
          console.log('Removing shadow host...');
          host.remove();
        }
      });
      this.currentPanel = null;
    } else {
      console.log('No current panel to close');
    }
  }

  insertTextIntoReplyBox(text) {
    const replyBox = document.querySelector('[data-testid="tweetTextarea_0"]');
    if (replyBox) {
      replyBox.focus();
        replyBox.value = text;
        replyBox.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new PostPilotContent();
  });
} else {
  new PostPilotContent();
}