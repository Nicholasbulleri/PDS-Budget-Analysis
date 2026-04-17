#!/bin/bash
# Script to check if Azure CLI login is still valid

export PATH="$HOME/Library/Python/3.9/bin:$PATH"

echo "Checking Azure CLI login status..."
echo ""

if az account show &> /dev/null; then
    echo "✓ Azure CLI is logged in"
    echo ""
    az account show --query "{Name:name, User:user.name}" -o table
    echo ""
    echo "You're all set! No need to login again."
else
    echo "✗ Azure CLI login expired or not found"
    echo ""
    echo "Please run:"
    echo "  export PATH=\"\$HOME/Library/Python/3.9/bin:\$PATH\""
    echo "  az login --use-device-code"
fi

