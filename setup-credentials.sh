#!/bin/bash

echo "🔥 CityPulse Credentials Setup"
echo "============================="
echo ""

cd credentials
node setup-credentials.js

echo ""
echo "✅ Credentials setup completed!"
echo "📝 Please review your .env.local file and update with actual values"
echo ""
