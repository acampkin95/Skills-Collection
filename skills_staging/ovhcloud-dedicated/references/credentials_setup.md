# OVHcloud API Credentials Setup

## Overview

The OVH API uses a three-key authentication system:
- **Application Key (AK)** — Identifies your application
- **Application Secret (AS)** — Signs requests (never transmitted)
- **Consumer Key (CK)** — Authorises access to a specific account with defined scopes

## Step 1: Create Application Credentials

Visit the token creation page for your region:

| Region | URL |
|--------|-----|
| Europe | https://eu.api.ovh.com/createToken/ |
| USA | https://api.us.ovhcloud.com/createToken/ |
| Canada | https://ca.api.ovh.com/createToken/ |

Fill in:
- **Application name**: e.g. "Server Management CLI"
- **Application description**: e.g. "Dedicated server admin via ovh_server.py"
- **Validity**: Choose unlimited for persistent tools, or time-limited for one-off tasks
- **Rights**: Add the API paths and methods you need

### Recommended Scopes

**Full dedicated server admin:**
```
GET    /dedicated/server/*
PUT    /dedicated/server/*
POST   /dedicated/server/*
DELETE /dedicated/server/*
GET    /ip/*
PUT    /ip/*
POST   /ip/*
DELETE /ip/*
```

**Read-only monitoring:**
```
GET /dedicated/server/*
GET /ip/*
```

After submission, you'll receive all three keys on screen. **Save them immediately** — the Application Secret and Consumer Key are shown only once.

## Step 2: Configure the Client

### Option A: Config File (recommended)

Create `~/.config/ovh.conf`:

```ini
[default]
endpoint=ovh-eu

[ovh-eu]
application_key=YOUR_APPLICATION_KEY
application_secret=YOUR_APPLICATION_SECRET
consumer_key=YOUR_CONSUMER_KEY
```

Secure it:
```bash
chmod 600 ~/.config/ovh.conf
```

The `python-ovh` library also checks `./ovh.conf` in the current directory and `/etc/ovh.conf` system-wide.

### Option B: Environment Variables

```bash
export OVH_ENDPOINT=ovh-eu
export OVH_APPLICATION_KEY=YOUR_AK
export OVH_APPLICATION_SECRET=YOUR_AS
export OVH_CONSUMER_KEY=YOUR_CK
```

Add to `~/.bashrc` or `~/.zshrc` for persistence. Environment variables take precedence over config files.

### Option C: Direct in Code (NOT recommended)

```python
import ovh
client = ovh.Client(
    endpoint='ovh-eu',
    application_key='AK',
    application_secret='AS',
    consumer_key='CK',
)
```

Only use this for throwaway scripts. Never commit credentials to version control.

## Step 3: Verify

```bash
python3 -c "
import ovh
c = ovh.Client()
me = c.get('/me')
print(f'Authenticated as: {me[\"firstname\"]} {me[\"lastname\"]} ({me[\"nichandle\"]})')
"
```

## OAuth2 Alternative

OVH also supports OAuth2 service accounts:

1. Create a service account at https://help.ovhcloud.com/csm/en-manage-service-account
2. Get `client_id` and `client_secret`
3. Configure:

```ini
[default]
endpoint=ovh-eu

[ovh-eu]
client_id=YOUR_CLIENT_ID
client_secret=YOUR_CLIENT_SECRET
```

OAuth2 is better for automated pipelines where you don't want user-scoped consumer keys.

## Key Rotation

If credentials are exposed:
1. Revoke the consumer key immediately via the OVH Control Panel → My Account → API Keys
2. Create a new token at the createToken URL
3. Update your config file or environment variables
4. Audit recent API activity in the Control Panel

## Multiple Accounts / Regions

You can configure multiple endpoints in the same config file:

```ini
[default]
endpoint=ovh-eu

[ovh-eu]
application_key=EU_AK
application_secret=EU_AS
consumer_key=EU_CK

[ovh-ca]
application_key=CA_AK
application_secret=CA_AS
consumer_key=CA_CK
```

Switch at runtime:
```python
client = ovh.Client(endpoint='ovh-ca')
```

Or via environment:
```bash
OVH_ENDPOINT=ovh-ca python3 scripts/ovh_server.py list
```
