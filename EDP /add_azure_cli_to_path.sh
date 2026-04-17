#!/bin/bash
# Add Azure CLI to PATH permanently

AZURE_CLI_PATH="$HOME/Library/Python/3.9/bin"

# Check if already in PATH
if [[ ":$PATH:" != *":$AZURE_CLI_PATH:"* ]]; then
    # Add to .zshrc (since you're using zsh)
    echo "" >> ~/.zshrc
    echo "# Azure CLI" >> ~/.zshrc
    echo "export PATH=\"\$HOME/Library/Python/3.9/bin:\$PATH\"" >> ~/.zshrc
    echo "✓ Added Azure CLI to PATH in ~/.zshrc"
    echo "Run: source ~/.zshrc (or restart terminal)"
else
    echo "Azure CLI is already in PATH"
fi

