#!/usr/bin/env node
const fs = require('fs');
const assert = require('assert');

const html = fs.readFileSync('index.html', 'utf8');

assert.match(html, /https:\/\/api\.buriedsignals\.com\/v1\/feedback/, 'shared feedback API endpoint is configured');
assert.doesNotMatch(html, /LINEAR_API_KEY/, 'Linear API key is never referenced client-side');
assert.doesNotMatch(html, /\/api\/feedback/, 'static GitHub Pages site does not point at a local serverless path');
console.log('feedback widget checks passed');
