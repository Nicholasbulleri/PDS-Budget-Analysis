# Troubleshooting Teams Call Recaps Script

## Permission Denied Errors

If you're getting "Permission denied" or "Operation not permitted" errors, here are solutions:

### Solution 1: Use Azure CLI Authentication (Recommended)

1. **Install Azure CLI** (if not already installed):
   ```bash
   brew install azure-cli
   ```

2. **Login to Azure**:
   ```bash
   az login
   ```
   This will open a browser for you to sign in with your JLL account.

3. **Run the script**:
   ```bash
   python3 get_teams_call_recaps.py
   ```
   It should now use your cached Azure CLI credentials.

### Solution 2: Run Outside Restricted Environments

If you're running in a sandboxed or restricted environment:
- Run the script directly in your terminal (not through IDE/sandbox)
- Make sure you have network access
- Check if your organization blocks certain authentication methods

### Solution 3: Check File Permissions

If the script file itself has permission issues:

```bash
# Make sure the script is executable
chmod +x get_teams_call_recaps.py

# Check permissions
ls -la get_teams_call_recaps.py
```

Should show: `-rwxr-xr-x` (executable)

### Solution 4: Use Python Directly

Instead of running the script directly, use Python:

```bash
python3 "/Users/nicholas.bulleri/Cursor Project/get_teams_call_recaps.py"
```

### Solution 5: Check Required Permissions

The script needs these Microsoft Graph API permissions:
- `Calendars.Read` - To read your calendar/meetings
- `OnlineMeetings.Read` - To access meeting transcripts
- `Files.Read` - To search OneDrive for transcripts

If you don't have these permissions, contact your IT administrator.

### Solution 6: Alternative - Use Service Principal

If browser authentication is blocked, you can use a service principal:

1. Get service principal credentials from your IT team:
   - `AZURE_TENANT_ID`
   - `AZURE_CLIENT_ID`
   - `AZURE_CLIENT_SECRET`

2. Set environment variables:
   ```bash
   export AZURE_TENANT_ID="your-tenant-id"
   export AZURE_CLIENT_ID="your-client-id"
   export AZURE_CLIENT_SECRET="your-client-secret"
   ```

3. Run the script - it will use service principal authentication

## Common Error Messages

### "Operation not permitted"
- **Cause**: System blocking authentication
- **Fix**: Use `az login` first, or run outside sandboxed environment

### "No such file or directory"
- **Cause**: Wrong path or not in correct directory
- **Fix**: 
  ```bash
  cd "/Users/nicholas.bulleri/Cursor Project"
  python3 get_teams_call_recaps.py
  ```

### "Authentication failed"
- **Cause**: Invalid credentials or permissions
- **Fix**: Run `az login` to refresh credentials

### "Permission denied" on .env file
- **Cause**: Script trying to read .env file without permission
- **Fix**: This is handled automatically - script will continue without .env

## Still Having Issues?

1. **Check Python version**:
   ```bash
   python3 --version
   ```
   Should be Python 3.7 or higher

2. **Check required packages**:
   ```bash
   pip3 list | grep -E "azure-identity|requests"
   ```

3. **Install missing packages**:
   ```bash
   pip3 install azure-identity requests python-dotenv
   ```

4. **Run with verbose output**:
   The script already provides detailed error messages. Check the output for specific issues.

