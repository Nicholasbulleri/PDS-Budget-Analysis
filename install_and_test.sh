#!/bin/bash
# Script to install dependencies and test Databricks connection

echo "=========================================="
echo "JLL EDP Databricks Connection Setup"
echo "=========================================="
echo ""

# Check if Xcode Command Line Tools are installed
if ! xcode-select -p &>/dev/null; then
    echo "⚠ Xcode Command Line Tools are required"
    echo ""
    echo "Please run this command to install them:"
    echo "  xcode-select --install"
    echo ""
    echo "This will open a dialog - click 'Install' and wait for completion."
    echo "Then run this script again."
    exit 1
fi

echo "✓ Xcode Command Line Tools found"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
echo "-----------------------------------"
pip3 install --user -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ Failed to install dependencies"
    echo "Try running: pip3 install --user python-dotenv databricks-sql-connector azure-identity"
    exit 1
fi

echo ""
echo "✓ Dependencies installed"
echo ""

# Run test
echo "=========================================="
echo "Testing Connection"
echo "=========================================="
echo ""

python3 test_connection.py


