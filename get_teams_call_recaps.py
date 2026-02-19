#!/usr/bin/env python3
"""
Extract all items tied to your name from Microsoft Teams call recaps/transcripts
Uses Microsoft Graph API to access Teams meeting transcripts and recordings
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict

# Load environment variables
try:
    from dotenv import load_dotenv
    try:
        load_dotenv()
    except (PermissionError, FileNotFoundError):
        # .env file may not exist or may not be accessible - that's okay
        pass
except ImportError:
    # dotenv not installed - that's okay, we'll use environment variables directly
    pass

def get_graph_token():
    """Get Microsoft Graph API access token using Azure AD authentication"""
    try:
        from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
        
        # Try DefaultAzureCredential first (uses cached Azure CLI login)
        credential = None
        try:
            credential = DefaultAzureCredential(exclude_visual_studio_code_credential=True, 
                                               exclude_shared_token_cache_credential=True,
                                               exclude_managed_identity_credential=True)
            # Test with Graph API scope
            test_token = credential.get_token("https://graph.microsoft.com/.default")
            print("✓ Using Default Azure Credential (cached Azure CLI login)")
            return test_token.token
        except Exception as e:
            error_msg = str(e)
            if "Operation not permitted" in error_msg or "Permission denied" in error_msg:
                print("⚠ DefaultAzureCredential blocked by permissions, trying Interactive Browser...")
            else:
                print(f"DefaultAzureCredential failed: {error_msg[:100]}")
            credential = None
        
        # Fallback to Interactive Browser
        if not credential:
            try:
                print("\nUsing Interactive Browser authentication...")
                print("A browser window will open for you to sign in.")
                credential = InteractiveBrowserCredential()
                token_response = credential.get_token("https://graph.microsoft.com/.default")
                print("✓ Authentication successful via browser")
                return token_response.token
            except Exception as e:
                error_msg = str(e)
                if "Operation not permitted" in error_msg or "Permission denied" in error_msg:
                    print("\n✗ Permission denied error during authentication.")
                    print("\nTroubleshooting steps:")
                    print("1. Make sure you have network access enabled")
                    print("2. Try running: az login (if Azure CLI is installed)")
                    print("3. Check if your organization allows browser-based authentication")
                    print("4. You may need to run this script outside of restricted environments")
                else:
                    print(f"Interactive Browser credential failed: {error_msg[:200]}")
                raise
        
    except ImportError:
        print("Error: azure-identity not installed.")
        print("Install with: pip install azure-identity")
        raise
    except Exception as e:
        print(f"\nAuthentication error: {e}")
        print("\nIf you're getting permission errors, try:")
        print("1. Run 'az login' first (if Azure CLI is installed)")
        print("2. Make sure you're not in a restricted/sandboxed environment")
        print("3. Check your network/firewall settings")
        raise

def make_graph_request(token: str, endpoint: str, method: str = "GET", params: Optional[Dict] = None):
    """Make a request to Microsoft Graph API"""
    import requests
    
    base_url = "https://graph.microsoft.com/v1.0"
    url = f"{base_url}{endpoint}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    if method == "GET":
        response = requests.get(url, headers=headers, params=params)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=params)
    else:
        raise ValueError(f"Unsupported method: {method}")
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        raise Exception("Authentication failed. Please re-authenticate.")
    elif response.status_code == 403:
        raise Exception("Permission denied. You may need additional permissions.")
    else:
        error_msg = response.text
        print(f"API Error ({response.status_code}): {error_msg}")
        return None

def get_user_info(token: str):
    """Get current user information"""
    try:
        user_data = make_graph_request(token, "/me")
        return user_data
    except Exception as e:
        print(f"Error getting user info: {e}")
        return None

def get_online_meetings(token: str, start_date: datetime = None, end_date: datetime = None):
    """Get online meetings (Teams calls) for a specific date range"""
    try:
        # Default to previous day and current day
        if start_date is None:
            # Start of previous day
            start_date = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        if end_date is None:
            # End of current day
            end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        start_date_str = start_date.isoformat() + "Z"
        end_date_str = end_date.isoformat() + "Z"
        
        meetings = []
        
        # Method 1: Get calendar events with online meetings
        try:
            params = {
                "$filter": f"start/dateTime ge '{start_date_str}' and end/dateTime le '{end_date_str}'",
                "$select": "id,subject,start,end,organizer,onlineMeeting,webLink,body",
                "$orderby": "start/dateTime desc",
                "$top": 1000
            }
            
            endpoint = "/me/calendar/events"
            response_data = make_graph_request(token, endpoint, params=params)
            
            if response_data and "value" in response_data:
                for event in response_data["value"]:
                    # Include events with online meeting info or Teams links
                    if event.get("onlineMeeting") or "teams.microsoft.com" in str(event.get("webLink", "")):
                        meetings.append(event)
        except Exception as e:
            print(f"   Note: Could not fetch calendar events: {e}")
        
        # Method 2: Get online meetings directly (if available)
        try:
            joined_endpoint = "/me/onlineMeetings"
            joined_params = {
                "$filter": f"startDateTime ge {start_date_str} and endDateTime le {end_date_str}",
                "$top": 1000
            }
            joined_data = make_graph_request(token, joined_endpoint, params=joined_params)
            if joined_data and "value" in joined_data:
                # Merge with existing meetings (avoid duplicates)
                existing_ids = {m.get("id") for m in meetings if m.get("id")}
                for meeting in joined_data["value"]:
                    if meeting.get("id") not in existing_ids:
                        meetings.append(meeting)
        except Exception as e:
            print(f"   Note: Could not fetch online meetings directly: {e}")
        
        # Remove duplicates based on ID
        seen_ids = set()
        unique_meetings = []
        for meeting in meetings:
            meeting_id = meeting.get("id")
            if meeting_id and meeting_id not in seen_ids:
                seen_ids.add(meeting_id)
                unique_meetings.append(meeting)
        
        return unique_meetings
    except Exception as e:
        print(f"Error getting meetings: {e}")
        return []

def has_ai_recap(token: str, meeting_id: str) -> bool:
    """Check if a meeting has AI recap/transcript available"""
    try:
        # Try to get transcript from online meeting
        # Teams AI recaps are typically available as transcripts
        endpoint = f"/me/onlineMeetings/{meeting_id}/transcripts"
        transcripts = make_graph_request(token, endpoint)
        
        if transcripts and "value" in transcripts and len(transcripts["value"]) > 0:
            return True
        
        # Alternative: Check for recordings (which may have AI recaps)
        try:
            recordings_endpoint = f"/me/onlineMeetings/{meeting_id}/recordings"
            recordings = make_graph_request(token, recordings_endpoint)
            
            if recordings and "value" in recordings and len(recordings["value"]) > 0:
                # Check if recording has transcript/recap metadata
                for recording in recordings.get("value", []):
                    # AI recaps might be indicated in recording metadata
                    if recording.get("recordingContentUrl") or recording.get("transcriptionState"):
                        return True
        except:
            pass
        
        return False
    except Exception as e:
        # If we can't check, assume no recap available
        return False

def get_meeting_transcript(token: str, meeting_id: str):
    """Get transcript for a specific meeting"""
    try:
        # Try to get transcript from online meeting
        # Note: Transcripts API may require specific permissions
        endpoint = f"/me/onlineMeetings/{meeting_id}/transcripts"
        transcripts = make_graph_request(token, endpoint)
        
        if transcripts and "value" in transcripts:
            return transcripts["value"]
        
        # Alternative: Try to get from recordings (recordings may contain transcript links)
        try:
            recordings_endpoint = f"/me/onlineMeetings/{meeting_id}/recordings"
            recordings = make_graph_request(token, recordings_endpoint)
            
            if recordings and "value" in recordings:
                return recordings["value"]
        except:
            pass
        
        return []
    except Exception as e:
        # Transcripts may not be available for all meetings
        # This is expected - not all meetings have transcripts enabled
        return []

def get_meeting_transcript_content(token: str, transcript_id: str):
    """Get the actual content of a transcript"""
    try:
        # Get transcript content
        endpoint = f"/me/onlineMeetings/transcripts/{transcript_id}/content"
        content = make_graph_request(token, endpoint)
        return content
    except Exception as e:
        print(f"Error getting transcript content: {e}")
        return None

def search_chat_messages(token: str, user_name_variations: List[str], days_back: int = 90):
    """Search Teams chat messages for mentions"""
    try:
        # Get all chats
        chats = make_graph_request(token, "/me/chats")
        
        if not chats or "value" not in chats:
            return []
        
        mentions = []
        for chat in chats.get("value", []):
            chat_id = chat.get("id")
            if not chat_id:
                continue
            
            # Get messages from this chat
            try:
                messages_endpoint = f"/me/chats/{chat_id}/messages"
                messages = make_graph_request(token, messages_endpoint)
                
                if messages and "value" in messages:
                    for message in messages["value"]:
                        message_body = message.get("body", {}).get("content", "")
                        message_time = message.get("createdDateTime", "")
                        
                        # Check if any name variation is mentioned
                        for name_var in user_name_variations:
                            if name_var.lower() in message_body.lower():
                                mentions.append({
                                    "type": "chat_message",
                                    "chat_id": chat_id,
                                    "message_id": message.get("id"),
                                    "content": message_body,
                                    "time": message_time,
                                    "sender": message.get("from", {}).get("user", {}).get("displayName", "Unknown")
                                })
            except Exception as e:
                # Some chats may not be accessible
                continue
        
        return mentions
    except Exception as e:
        print(f"Error searching chat messages: {e}")
        return []

def extract_action_items(text: str, user_name_variations: List[str]) -> List[Dict]:
    """Extract action items or items tied to user's name from text"""
    action_items = []
    
    # Patterns to identify action items
    action_patterns = [
        r"(?i)(?:{})\s*(?:will|should|needs? to|must|has to|is to|assigned to|responsible for|action:?|todo:?|task:?)"
            .format("|".join([re.escape(name) for name in user_name_variations])),
        r"(?i)(?:action|todo|task|follow.?up|next steps?|assign|responsibility).*?(?:{})"
            .format("|".join([re.escape(name) for name in user_name_variations])),
        r"(?i)(?:{})\s*:?\s*([^\.\n]+(?:\.|$))"
            .format("|".join([re.escape(name) for name in user_name_variations])),
    ]
    
    # Split text into sentences
    sentences = re.split(r'[.!?]\s+', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Check if sentence contains user name
        contains_name = any(name.lower() in sentence.lower() for name in user_name_variations)
        
        if contains_name:
            # Check for action item patterns
            for pattern in action_patterns:
                matches = re.finditer(pattern, sentence)
                for match in matches:
                    action_items.append({
                        "text": sentence,
                        "matched_pattern": pattern,
                        "context": sentence[:200]  # First 200 chars for context
                    })
                    break  # Only add once per sentence
    
    return action_items

def search_onedrive_for_transcripts(token: str, user_name_variations: List[str]):
    """Search OneDrive for Teams transcript files"""
    try:
        # Search for transcript files in OneDrive
        # Teams transcripts are typically in Recordings folder
        transcript_files = []
        
        # Method 1: Search in Recordings folder (common location for Teams transcripts)
        try:
            recordings_endpoint = "/me/drive/root:/Recordings:/children"
            recordings = make_graph_request(token, recordings_endpoint)
            
            if recordings and "value" in recordings:
                for item in recordings.get("value", []):
                    file_name = item.get("name", "")
                    if any(ext in file_name.lower() for ext in [".vtt", ".txt", ".docx", ".transcript", ".srt"]):
                        transcript_files.append(item)
        except:
            pass
        
        # Method 2: General search
        try:
            search_query = "transcript OR recording OR recap"
            endpoint = f"/me/drive/search(q='{search_query}')"
            results = make_graph_request(token, endpoint)
            
            if results and "value" in results:
                for item in results.get("value", []):
                    file_name = item.get("name", "")
                    if any(ext in file_name.lower() for ext in [".vtt", ".txt", ".docx", ".transcript", ".srt"]):
                        # Avoid duplicates
                        if not any(f.get("id") == item.get("id") for f in transcript_files):
                            transcript_files.append(item)
        except:
            pass
        
        return transcript_files
    except Exception as e:
        print(f"Error searching OneDrive: {e}")
        return []

def get_all_items_from_teams(token: str, user_name: str = "nicholas.bulleri"):
    """Main function to get all items tied to user's name from Teams call recaps
    Only processes meetings from previous and current day that have AI recaps"""
    print("=" * 80)
    print("Teams Call Recaps - Extracting Items for Your Name")
    print("Date Range: Previous Day + Current Day Only")
    print("Filter: Only Meetings with AI Recaps")
    print("=" * 80)
    
    # Get user info
    print("\n1. Getting user information...")
    user_info = get_user_info(token)
    if user_info:
        print(f"   ✓ User: {user_info.get('displayName', 'Unknown')} ({user_info.get('userPrincipalName', 'Unknown')})")
        # Use actual user name if available
        if user_info.get('userPrincipalName'):
            user_name = user_info.get('userPrincipalName', user_name)
    
    # Create name variations
    name_parts = user_name.split('.')
    first_name = name_parts[0].capitalize() if name_parts else ""
    last_name = name_parts[1].capitalize() if len(name_parts) > 1 else ""
    full_name = f"{first_name} {last_name}" if last_name else first_name
    
    user_name_variations = [
        user_name,
        user_name.lower(),
        user_name.upper(),
        first_name,
        first_name.lower(),
        last_name,
        last_name.lower(),
        full_name,
        full_name.lower(),
        f"{first_name} {last_name}",
        f"{first_name}.{last_name}",
        "nicholas",
        "nick",
        "bulleri"
    ]
    
    print(f"\n2. Searching for name variations: {', '.join(set(user_name_variations[:5]))}...")
    
    # Get meetings from previous day and current day only
    print("\n3. Fetching Teams meetings (previous and current day only)...")
    start_date = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    print(f"   Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    meetings = get_online_meetings(token, start_date=start_date, end_date=end_date)
    print(f"   ✓ Found {len(meetings)} meetings in date range")
    
    all_items = {
        "user_name": user_name,
        "name_variations": list(set(user_name_variations)),
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "meetings": [],
        "action_items": [],
        "chat_mentions": [],
        "transcript_files": [],
        "summary": {
            "total_meetings_in_range": len(meetings),
            "meetings_with_ai_recaps": 0,
            "meetings_with_transcripts": 0,
            "total_action_items": 0,
            "total_chat_mentions": 0
        }
    }
    
    # Filter meetings to only those with AI recaps
    print("\n4. Checking which meetings have AI recaps...")
    meetings_with_recaps = []
    for i, meeting in enumerate(meetings, 1):
        meeting_id = meeting.get("id") or meeting.get("onlineMeeting", {}).get("id")
        subject = meeting.get("subject", "No Subject")
        
        if meeting_id:
            has_recap = has_ai_recap(token, meeting_id)
            if has_recap:
                meetings_with_recaps.append(meeting)
                print(f"   ✓ {subject[:60]}... (has AI recap)")
            else:
                print(f"   ✗ {subject[:60]}... (no AI recap)")
        else:
            print(f"   ✗ {subject[:60]}... (no meeting ID)")
    
    print(f"\n   Found {len(meetings_with_recaps)} meetings with AI recaps")
    
    # Update summary with count of meetings with recaps
    all_items["summary"]["meetings_with_ai_recaps"] = len(meetings_with_recaps)
    
    if len(meetings_with_recaps) == 0:
        print("\n   ⚠ No meetings with AI recaps found in the date range.")
        print("   This could mean:")
        print("   - No meetings occurred in the previous/current day")
        print("   - Meetings occurred but AI recaps were not enabled")
        print("   - You don't have permission to access the recaps")
    
    # Process only meetings with AI recaps
    print("\n5. Processing meetings with AI recaps for mentions...")
    for i, meeting in enumerate(meetings_with_recaps, 1):
        meeting_id = meeting.get("id") or meeting.get("onlineMeeting", {}).get("id")
        subject = meeting.get("subject", "No Subject")
        start_time = meeting.get("start", {}).get("dateTime", "") or meeting.get("startDateTime", "")
        
        print(f"   [{i}/{len(meetings_with_recaps)}] Processing: {subject[:60]}...")
        
        # Process meeting with AI recap (we already filtered to only meetings with recaps)
        if meeting_id:
            try:
                transcripts = get_meeting_transcript(token, meeting_id)
                if transcripts:
                    all_items["summary"]["meetings_with_transcripts"] += 1
                    
                    # Add meeting to list (since it has recap)
                    all_items["meetings"].append({
                        "meeting_id": meeting_id,
                        "subject": subject,
                        "start_time": start_time,
                        "organizer": meeting.get("organizer", {}).get("emailAddress", {}).get("name", "Unknown") if isinstance(meeting.get("organizer"), dict) else "Unknown",
                        "web_link": meeting.get("webLink", ""),
                        "has_transcript": True
                    })
                    
                    # Process transcript content
                    for transcript in transcripts:
                        transcript_id = transcript.get("id")
                        if transcript_id:
                            try:
                                content = get_meeting_transcript_content(token, transcript_id)
                                if content:
                                    # Extract action items
                                    content_str = str(content)
                                    action_items = extract_action_items(content_str, user_name_variations)
                                    if action_items:
                                        all_items["action_items"].extend([{
                                            **item,
                                            "meeting_id": meeting_id,
                                            "meeting_subject": subject,
                                            "meeting_time": start_time
                                        } for item in action_items])
                            except Exception as e:
                                # Some transcripts may not be accessible
                                print(f"      ⚠ Could not access transcript content: {e}")
                                continue
            except Exception as e:
                # Transcript access may fail for various reasons
                print(f"      ⚠ Error accessing transcript: {e}")
                continue
    
    # Note: Not searching chat messages since we're only focusing on AI recaps
    print("\n6. Skipping chat message search (focusing only on AI recaps)...")
    chat_mentions = []
    all_items["chat_mentions"] = chat_mentions
    all_items["summary"]["total_chat_mentions"] = len(chat_mentions)
    print(f"   ✓ Found {len(chat_mentions)} chat mentions")
    
    # Search OneDrive for transcript files from previous/current day
    print("\n7. Searching OneDrive for recent transcript files...")
    transcript_files = search_onedrive_for_transcripts(token, user_name_variations)
    
    # Filter transcript files to only those from previous/current day
    if transcript_files:
        filtered_files = []
        for file in transcript_files:
            file_created = file.get("createdDateTime") or file.get("lastModifiedDateTime")
            if file_created:
                try:
                    file_date = datetime.fromisoformat(file_created.replace('Z', '+00:00'))
                    if start_date <= file_date <= end_date:
                        filtered_files.append(file)
                except:
                    # If we can't parse date, include it to be safe
                    filtered_files.append(file)
        transcript_files = filtered_files
        print(f"   ✓ Found {len(transcript_files)} transcript files from date range")
    all_items["transcript_files"] = [
        {
            "name": f.get("name"),
            "web_url": f.get("webUrl"),
            "created": f.get("createdDateTime"),
            "modified": f.get("lastModifiedDateTime")
        } for f in transcript_files
    ]
    print(f"   ✓ Found {len(transcript_files)} transcript files")
    
    # Update summary
    all_items["summary"]["total_action_items"] = len(all_items["action_items"])
    
    # Save results
    output_file = "TEAMS_CALL_RECAPS_ITEMS.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Results saved to: {output_file}")
    
    # Create summary report
    create_summary_report(all_items)
    
    return all_items

def create_summary_report(data: Dict):
    """Create a human-readable summary report"""
    report = []
    report.append("# Teams Call Recaps - Items Tied to Your Name\n\n")
    report.append(f"**User:** {data['user_name']}\n\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    report.append("---\n\n")
    
    # Summary
    summary = data['summary']
    date_range = data.get('date_range', {})
    report.append("## Summary\n\n")
    if date_range.get('start') and date_range.get('end'):
        start = datetime.fromisoformat(date_range['start'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(date_range['end'].replace('Z', '+00:00'))
        report.append(f"**Date Range:** {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}\n\n")
    report.append(f"- **Total Meetings in Date Range:** {summary.get('total_meetings_in_range', 0)}\n")
    report.append(f"- **Meetings with AI Recaps:** {summary.get('meetings_with_ai_recaps', 0)}\n")
    report.append(f"- **Meetings Processed:** {summary['meetings_with_transcripts']}\n")
    report.append(f"- **Action Items Found:** {summary['total_action_items']}\n")
    report.append(f"- **Chat Mentions:** {summary['total_chat_mentions']}\n\n")
    report.append("---\n\n")
    
    # Action Items
    if data['action_items']:
        report.append("## Action Items & Items Tied to Your Name\n\n")
        for i, item in enumerate(data['action_items'], 1):
            report.append(f"### Item {i}\n\n")
            report.append(f"**Meeting:** {item.get('meeting_subject', 'Unknown')}\n\n")
            report.append(f"**Time:** {item.get('meeting_time', 'Unknown')}\n\n")
            report.append(f"**Text:** {item.get('text', '')}\n\n")
            report.append(f"**Context:** {item.get('context', '')}\n\n")
            report.append("---\n\n")
    else:
        report.append("## Action Items\n\n")
        report.append("No action items found in meeting transcripts.\n\n")
    
    # Chat Mentions
    if data['chat_mentions']:
        report.append("## Chat Mentions\n\n")
        for i, mention in enumerate(data['chat_mentions'][:20], 1):  # First 20
            report.append(f"### Mention {i}\n\n")
            report.append(f"**From:** {mention.get('sender', 'Unknown')}\n\n")
            report.append(f"**Time:** {mention.get('time', 'Unknown')}\n\n")
            report.append(f"**Content:** {mention.get('content', '')[:500]}...\n\n")
            report.append("---\n\n")
    
    # Meetings
    if data['meetings']:
        report.append("## Meetings Where You Were Mentioned\n\n")
        for meeting in data['meetings']:
            report.append(f"- **{meeting.get('subject', 'No Subject')}**\n")
            report.append(f"  - Time: {meeting.get('start_time', 'Unknown')}\n")
            report.append(f"  - Organizer: {meeting.get('organizer', 'Unknown')}\n")
            if meeting.get('web_link'):
                report.append(f"  - [Meeting Link]({meeting.get('web_link')})\n")
            report.append("\n")
    
    # Transcript Files
    if data['transcript_files']:
        report.append("## Transcript Files Found\n\n")
        for file in data['transcript_files']:
            report.append(f"- **{file.get('name', 'Unknown')}**\n")
            report.append(f"  - Created: {file.get('created', 'Unknown')}\n")
            if file.get('web_url'):
                report.append(f"  - [View File]({file.get('web_url')})\n")
            report.append("\n")
    
    report_file = "TEAMS_CALL_RECAPS_ITEMS.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(''.join(report))
    print(f"✓ Summary report saved to: {report_file}")

def main():
    """Main entry point"""
    try:
        print("Authenticating with Microsoft Graph API...")
        token = get_graph_token()
        print("✓ Authentication successful\n")
        
        # Get user name from environment or use default
        user_name = os.getenv("USER_NAME", "nicholas.bulleri")
        
        # Get all items
        results = get_all_items_from_teams(token, user_name)
        
        print("\n" + "=" * 80)
        print("COMPLETE")
        print("=" * 80)
        print(f"\nSummary:")
        print(f"  - Meetings in date range: {results['summary'].get('total_meetings_in_range', 0)}")
        print(f"  - Meetings with AI recaps: {results['summary'].get('meetings_with_ai_recaps', 0)}")
        print(f"  - Meetings processed: {results['summary'].get('meetings_with_transcripts', 0)}")
        print(f"  - Action items found: {results['summary']['total_action_items']}")
        print(f"  - Chat mentions: {results['summary']['total_chat_mentions']}")
        print(f"\nFiles created:")
        print(f"  - TEAMS_CALL_RECAPS_ITEMS.json (detailed data)")
        print(f"  - TEAMS_CALL_RECAPS_ITEMS.md (summary report)")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

