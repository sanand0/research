#!/bin/bash

echo "========================================="
echo "GitHub CLI Authentication Verification"
echo "========================================="
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ gh CLI is not installed"
    exit 1
fi

echo "✅ gh CLI installed: $(gh --version | head -n1)"
echo ""

# Check authentication status
echo "Checking authentication..."
if gh auth status &> /dev/null; then
    echo "✅ GitHub CLI is authenticated!"
    echo ""
    gh auth status
    echo ""
    echo "You can now use gh commands like:"
    echo "  - gh repo list"
    echo "  - gh pr list"
    echo "  - gh issue list"
else
    echo "⚠️  GitHub CLI is NOT authenticated"
    echo ""
    echo "Available authentication methods:"
    echo ""
    echo "1. Environment Variable (Recommended):"
    echo "   Set GH_TOKEN in your host environment or VS Code settings"
    echo "   Then rebuild the container"
    echo ""
    echo "2. Mount Configuration (Alternative):"
    echo "   Run on host: gh auth login --insecure-storage"
    echo "   Then rebuild the container"
    echo ""
    echo "3. Manual Authentication (Temporary):"
    echo "   Run: gh auth login --insecure-storage"
    echo "   Note: Lost on container rebuild"
    echo ""
fi

echo "========================================="
