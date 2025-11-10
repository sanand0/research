# Method 1: Environment Variable (GH_TOKEN)

## Overview
This method uses a GitHub Personal Access Token (PAT) passed via environment variable.

## Pros
- ✅ Simple and cross-platform (Windows, macOS, Linux)
- ✅ No file mounting required
- ✅ Works in all container environments (Docker, Podman, etc.)
- ✅ Good for CI/CD pipelines

## Cons
- ❌ Requires creating and managing a PAT
- ❌ Token must be set in host environment or VS Code secrets
- ❌ Less convenient than interactive `gh auth login`

## Setup Instructions

### 1. Create a GitHub Personal Access Token
- Go to https://github.com/settings/tokens
- Click "Generate new token" → "Generate new token (classic)"
- Select required scopes (repo, workflow, etc.)
- Copy the token

### 2. Set the token on your host
**Linux/macOS:**
```bash
export GH_TOKEN=ghp_your_token_here
# Add to ~/.bashrc or ~/.zshrc for persistence
```

**Windows (PowerShell):**
```powershell
$env:GH_TOKEN = "ghp_your_token_here"
# Add to PowerShell profile for persistence
```

**VS Code User Secrets (Recommended):**
- Press `Ctrl/Cmd+Shift+P`
- Run "Preferences: Open User Settings (JSON)"
- Add:
```json
{
  "terminal.integrated.env.linux": {
    "GH_TOKEN": "ghp_your_token_here"
  },
  "terminal.integrated.env.osx": {
    "GH_TOKEN": "ghp_your_token_here"
  },
  "terminal.integrated.env.windows": {
    "GH_TOKEN": "ghp_your_token_here"
  }
}
```

### 3. Open in dev container
The token will be automatically available.

### 4. Verify
```bash
gh auth status
```

## Security Notes
- Never commit tokens to git
- Use VS Code secrets or environment variables
- Rotate tokens regularly
- Use minimal required scopes
