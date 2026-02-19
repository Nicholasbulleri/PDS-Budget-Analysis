#!/bin/bash
# Script to set up Azure CLI for cached authentication

echo "=========================================="
echo "Setting up Azure CLI for Databricks"
echo "=========================================="
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Azure CLI is not installed."
    echo ""
    echo "Install it with:"
    echo "  brew install azure-cli"
    echo ""
    echo "Or download from: https://aka.ms/InstallAzureCLIMacOS"
    exit 1
fi

echo "✓ Azure CLI is installed"
echo ""

# Check if already logged in
if az account show &> /dev/null; then
    echo "You are already logged in to Azure CLI."
    echo ""
    echo "Current account:"
    az account show --query "{Name:name, User:user.name}" -o table
    echo ""
    echo "If this is the correct account, you're all set!"
    echo "If you need to switch accounts, run: az login"
else
    echo "Logging in to Azure CLI..."
    echo "This will open a browser for you to sign in with your JLL credentials."
    echo ""
    az login
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Successfully logged in!"
        echo ""
        echo "Your credentials are now cached."
        echo "You can run Databricks queries without browser login."
    else
        echo ""
        echo "✗ Login failed. Please try again."
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. Test your connection:"
echo "   python3 test_connection.py"
echo ""
echo "2. Run queries without browser login:"
echo "   python3 run_query.py \"SELECT COUNT(*) FROM your_table\""
echo ""
echo "Note: Your Azure CLI credentials are cached and will be reused"
echo "      automatically. You only need to run 'az login' again if"
echo "      your session expires (typically after 90 days)."

