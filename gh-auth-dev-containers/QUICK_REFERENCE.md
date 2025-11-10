# Quick Reference: GitHub CLI Auth in Dev Containers

## TL;DR - Just Give Me the Answer

**Use this in your `.devcontainer/devcontainer.json`:**

```json
{
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "remoteEnv": {
    "GH_TOKEN": "${localEnv:GH_TOKEN}"
  }
}
```

**Then set `GH_TOKEN` in VS Code User Settings JSON:**

```json
{
  "terminal.integrated.env.linux": { "GH_TOKEN": "ghp_YOUR_TOKEN" },
  "terminal.integrated.env.osx": { "GH_TOKEN": "ghp_YOUR_TOKEN" },
  "terminal.integrated.env.windows": { "GH_TOKEN": "ghp_YOUR_TOKEN" }
}
```

**Create token at:** https://github.com/settings/tokens

---

## One-Minute Setup Guide

### Step 1: Get a Token (1 minute)
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name it "VS Code Dev Container"
4. Check boxes: `repo`, `workflow`, `read:org`
5. Click "Generate token"
6. Copy the token (starts with `ghp_`)

### Step 2: Save in VS Code (30 seconds)
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "user settings json" and select it
3. Add the token to all three OS sections:
   ```json
   {
     "terminal.integrated.env.linux": {
       "GH_TOKEN": "ghp_paste_token_here"
     },
     "terminal.integrated.env.osx": {
       "GH_TOKEN": "ghp_paste_token_here"
     },
     "terminal.integrated.env.windows": {
       "GH_TOKEN": "ghp_paste_token_here"
     }
   }
   ```
4. Save and close

### Step 3: Update devcontainer.json (30 seconds)
Add these two sections to your `.devcontainer/devcontainer.json`:
```json
"features": {
  "ghcr.io/devcontainers/features/github-cli:1": {}
},
"remoteEnv": {
  "GH_TOKEN": "${localEnv:GH_TOKEN}"
}
```

### Step 4: Rebuild (1 minute)
1. Press `Ctrl+Shift+P` or `Cmd+Shift+P`
2. Type "rebuild container" and select it
3. Wait for container to rebuild
4. Done! Test with: `gh auth status`

**Total time: ~3 minutes**

---

## Common Issues & Quick Fixes

| Problem | Fix |
|---------|-----|
| "gh not authenticated" | Run `echo $GH_TOKEN` in container. If empty, check VS Code settings |
| "command not found: gh" | Add the `features` section to devcontainer.json |
| Token doesn't work | Check it starts with `ghp_` and has right scopes at https://github.com/settings/tokens |
| VS Code doesn't pass token | Restart VS Code after changing settings |
| Works on host, not container | Make sure you're using user settings, not workspace settings |

---

## Alternative: Use Host Config (No Token Needed)

**If you prefer not to create a token:**

1. Run on your computer: `gh auth login --insecure-storage`
2. Add to devcontainer.json:
   ```json
   "mounts": [
     "source=${localEnv:HOME}${localEnv:USERPROFILE}/.config/gh,target=/home/vscode/.config/gh,type=bind"
   ]
   ```
3. Rebuild container

**Note:** This stores credentials in plain text on your computer.

---

## Complete Example devcontainer.json

```json
{
  "name": "My Project",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",

  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },

  "remoteEnv": {
    "GH_TOKEN": "${localEnv:GH_TOKEN}"
  },

  "postCreateCommand": "gh auth status",

  "remoteUser": "vscode"
}
```

---

## Test Your Setup

```bash
# In dev container terminal:
gh auth status        # Should show "Logged in to github.com"
gh repo list          # Should list your repos
gh pr list            # Should show PRs (if any)
```

---

## Security Tips

- ✅ DO store token in VS Code user settings
- ✅ DO use minimal scopes (only what you need)
- ✅ DO set token expiration
- ❌ DON'T commit tokens to git
- ❌ DON'T share tokens with others
- ❌ DON'T use tokens in .env files tracked by git

---

## For CI/CD (GitHub Actions)

```yaml
- name: Setup
  run: |
    gh auth status
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Need More Details?

See the full [README.md](README.md) for:
- Detailed explanations
- Alternative methods
- Troubleshooting guide
- Best practices
- Security considerations
