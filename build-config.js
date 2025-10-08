#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Load environment variables from .env file if it exists
require('dotenv').config();

// Read the current config.js
const configPath = path.join(__dirname, 'extension/src/config.js');
let configContent = fs.readFileSync(configPath, 'utf8');

// Replace placeholders with environment variables
const replacements = {
  'http://127.0.0.1:8787': process.env.BACKEND_URL || 'http://127.0.0.1:8787',
  "''": `'${process.env.FIREWORKS_API_KEY || ''}'`,
  'false': process.env.DEBUG === 'true' ? 'true' : 'false'
};

// Apply replacements
Object.entries(replacements).forEach(([placeholder, value]) => {
  configContent = configContent.replace(placeholder, value);
});

// Write the updated config
fs.writeFileSync(configPath, configContent);

console.log('✅ Config updated with environment variables');
console.log(`Backend URL: ${process.env.BACKEND_URL || 'http://127.0.0.1:8787'}`);
console.log(`API Key: ${process.env.FIREWORKS_API_KEY ? 'Set' : 'Not set'}`);
console.log(`Debug Mode: ${process.env.DEBUG === 'true' ? 'Enabled' : 'Disabled'}`);
