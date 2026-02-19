# Installing Azure CLI on macOS

Azure CLI is not currently installed. Here are your options:

## Option 1: Install via Homebrew (Recommended)

If you have Homebrew installed:
```bash
brew install azure-cli
```

If you don't have Homebrew, install it first:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install Azure CLI:
```bash
brew install azure-cli
```

## Option 2: Install via Direct Download

1. Download the installer from Microsoft:
   https://aka.ms/InstallAzureCLIMacOS

2. Run the downloaded `.pkg` file

3. Follow the installation wizard

## Option 3: Install via pip (Python)

If you have Python installed:
```bash
pip3 install azure-cli
```

## After Installation

Once Azure CLI is installed, run:
```bash
az login
```

This will open a browser for you to sign in with your JLL credentials. After that, your credentials will be cached and you won't need to sign in via browser for future queries.

## Verify Installation

Check if Azure CLI is installed:
```bash
az --version
```

## Alternative: Use Service Principal

If you prefer not to install Azure CLI, you can use a Service Principal instead. Contact your IT team to get:
- Azure Tenant ID
- Azure Client ID  
- Azure Client Secret

Then add them to your `.env` file.

