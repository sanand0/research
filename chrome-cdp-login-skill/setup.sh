#!/bin/bash

echo "========================================"
echo "Chrome CDP Login Skill - Setup Script"
echo "========================================"
echo

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js first:"
    echo "   https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js $(node --version) found"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm."
    exit 1
fi

echo "✓ npm $(npm --version) found"

# Install dependencies
echo
echo "Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"

# Check for Chrome/Chromium
echo
echo "Checking for Chrome/Chromium..."

CHROME_PATH=""

if command -v google-chrome &> /dev/null; then
    CHROME_PATH=$(which google-chrome)
    echo "✓ Found Chrome at: $CHROME_PATH"
elif command -v chromium-browser &> /dev/null; then
    CHROME_PATH=$(which chromium-browser)
    echo "✓ Found Chromium at: $CHROME_PATH"
elif command -v chromium &> /dev/null; then
    CHROME_PATH=$(which chromium)
    echo "✓ Found Chromium at: $CHROME_PATH"
elif [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    echo "✓ Found Chrome at: $CHROME_PATH"
else
    echo "⚠️  Chrome/Chromium not found in standard locations"
    echo
    echo "Please install Chrome or Chromium:"
    echo "  Ubuntu/Debian: sudo apt-get install chromium-browser"
    echo "  macOS: brew install --cask google-chrome"
    echo "  Or download from: https://www.google.com/chrome/"
    echo
    echo "You can also specify a custom path in your code:"
    echo "  const cdp = new CDPHelper({ executablePath: '/path/to/chrome' });"
fi

# Create directories
echo
echo "Creating directories..."
mkdir -p .sessions
mkdir -p examples
echo "✓ Directories created"

# Create sample credentials file
if [ ! -f ".credentials.json" ]; then
    echo
    echo "Creating sample .credentials.json..."
    cat > .credentials.json << 'EOF'
{
  "pastebin": {
    "username": "your_username_here",
    "password": "your_password_here"
  },
  "github": {
    "username": "your_username_here",
    "password": "your_password_here"
  }
}
EOF
    echo "✓ Sample .credentials.json created"
    echo "  ⚠️  Please edit .credentials.json with your actual credentials"
else
    echo "✓ .credentials.json already exists"
fi

# Test the setup
echo
echo "Testing setup with a simple example..."
node -e "
const CDPHelper = require('./cdp-helper');
console.log('✓ CDPHelper loaded successfully');
"

if [ $? -eq 0 ]; then
    echo
    echo "========================================"
    echo "✓ Setup completed successfully!"
    echo "========================================"
    echo
    echo "Next steps:"
    echo "  1. Edit .credentials.json with your actual credentials (if needed)"
    echo "  2. Run examples:"
    echo "     node examples/basic-navigation.js"
    echo "     node examples/jsfiddle-example.js"
    echo "  3. Read SKILL.md for full documentation"
    echo
else
    echo
    echo "❌ Setup test failed"
    exit 1
fi
