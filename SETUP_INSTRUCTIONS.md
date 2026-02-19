# Setup Instructions for Testing Databricks Connection

## Step 1: Install Xcode Command Line Tools (Required)

Your system needs Xcode Command Line Tools to run Python packages. Install them:

```bash
xcode-select --install
```

This will open a dialog - click "Install" and wait for it to complete (may take 10-15 minutes).

**Alternative:** If you have Xcode installed, you can enable command line tools:
```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
```

## Step 2: Install Python Dependencies

Once command line tools are installed, install the required packages:

```bash
pip3 install -r requirements.txt
```

Or install individually:
```bash
pip3 install python-dotenv databricks-sql-connector azure-identity
```

## Step 3: Test the Connection

Run the test script:

```bash
python3 test_connection.py
```

Or test directly:

```bash
python3 edp_connection.py
```

## What to Expect

When you run the connection test:

1. **First time:** A browser window will open
2. **Sign in:** Use your JLL Azure AD credentials
3. **Success:** You'll see connection details and be ready to query

## Troubleshooting

### "xcode-select: note: No developer tools were found"
- **Solution:** Run `xcode-select --install` and complete the installation

### "Module not found" errors
- **Solution:** Install dependencies: `pip3 install -r requirements.txt`

### "Connection timeout"
- **Check:** Is your SQL Warehouse running in Databricks?
- **Check:** Are you connected to VPN (if required)?

### "Authentication failed"
- **Check:** Did you sign in successfully in the browser?
- **Check:** Are your JLL credentials correct?

### Browser doesn't open
- **Try:** Manually open a browser and sign in to Azure AD
- **Check:** Pop-up blockers may be preventing the browser from opening

## Quick Test

After installing dependencies, you can quickly test with:

```bash
python3 -c "from edp_connection import test_connection; test_connection()"
```


