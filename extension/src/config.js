const EXTENSION_CONFIG = {
  BACKEND_URL: 'http://127.0.0.1:8787', //this is default backend url
  API_KEY: '', //enter firework api key here
  DEFAULT_PERSONA: 'human',
  PRIVACY_STRIP_URLS: false,
  PRIVACY_STRIP_MENTIONS: false,
  DEBUG_MODE: false
};
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { EXTENSION_CONFIG };
} else if (typeof window !== 'undefined') {
  window.EXTENSION_CONFIG = EXTENSION_CONFIG;
} else if (typeof self !== 'undefined') {
  self.EXTENSION_CONFIG = EXTENSION_CONFIG;
}
