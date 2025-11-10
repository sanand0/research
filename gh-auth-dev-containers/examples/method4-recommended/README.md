# Method 4: Recommended Flexible Approach

## Overview
This is the **recommended approach** that combines multiple authentication methods with proper fallback and verification.

## Key Features
- ✅ Supports GH_TOKEN environment variable (primary)
- ✅ Supports mounted config file (fallback)
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Automatic verification on container creation
- ✅ Clear error messages and guidance
- ✅ Works for teams with different preferences

## Quick Start

### Option A: Environment Variable (Recommended)

1. **Create a GitHub Personal Access Token:**
   - Visit https://github.com/settings/tokens
   - Generate new token (classic)
   - Select scopes: `repo`, `workflow`, `read:org`
   - Copy the token

2. **Set in VS Code (Recommended):**

   Press `Ctrl/Cmd+Shift+P` → "Preferences: Open User Settings (JSON)"

   Add:
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

3. **Open in dev container** - Authentication will work automatically!

### Option B: Mount Configuration (Alternative)

1. **Authenticate on host:**
   ```bash
   gh auth login --insecure-storage
   ```

2. **Uncomment mounts in devcontainer.json** (they're included by default)

3. **Open in dev container** - Configuration will be mounted!

## Configuration Options

### Basic Setup (GH_TOKEN only)
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

### Flexible Setup (Both methods)
```json
{
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "remoteEnv": {
    "GH_TOKEN": "${localEnv:GH_TOKEN}"
  },
  "mounts": [
    "source=${localEnv:HOME}${localEnv:USERPROFILE}/.config/gh,target=/home/vscode/.config/gh,type=bind"
  ]
}
```

## Why This Approach?

### 1. **Team Flexibility**
Different developers can use different authentication methods:
- CI/CD pipelines: Use `GH_TOKEN`
- Developers with file-based auth: Use mounts
- Developers with keyring: Use `GH_TOKEN`

### 2. **Cross-Platform**
- `${localEnv:HOME}` works on Linux/macOS
- `${localEnv:USERPROFILE}` works on Windows
- `${localEnv:GH_TOKEN}` works everywhere

### 3. **Automatic Verification**
The `postCreateCommand` script checks authentication and provides helpful guidance.

### 4. **Security Considerations**
- Environment variables don't expose files
- Mounted files are user-specific
- Clear separation from container images

## Verification Script

The included `verify-auth.sh` script:
- ✅ Checks if gh is installed
- ✅ Tests authentication status
- ✅ Provides clear success/failure messages
- ✅ Offers guidance for unauthenticated users

## Advanced: Per-Project Configuration

For projects that need specific tokens:

1. **Create `.env` file** (add to `.gitignore`):
   ```bash
   GH_TOKEN=ghp_project_specific_token
   ```

2. **Update devcontainer.json**:
   ```json
   {
     "runArgs": ["--env-file", ".env"]
   }
   ```

## Comparison to Other Methods

| Feature | Method 1 (Env Var) | Method 2 (Mount) | Method 3 (Manual) | Method 4 (This) |
|---------|-------------------|------------------|-------------------|-----------------|
| Cross-platform | ✅ | ⚠️ (needs setup) | ✅ | ✅ |
| Automated | ✅ | ✅ | ❌ | ✅ |
| Secure | ✅ | ⚠️ (plain text) | ⚠️ (plain text) | ✅ |
| Team-friendly | ⚠️ (token sharing) | ⚠️ (setup needed) | ❌ | ✅ |
| CI/CD ready | ✅ | ❌ | ❌ | ✅ |
| Persists rebuilds | ✅ | ✅ | ❌ | ✅ |
| Flexibility | ⚠️ (one method) | ⚠️ (one method) | ⚠️ (one method) | ✅ |

## Troubleshooting

### "gh not authenticated"

**Check 1: Environment variable**
```bash
echo $GH_TOKEN
```
If empty, set it in VS Code settings or shell profile.

**Check 2: Mounted configuration**
```bash
ls ~/.config/gh/hosts.yml
```
If missing, run `gh auth login --insecure-storage` on host.

**Check 3: Manual authentication (temporary)**
```bash
gh auth login --insecure-storage
```

### Permission errors with mounted config
```bash
# On host
chmod 700 ~/.config/gh
chmod 600 ~/.config/gh/hosts.yml
```

### VS Code not passing environment variables
- Restart VS Code after changing settings
- Check the user settings JSON (not workspace settings)
- Ensure no typos in variable names

## Best Practices

1. **For Individual Developers:** Use GH_TOKEN in VS Code user settings
2. **For Teams:** Document both methods in project README
3. **For CI/CD:** Use GH_TOKEN from secrets
4. **For Security:** Rotate tokens regularly, use minimal scopes
5. **For Convenience:** Keep the verification script for debugging

## Next Steps

After authentication works:
- Test with `gh repo list`
- Use in scripts: `gh pr create`, `gh issue create`
- Integrate into development workflows
- Add to CI/CD pipelines
