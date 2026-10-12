# Credentials Setup Guide

This guide explains how to securely configure API credentials for the cloud-api-management skill.

## Security Principles

1. **Never hardcode credentials** in scripts or configuration files
2. **Never commit credentials** to version control
3. **Use environment variables** for all secrets
4. **Restrict file permissions** on credential files
5. **Rotate keys regularly** and after any suspected exposure

## Quick Setup

### 1. Create Credentials File

```bash
mkdir -p ~/.config
touch ~/.config/cloud-api-keys.env
chmod 600 ~/.config/cloud-api-keys.env
```

### 2. Add Your Credentials

Edit `~/.config/cloud-api-keys.env`:

```bash
# ======================
# CLOUDFLARE
# ======================
# Get from: https://dash.cloudflare.com/profile/api-tokens
export CLOUDFLARE_API_KEY="your-api-token-here"

# Get from: Cloudflare Dashboard > Account Home (top-right dropdown) > Account ID
export CLOUDFLARE_ACCOUNT_ID="your-account-id"

# Get from: Domain dashboard > Overview > Zone ID (right sidebar)
export CLOUDFLARE_ZONE_ID="your-zone-id"

# ======================
# CONTABO OBJECT STORAGE
# ======================
# Get from: Contabo Customer Panel > Object Storage > S3 Credentials
export CONTABO_ACCESS_KEY="your-access-key"
export CONTABO_SECRET_KEY="your-secret-key"
export CONTABO_ENDPOINT="https://sin1.contabostorage.com"  # Adjust region
export CONTABO_BUCKET="your-bucket-name"

# ======================
# GITHUB
# ======================
# Get from: https://github.com/settings/tokens
# Create a Personal Access Token (classic) with required scopes
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# ======================
# PERPLEXITY
# ======================
# Get from: https://www.perplexity.ai/settings/api
export PERPLEXITY_API_KEY="pplx-xxxxxxxxxxxx"

# ======================
# CONTEXT7
# ======================
# Get from: https://context7.com/api
export CONTEXT7_API_KEY="ctx7sk-xxxxxxxxxxxx"
```

### 3. Load Credentials

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
# Load cloud API credentials
if [ -f ~/.config/cloud-api-keys.env ]; then
    source ~/.config/cloud-api-keys.env
fi
```

Or load manually before use:

```bash
source ~/.config/cloud-api-keys.env
```

## Service-Specific Setup

### Cloudflare API Token

1. Go to [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens)
2. Click "Create Token"
3. Choose a template or create custom token with permissions:
   - **Zone:DNS:Edit** - For DNS management
   - **Zone:Zone:Read** - For zone information
   - **Zone:Firewall Services:Edit** - For firewall rules
   - **Zone:Cache Purge:Purge** - For cache management
   - **Account:Workers Scripts:Edit** - For Workers management
4. Restrict to specific zones if possible

### Contabo Object Storage

1. Log into [Contabo Customer Panel](https://my.contabo.com)
2. Navigate to Object Storage section
3. Create or view S3 credentials
4. Note the endpoint URL for your region:
   - Singapore: `https://sin1.contabostorage.com`
   - Europe: `https://eu2.contabostorage.com`
   - US: `https://usc1.contabostorage.com`

### GitHub Personal Access Token

1. Go to [GitHub Token Settings](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes based on needs:
   - **repo** - Full repository access
   - **workflow** - GitHub Actions
   - **admin:repo_hook** - Webhooks
   - **delete_repo** - Repository deletion (use cautiously)
4. Copy token immediately (shown only once)

### Perplexity API

1. Go to [Perplexity Settings](https://www.perplexity.ai/settings/api)
2. Generate an API key
3. Note: API access requires a Perplexity Pro subscription

## Verification

Test each service after setup:

```bash
# Test Cloudflare
python3 scripts/cloudflare_api.py zones list

# Test Contabo
python3 scripts/contabo_storage.py buckets

# Test GitHub
python3 scripts/github_api.py user me

# Test Perplexity
python3 scripts/perplexity_search.py "test query"
```

## Troubleshooting

### "Environment variable not set"
- Ensure you've sourced the credentials file
- Check for typos in variable names
- Verify the file has correct permissions

### "Authentication failed"
- Verify the API key is correct
- Check if the key has expired
- Ensure required permissions are granted

### "Permission denied" on credentials file
```bash
chmod 600 ~/.config/cloud-api-keys.env
```

## Security Best Practices

1. **Use separate API tokens** for different projects when possible
2. **Set expiration dates** on tokens where supported
3. **Review token permissions** regularly
4. **Monitor API usage** through provider dashboards
5. **Revoke compromised tokens** immediately
6. **Never share credentials** via chat, email, or tickets

## Credential Rotation

When rotating credentials:

1. Generate new credential
2. Update `~/.config/cloud-api-keys.env`
3. Source the updated file
4. Test all affected services
5. Revoke old credential
