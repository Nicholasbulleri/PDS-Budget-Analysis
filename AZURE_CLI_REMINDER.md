# Azure CLI Login Reminder

## ⏰ Reminder Date: May 18, 2025

Your Azure CLI login session will expire in approximately **90 days** from today (February 17, 2025).

## When to Re-login

You'll need to run `az login` again when:
- Your session expires (typically after 90 days)
- You get authentication errors when running queries
- You see "Please run 'az login' to setup account" errors

## How to Re-login

Run this command:
```bash
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
az login --use-device-code
```

Or if you prefer browser login:
```bash
az login
```

## Check Current Login Status

To verify you're still logged in:
```bash
az account show
```

If you see account information, you're still logged in. If you see an error, you need to login again.

---

**Last login:** February 17, 2025  
**Next reminder:** May 18, 2025

