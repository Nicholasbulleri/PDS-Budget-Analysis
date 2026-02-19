# Teams Call Recaps - Extracting Items Tied to Your Name

This script extracts all items, action items, and mentions tied to your name from Microsoft Teams call recaps. **It only processes meetings from the previous day and current day that have AI recaps enabled.**

## Features

- **Date Range**: Only processes meetings from **previous day and current day**
- **AI Recap Filter**: Only processes meetings that have **AI recaps/transcripts available**
- **Meeting Transcripts**: Searches Teams meeting transcripts for mentions of your name
- **Action Items**: Extracts action items and tasks assigned to you
- **OneDrive Transcripts**: Finds transcript files in your OneDrive (filtered to date range)
- **Comprehensive Report**: Generates both JSON and Markdown reports

## Prerequisites

1. **Azure AD Authentication**: You need to be logged into Azure AD (same as your JLL account)
2. **Microsoft Graph API Permissions**: The script requires the following permissions:
   - `Calendars.Read` - To read your calendar/meetings
   - `Chat.Read` - To read Teams chat messages
   - `Files.Read` - To search OneDrive for transcripts
   - `OnlineMeetings.Read` - To access meeting transcripts

## Installation

The required packages are already in `requirements.txt`:
- `azure-identity` - For Azure AD authentication
- `requests` - For HTTP requests to Microsoft Graph API
- `python-dotenv` - For environment variables

If you need to install them:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python3 get_teams_call_recaps.py
```

The script will:
1. Authenticate using Azure AD (may open browser for first-time login)
2. Search Teams meetings from **previous day and current day only**
3. Filter to only meetings that have **AI recaps/transcripts available**
4. Extract action items and mentions tied to your name from those recaps
5. Generate reports:
   - `TEAMS_CALL_RECAPS_ITEMS.json` - Detailed JSON data
   - `TEAMS_CALL_RECAPS_ITEMS.md` - Human-readable summary report

### Custom User Name

You can set a custom user name via environment variable:

```bash
export USER_NAME="your.name@company.com"
python3 get_teams_call_recaps.py
```

Or create a `.env` file:
```
USER_NAME=your.name@company.com
```

## Authentication

The script uses Azure AD authentication, similar to your Databricks connection:

1. **First Run**: Will open a browser window for you to sign in
2. **Subsequent Runs**: Uses cached Azure CLI credentials if available
3. **Azure CLI**: If you've run `az login`, it will use those credentials automatically

## Output Files

### TEAMS_CALL_RECAPS_ITEMS.json

Contains detailed data in JSON format:
- All meetings found
- Action items with full context
- Chat mentions
- Transcript files found
- Summary statistics

### TEAMS_CALL_RECAPS_ITEMS.md

Human-readable Markdown report with:
- Summary statistics
- Action items organized by meeting
- Chat mentions
- Links to meetings and transcript files

## Name Variations

The script automatically searches for multiple variations of your name:
- Full email address (e.g., `nicholas.bulleri@jll.com`)
- First name (e.g., `nicholas`, `Nicholas`)
- Last name (e.g., `bulleri`, `Bulleri`)
- Full name (e.g., `Nicholas Bulleri`)
- Common nicknames (e.g., `nick`)

## Limitations

1. **Transcript Availability**: Not all Teams meetings have transcripts. Only meetings where transcription was enabled will have transcripts available.

2. **Permissions**: You can only access:
   - Meetings you organized or were invited to
   - Chat messages in chats you're part of
   - Transcript files in your OneDrive

3. **Time Range**: Only searches **previous day and current day**. This is hardcoded to focus on recent meetings with AI recaps.

4. **API Rate Limits**: Microsoft Graph API has rate limits. The script processes meetings in batches to avoid hitting limits.

## Troubleshooting

### Authentication Errors

If you get authentication errors:
1. Make sure you're logged into Azure CLI: `az login`
2. Or the script will prompt you to sign in via browser

### Permission Errors

If you get permission denied errors:
1. You may need to grant additional permissions in Azure AD
2. Contact your IT administrator to ensure you have the required Graph API permissions

### No Transcripts Found

If no transcripts are found:
1. Transcripts are only available for meetings where transcription was enabled
2. Check if your organization allows transcript downloads
3. Some meetings may have transcripts stored in SharePoint (channel meetings) which require different access

## Advanced Usage

### Modify Search Time Range

Edit the script and change the date range in the `get_all_items_from_teams` function:

```python
# Change these lines to adjust date range
start_date = (datetime.now() - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)  # 2 days ago
end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)  # Today
```

### Customize Name Variations

Edit the `user_name_variations` list in the `get_all_items_from_teams` function to add more name variations.

### Filter Specific Meetings

You can modify the script to filter meetings by:
- Subject keywords
- Organizer
- Date range
- Meeting type

## Notes

- The script respects Microsoft Graph API rate limits
- Large numbers of meetings may take several minutes to process
- Transcript content is processed locally (not sent to external services)
- All data is saved locally in the output files

## Support

For issues or questions:
1. Check the error messages in the console output
2. Verify your Azure AD authentication is working
3. Ensure you have the required Microsoft Graph API permissions

