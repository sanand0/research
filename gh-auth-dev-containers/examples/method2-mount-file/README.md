# Method 2: Mount hosts.yml File

## Overview
This method mounts the GitHub CLI configuration directory from the host into the container.

## Pros
- ✅ Uses existing gh authentication from host
- ✅ No token management needed
- ✅ Cross-platform with `${localEnv}` variables

## Cons
- ❌ **Requires `--insecure-storage` on host** (gh v2.24.0+)
- ❌ Doesn't work with keyring-based auth
- ❌ File permissions can be tricky
- ❌ Not ideal for multi-user setups

## Setup Instructions

### 1. Configure gh on host with insecure storage

**First time or if using keyring:**
```bash
# This stores credentials in plain text at ~/.config/gh/hosts.yml
gh auth login --insecure-storage
```

**If already authenticated with keyring:**
```bash
# Re-authenticate with file-based storage
gh auth logout
gh auth login --insecure-storage
```

### 2. Verify the file exists
```bash
# Linux/macOS
cat ~/.config/gh/hosts.yml

# Windows
type %USERPROFILE%\.config\gh\hosts.yml
```

### 3. Open in dev container
The configuration will be mounted automatically.

### 4. Verify inside container
```bash
gh auth status
```

## Cross-Platform Notes

The mount path uses both `${localEnv:HOME}` (Linux/macOS) and `${localEnv:USERPROFILE}` (Windows):
- On Linux/macOS: Expands to `$HOME/.config/gh`
- On Windows: Expands to `%USERPROFILE%/.config/gh`

## Security Considerations

⚠️ **Important:** This method stores credentials in plain text on the host system.

- Only use on trusted development machines
- Ensure file has restrictive permissions (600)
- Consider method 1 (GH_TOKEN) for shared or less secure environments
- The mount is read-only in production; remove `,consistency=cached` for stricter security

## Troubleshooting

**"gh not authenticated" in container:**
1. Verify host authentication: `gh auth status`
2. Check file exists: `ls ~/.config/gh/hosts.yml`
3. Ensure you used `--insecure-storage` flag
4. Rebuild container after host re-authentication

**Permission errors:**
- On Linux: `chmod 600 ~/.config/gh/hosts.yml`
- May need to match UID/GID in container

**Keyring error:**
- You're using keyring storage instead of file storage
- Re-run: `gh auth login --insecure-storage`
