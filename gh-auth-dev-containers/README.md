# GitHub CLI Authentication in Dev Containers: A Cross-Platform Guide

**Research Date:** November 10, 2025
**Objective:** Find the cleanest cross-platform way to share GitHub CLI (`gh`) authentication into dev containers safely.

## Executive Summary

After extensive research and testing, **the recommended approach is to use the `GH_TOKEN` environment variable** as the primary authentication method, with optional file mounting as a fallback. This provides the best balance of:

- ✅ Cross-platform compatibility (Windows, macOS, Linux)
- ✅ Security (no plain-text credentials in repositories)
- ✅ Team flexibility (supports different developer preferences)
- ✅ CI/CD readiness (works in automated environments)
- ✅ Persistence across container rebuilds

## Table of Contents

1. [Understanding the Problem](#understanding-the-problem)
2. [Authentication Methods Comparison](#authentication-methods-comparison)
3. [Recommended Solution](#recommended-solution)
4. [Quick Start](#quick-start)
5. [Alternative Methods](#alternative-methods)
6. [Testing](#testing)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Understanding the Problem

### The Challenge

GitHub CLI (`gh`) needs authentication to work, but dev containers present unique challenges:

- **Container isolation**: Credentials from the host aren't automatically available
- **Persistence**: Authentication should survive container rebuilds
- **Cross-platform**: Solution must work on Windows, macOS, and Linux
- **Security**: Credentials shouldn't be baked into container images
- **Keyring limitation**: Modern `gh` (v2.24.0+) uses system keyrings which don't work well in containers

### How gh Stores Authentication

| Version | Storage Method | Location | Container-Friendly? |
|---------|---------------|----------|-------------------|
| Pre v2.24.0 | Plain text file | `~/.config/gh/hosts.yml` | ✅ Yes |
| v2.24.0+ | System keyring | OS-specific (Keychain, gnome-keyring, etc.) | ❌ No |
| Any | Environment variable | `GH_TOKEN` | ✅ Yes |
| Any | File with flag | `~/.config/gh/hosts.yml` (with `--insecure-storage`) | ✅ Yes |

## Authentication Methods Comparison

| Method | Cross-Platform | Security | Ease of Setup | CI/CD Ready | Persists Rebuilds | Team-Friendly |
|--------|---------------|----------|---------------|-------------|-------------------|---------------|
| **GH_TOKEN** | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| **Mount config file** | ⚠️ | ⚠️ | ⚠️ | ❌ | ✅ | ✅ |
| **Manual auth** | ✅ | ⚠️ | ✅ | ❌ | ❌ | ⚠️ |
| **Recommended (hybrid)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### Method Details

#### 1. GH_TOKEN Environment Variable ⭐ **Recommended**

**How it works:** Set the `GH_TOKEN` environment variable with a GitHub Personal Access Token (PAT).

**Pros:**
- Truly cross-platform
- No file system dependencies
- Works in all container runtimes
- Perfect for CI/CD
- Secure when using VS Code secrets

**Cons:**
- Requires creating and managing a PAT
- Token rotation needed for security

#### 2. Mount Config File

**How it works:** Mount `~/.config/gh/hosts.yml` from host to container.

**Pros:**
- Uses existing host authentication
- No token management needed

**Cons:**
- Requires `--insecure-storage` flag on host
- Plain-text credentials on host
- File permissions can be tricky
- Doesn't work with keyring auth

#### 3. Manual Authentication

**How it works:** Run `gh auth login --insecure-storage` inside the container.

**Pros:**
- Simple configuration
- No host setup required

**Cons:**
- Lost on container rebuild
- Poor developer experience
- Not suitable for automation

#### 4. Recommended Hybrid Approach ⭐

**How it works:** Combine methods 1 and 2 with automatic fallback.

**Pros:**
- All benefits of method 1
- Fallback to method 2 if needed
- Team members can choose their preferred method
- Includes verification script

**Cons:**
- Slightly more complex configuration

## Recommended Solution

### Configuration

Create `.devcontainer/devcontainer.json`:

```json
{
  "name": "My Project",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",

  // Install GitHub CLI
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },

  // Primary method: Environment variable
  "remoteEnv": {
    "GH_TOKEN": "${localEnv:GH_TOKEN}"
  },

  // Optional fallback: Mount config
  "mounts": [
    "source=${localEnv:HOME}${localEnv:USERPROFILE}/.config/gh,target=/home/vscode/.config/gh,type=bind,consistency=cached"
  ],

  "postCreateCommand": "gh auth status || echo 'See README for authentication setup'",
  "remoteUser": "vscode"
}
```

### Why This Works

1. **${localEnv:GH_TOKEN}** - Pulls from host environment, works everywhere
2. **${localEnv:HOME}** - Linux/macOS home directory
3. **${localEnv:USERPROFILE}** - Windows user profile
4. **Features** - Installs gh CLI automatically
5. **Mounts** - Optional fallback for file-based auth

## Quick Start

### Option A: Environment Variable (Recommended)

**1. Create a GitHub Personal Access Token:**
- Visit https://github.com/settings/tokens
- Click "Generate new token (classic)"
- Select scopes: `repo`, `workflow`, `read:org`
- Copy the token (starts with `ghp_`)

**2. Configure VS Code (Recommended):**

Open VS Code User Settings JSON (`Ctrl/Cmd+Shift+P` → "Preferences: Open User Settings (JSON)"):

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

**3. Rebuild dev container** - Authentication will work automatically!

### Option B: Mount Configuration

**1. Authenticate on host:**
```bash
gh auth login --insecure-storage
```

**2. Verify config file exists:**
```bash
# Linux/macOS
ls ~/.config/gh/hosts.yml

# Windows
dir %USERPROFILE%\.config\gh\hosts.yml
```

**3. Rebuild dev container** - Configuration will be mounted!

## Alternative Methods

This repository includes 4 example configurations in the `examples/` directory:

- **method1-env-var/** - Pure GH_TOKEN approach
- **method2-mount-file/** - File mounting approach
- **method3-feature-only/** - Manual authentication
- **method4-recommended/** - Hybrid approach (recommended)

Each includes a complete `.devcontainer/` setup and detailed README.

## Testing

### Test Script

Run `./test-auth.sh` to validate your setup:

```bash
cd gh-auth-dev-containers
./test-auth.sh
```

The script checks:
- ✅ Host gh CLI installation
- ✅ GH_TOKEN environment variable
- ✅ Config file existence and permissions
- ✅ Docker container authentication (if available)

### Expected Output

```
==========================================
GitHub CLI Authentication Test
==========================================

Test 1: Checking host environment...
✅ gh CLI installed on host: gh version 2.xx.x

Test 2: Checking GH_TOKEN environment variable...
✅ GH_TOKEN is set (length: 40 characters)
✅ GH_TOKEN is valid and working

Test 3: Checking for gh config file...
✅ Config file exists: /home/user/.config/gh/hosts.yml

Test 4: Testing authentication in Docker container...
✅ Authentication works in container with GH_TOKEN

==========================================
Summary
==========================================

✅ Method 1 (GH_TOKEN): Ready to use
✅ Method 2 (Mount config): Ready to use
```

## Best Practices

### Security

1. **Never commit tokens to git**
   - Add `.env` to `.gitignore`
   - Use VS Code user settings (not workspace settings)
   - Use GitHub secrets in CI/CD

2. **Use minimal token scopes**
   - Only grant permissions you need
   - Separate tokens for different purposes

3. **Rotate tokens regularly**
   - Set expiration dates
   - Update in settings when rotated

4. **File permissions (if mounting)**
   ```bash
   chmod 700 ~/.config/gh
   chmod 600 ~/.config/gh/hosts.yml
   ```

### Development Workflow

1. **For individual developers:** Use GH_TOKEN in VS Code user settings
2. **For teams:** Document both methods in project README
3. **For CI/CD:** Use GH_TOKEN from secrets/environment
4. **For public repos:** Include example devcontainer.json with clear setup instructions

### Team Configuration

Create `.devcontainer/README.md` in your project:

```markdown
# Dev Container Setup

## GitHub CLI Authentication

Choose one method:

### Method A: Environment Variable (Recommended)
1. Create GitHub PAT: https://github.com/settings/tokens
2. Add to VS Code user settings:
   - Open settings JSON
   - Add GH_TOKEN to terminal.integrated.env.*

### Method B: Mount Configuration
1. Run: gh auth login --insecure-storage
2. Rebuild container

See https://github.com/your-org/gh-auth-guide for details.
```

## Troubleshooting

### "gh not authenticated" in container

**Check 1: Environment variable**
```bash
echo $GH_TOKEN
```
If empty, set in VS Code settings or shell profile.

**Check 2: Mounted configuration**
```bash
ls ~/.config/gh/hosts.yml
cat ~/.config/gh/hosts.yml
```
If missing, run `gh auth login --insecure-storage` on host.

**Check 3: Token validity**
```bash
curl -H "Authorization: token $GH_TOKEN" https://api.github.com/user
```
Should return user info, not 401 error.

### VS Code not passing environment variables

- Restart VS Code after changing settings
- Check user settings (not workspace settings)
- Ensure no typos in variable names
- Try setting in shell profile as backup:
  ```bash
  # ~/.bashrc or ~/.zshrc
  export GH_TOKEN=ghp_your_token_here
  ```

### Permission errors with mounted config

```bash
# On host
chmod 700 ~/.config/gh
chmod 600 ~/.config/gh/hosts.yml

# If using non-root container user, ensure UID matches
id -u  # Check UID
```

### "keyring error" in container

Modern gh uses system keyrings which don't work in containers. Use:
- `GH_TOKEN` environment variable (preferred)
- `gh auth login --insecure-storage` (file-based)

### Cross-platform path issues

Use both HOME and USERPROFILE in mounts:
```json
"source=${localEnv:HOME}${localEnv:USERPROFILE}/.config/gh"
```
One will be empty, one will be populated depending on OS.

## Important Clarifications

### About the DevContainers Feature

The official feature `ghcr.io/devcontainers/features/github-cli:1`:
- ✅ Installs gh CLI
- ✅ Auto-detects latest version
- ✅ Installs dependencies
- ❌ Does NOT handle authentication

**Authentication must be configured separately using one of the methods above.**

### About VS Code Credential Sharing

VS Code automatically shares:
- ✅ Git credentials (via SSH agent forwarding)
- ✅ `.gitconfig` file
- ❌ gh CLI authentication

**gh CLI authentication is separate and must be configured explicitly.**

## Key Takeaways

1. **Use `GH_TOKEN` as primary method** - Most reliable and cross-platform
2. **Store in VS Code user settings** - Secure and persistent
3. **Include verification in postCreateCommand** - Catch issues early
4. **Support multiple methods** - Flexibility for team members
5. **Document clearly** - Make setup easy for contributors

## Additional Resources

- [GitHub CLI Manual](https://cli.github.com/manual/)
- [Dev Containers Specification](https://containers.dev/)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Creating Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

## Files in This Repository

```
gh-auth-dev-containers/
├── README.md                          # This file
├── notes.md                           # Research notes and findings
├── test-auth.sh                       # Authentication validation script
└── examples/
    ├── method1-env-var/               # GH_TOKEN approach
    │   ├── .devcontainer/devcontainer.json
    │   └── README.md
    ├── method2-mount-file/            # Mount config approach
    │   ├── .devcontainer/devcontainer.json
    │   └── README.md
    ├── method3-feature-only/          # Manual auth approach
    │   ├── .devcontainer/devcontainer.json
    │   └── README.md
    └── method4-recommended/           # Hybrid approach ⭐
        ├── .devcontainer/devcontainer.json
        ├── .devcontainer/verify-auth.sh
        └── README.md
```

## License

This research and examples are provided as-is for educational and reference purposes.

---

**Questions or Issues?** Open an issue or contribute improvements!
