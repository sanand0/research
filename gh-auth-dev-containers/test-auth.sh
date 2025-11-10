#!/bin/bash

# Test script for GitHub CLI authentication in containers
# This script tests authentication methods without requiring a full dev container

set -e

echo "=========================================="
echo "GitHub CLI Authentication Test"
echo "=========================================="
echo ""

# Test 1: Check if gh is available on host
echo "Test 1: Checking host environment..."
if command -v gh &> /dev/null; then
    echo "✅ gh CLI installed on host: $(gh --version | head -n1)"

    # Check host authentication
    if gh auth status &> /dev/null 2>&1; then
        echo "✅ gh is authenticated on host"
    else
        echo "⚠️  gh is NOT authenticated on host"
    fi
else
    echo "❌ gh CLI not installed on host"
fi
echo ""

# Test 2: Check for environment variable
echo "Test 2: Checking GH_TOKEN environment variable..."
if [ -n "$GH_TOKEN" ]; then
    echo "✅ GH_TOKEN is set (length: ${#GH_TOKEN} characters)"
    # Test if token works by trying to access API
    if command -v curl &> /dev/null; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token $GH_TOKEN" https://api.github.com/user)
        if [ "$HTTP_CODE" = "200" ]; then
            echo "✅ GH_TOKEN is valid and working"
        else
            echo "❌ GH_TOKEN appears invalid (HTTP $HTTP_CODE)"
        fi
    fi
else
    echo "❌ GH_TOKEN is not set"
    echo "   Set it with: export GH_TOKEN=ghp_your_token_here"
fi
echo ""

# Test 3: Check for config file
echo "Test 3: Checking for gh config file..."
GH_CONFIG="$HOME/.config/gh/hosts.yml"
if [ -f "$GH_CONFIG" ]; then
    echo "✅ Config file exists: $GH_CONFIG"
    echo "   Permissions: $(ls -l $GH_CONFIG | awk '{print $1}')"

    # Check if it contains oauth_token
    if grep -q "oauth_token" "$GH_CONFIG" 2>/dev/null; then
        echo "✅ Config contains oauth_token (file-based storage)"
    else
        echo "⚠️  Config exists but may use keyring storage"
        echo "   Use: gh auth login --insecure-storage"
    fi
else
    echo "❌ Config file not found: $GH_CONFIG"
    echo "   Run: gh auth login --insecure-storage"
fi
echo ""

# Test 4: Test in a Docker container
echo "Test 4: Testing authentication in Docker container..."
if command -v docker &> /dev/null; then
    echo "Creating test container..."

    # Test with GH_TOKEN if available
    if [ -n "$GH_TOKEN" ]; then
        echo "Testing with GH_TOKEN..."
        docker run --rm \
            -e GH_TOKEN="$GH_TOKEN" \
            ubuntu:22.04 bash -c '
                apt-get update -qq && apt-get install -y -qq gh > /dev/null 2>&1
                if gh auth status &> /dev/null; then
                    echo "✅ Authentication works in container with GH_TOKEN"
                else
                    echo "❌ Authentication failed in container"
                fi
            ' 2>/dev/null || echo "❌ Docker test failed"
    else
        echo "⚠️  Skipping container test (no GH_TOKEN)"
    fi
else
    echo "⚠️  Docker not available, skipping container test"
fi
echo ""

# Summary
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
echo "Recommended approaches:"
echo ""
if [ -n "$GH_TOKEN" ]; then
    echo "✅ Method 1 (GH_TOKEN): Ready to use"
    echo "   This will work in dev containers automatically"
else
    echo "❌ Method 1 (GH_TOKEN): Not configured"
    echo "   Create a token at: https://github.com/settings/tokens"
    echo "   Then: export GH_TOKEN=ghp_your_token_here"
fi
echo ""

if [ -f "$GH_CONFIG" ]; then
    echo "✅ Method 2 (Mount config): Ready to use"
    echo "   Your config file can be mounted in containers"
else
    echo "❌ Method 2 (Mount config): Not configured"
    echo "   Run: gh auth login --insecure-storage"
fi
echo ""

echo "For dev containers, use Method 4 (Recommended)"
echo "which supports both approaches."
echo "=========================================="
