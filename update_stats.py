import os
import re
import requests

# Fetch authentication keys securely from GitHub Secrets (Safe for public repos)
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
LIMIT = 10

def get_completed_rooms_from_notion():
    if not NOTION_TOKEN or not DATABASE_ID:
        print("Error: Missing NOTION_TOKEN or NOTION_DATABASE_ID in environment variables.")
        return []

    url = f"https://notion.com{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # Sorts labs by your custom "Completed" date column (Newest first)
    payload = {
        "sorts": [
            {
                "property": "Completed",
                "direction": "descending"
            }
        ],
        "page_size": LIMIT
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"Notion API Error: {response.status_code} - {response.text}")
            return []

        data = response.json()
        rooms = []

        for result in data.get("results", []):
            properties = result.get("properties", {})
            
            # 1. Extract Room Name
            name_title_list = properties.get("Name", {}).get("title", [])
            room_name = ""
            if name_title_list:
                room_name = name_title_list[0].get("text", {}).get("content", "").strip()
            
            # Skip processing if name field is blank
            if not room_name:
                continue

            # 2. Extract Category (Red Team, Blue Team, Purple Team)
            category_select = properties.get("Category", {}).get("select") or {}
            category_name = category_select.get("name", "General")
            
            # Map categories to team emojis
            if "Red Team" in category_name:
                cat_emoji = "🔴"
            elif "Blue Team" in category_name:
                cat_emoji = "🔵"
            elif "Purple Team" in category_name:
                cat_emoji = "🟣"
            else:
                cat_emoji = "🚀"

            # 3. Extract Difficulty (Info, Easy, Medium, Hard, Insane)
            difficulty_select = properties.get("Difficulty", {}).get("select") or {}
            difficulty_name = difficulty_select.get("name", "").lower().strip()
            
            # Map difficulties to color scale emojis
            if "info" in difficulty_name:
                diff_emoji = "⚪ Info"
            elif "easy" in difficulty_name:
                diff_emoji = "🟢 Easy"
            elif "medium" in difficulty_name:
                diff_emoji = "🟡 Medium"
            elif "hard" in difficulty_name:
                diff_emoji = "🟠 Hard"
            elif "insane" in difficulty_name:
                diff_emoji = "🔴 Insane"
            else:
                diff_emoji = "⚙️ Lab"

            # 4. Extract the direct lab URL
            room_url = properties.get("Url", {}).get("url", "")
            
            # Build the clean line item
            metadata = f"— *{category_name}* | `{diff_emoji}`"
            if room_url:
                rooms.append(f"* {cat_emoji} [**{room_name}**]({room_url}) {metadata}")
            else:
                rooms.append(f"* {cat_emoji} **{room_name}** {metadata}")

        print(f"Successfully fetched {len(rooms)} labs from your custom Notion Tracker!")
        return rooms

    except Exception as e:
        print(f"An error occurred accessing Notion: {e}")
        return []

def update_readme(rooms):
    try:
        with open("README.md", "r") as f:
            content = f.read()
    except FileNotFoundError:
        content = "<!-- THM-ROOMS:START -->\n<!-- THM-ROOMS:END -->"

    start_marker = "<!-- THM-ROOMS:START -->"
    end_marker = "<!-- THM-ROOMS:END -->"
    
    if start_marker not in content or end_marker not in content:
        print("Error: Comment markers missing in README.md")
        return

    if rooms:
        room_list_str = "\n" + "\n".join(rooms) + "\n"
    else:
        room_list_str = "\n* No recent completed labs found in Notion tracker.\n"

    pattern = f"{start_marker}.*?{end_marker}"
    new_content = re.sub(pattern, f"{start_marker}{room_list_str}{end_marker}", content, flags=re.DOTALL)

    with open("README.md", "w") as f:
        f.write(new_content)

if __name__ == "__main__":
    completed_rooms = get_completed_rooms_from_notion()
    update_readme(completed_rooms)
