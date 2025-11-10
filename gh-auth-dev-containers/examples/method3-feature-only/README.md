# Method 3: Feature Only with Manual Authentication

## Overview
This method only installs gh CLI via the devcontainers feature. Authentication is performed manually inside the container.

## Pros
- ✅ Simple configuration
- ✅ No host setup required
- ✅ Works on any platform
- ✅ Each developer authenticates independently

## Cons
- ❌ Must re-authenticate after container rebuilds
- ❌ Not automated
- ❌ Poor developer experience
- ❌ Not suitable for CI/CD

## Setup Instructions

### 1. Open in dev container
The container will have gh installed but not authenticated.

### 2. Authenticate inside the container
```bash
gh auth login --insecure-storage
```

**Why `--insecure-storage`?**
Containers typically don't have system keyrings (gnome-keyring, Keychain, etc.) configured. The `--insecure-storage` flag stores credentials in `~/.config/gh/hosts.yml` instead.

### 3. Follow the prompts
- Choose authentication method (web browser or token)
- Select protocols and preferences
- Complete authentication

### 4. Verify
```bash
gh auth status
```

## Limitations

**Container Rebuilds:**
Authentication is lost when the container is rebuilt. You'll need to re-authenticate.

**Persistence:**
To persist authentication across rebuilds, you would need to:
1. Use named volumes (complex)
2. Mount configuration from host (Method 2)
3. Use environment variable (Method 1)

## When to Use This Method

This method is suitable for:
- Quick testing or demos
- Learning/exploring gh CLI
- One-off tasks

This method is NOT suitable for:
- Regular development workflows
- Team projects
- CI/CD pipelines
- Any scenario requiring automation

## Recommendation

For actual development, use Method 1 (GH_TOKEN) or Method 4 (Recommended combined approach).
