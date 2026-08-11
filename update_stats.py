import os
import re
import requests

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
LIMIT = 10

def get_completed_rooms_from_notion():
    if not NOTION_TOKEN or not DATABASE_ID:
        print("Error: Missing NOTION_TOKEN or NOTION_DATABASE_ID in environment variables.")
        return [], 0

    token = NOTION_TOKEN.strip()
    db_id = DATABASE_ID.strip()

    protocol = "https"
    domain = "://notion.com"
    path = f"/v1/databases/{db_id}/query"
    url = f"{protocol}://{domain}{path}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    payload = {
        "sorts": [
            {
                "property": "Completed",
                "direction": "descending"
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"Connection established, but API returned status: {response.status_code}")
            return [], 0

        data = response.json()
        results = data.get("results", [])
        total_completed = len(results)

        rooms = []
        for index, result in enumerate(results):
            properties = result.get("properties", {})
            
            # 1. Extract Room Name
            name_property = properties.get("Name", {}) or {}
            name_title_list = name_property.get("title", [])
            room_name = ""
            if name_title_list and len(name_title_list) > 0:
                room_name = name_title_list[0].get("plain_text", "").strip()
            
            if not room_name:
                continue

            # 2. Extract Category
            category_select = properties.get("Category", {}) or {}
            select_data = category_select.get("select", {}) or {}
            category_name = select_data.get("name", "General")
            
            if "Red Team" in category_name:
                cat_emoji = "🔴"
            elif "Blue Team" in category_name:
                cat_emoji = "🔵"
            elif "Purple Team" in category_name:
                cat_emoji = "🟣"
            else:
                cat_emoji = "🚀"

            # 3. Extract Difficulty
            difficulty_select = properties.get("Difficulty", {}) or {}
            diff_data = difficulty_select.get("select", {}) or {}
            difficulty_name = diff_data.get("name", "").lower().strip()
            
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

            # 4. Extract URL (Strict case check matching your 'Url' naming choice)
            url_property = properties.get("Url", {}) or {}
            room_url = url_property.get("url", "")

            # 5. Extract Completed Date
            date_property = properties.get("Completed", {}) or {}
            date_data = date_property.get("date", {}) or {}
            completed_date = date_data.get("start", "") # Outputs format YYYY-MM-DD
            
            # Format date visual string if it exists
            date_str = f" 🗓️ *{completed_date}*" if completed_date else ""
            
            # Build metadata block structure
            metadata = f"— *{category_name}* \| `{diff_emoji}`{date_str}"
            
            if len(rooms) < LIMIT:
                # If a URL exists in Notion, make the name a clickable hyperlink
                if room_url:
                    rooms.append(f"* {cat_emoji} [**{room_name}**]({room_url}) {metadata}")
                else:
                    rooms.append(f"* {cat_emoji} **{room_name}** {metadata}")

        return rooms, total_completed

    except Exception as e:
        print(f"An unexpected connection error occurred: {e}")
        return [], 0

def update_readme(rooms, total_completed):
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

    output_lines = [
        "### ⚡ Quick Stats",
        "| Metric | Value |",
        "| :--- | :--- |",
        f"| 🏆 Rooms Completed | **{total_completed}** |",
        "",
        "### 🕒 Recent Lab Activity"
    ]

    if rooms:
        output_lines.extend(rooms)
    else:
        output_lines.append("* No recent completed labs found in Notion tracker.")

    room_list_str = "\n" + "\n".join(output_lines) + "\n"

    pattern = f"{start_marker}.*?{end_marker}"
    new_content = re.sub(pattern, f"{start_marker}{room_list_str}{end_marker}", content, flags=re.DOTALL)

    with open("README.md", "w") as f:
        f.write(new_content)

if __name__ == "__main__":
    completed_rooms, total_count = get_completed_rooms_from_notion()
    update_readme(completed_rooms, total_count)
