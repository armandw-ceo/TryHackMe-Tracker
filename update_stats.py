import re
import requests

USERNAME = "Blueeech0"  # Ensure this matches your exact case-sensitive username
LIMIT = 10  

def get_completed_rooms():
    url = f"https://tryhackme.com/p/Blueeech0"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            return []
        
        data = response.json()
        raw_logs = data.get("data", [])
        
        # DEBUG PRINT: This will print your last 3 activities in GitHub Actions logs so you can see them!
        print(f"Total raw activity logs fetched: {len(raw_logs)}")
        for x in raw_logs[:3]:
            print(f"Sample Log Found: {x.get('text')}")

        rooms = []
        for activity in raw_logs:
            text = activity.get("text", "")
            # Broader keyword checking to handle alternative formatting
            if "complete" in text.lower() or "finish" in text.lower():
                # Extract markdown links [Room Name](url) or clean up plain text
                match = re.search(r"\[(.*?)\]", text)
                room_name = match.group(1) if match else text.replace("Completed the room", "").replace("room", "").strip()
                
                if room_name and room_name not in rooms:
                    rooms.append(room_name)
                    
        return rooms[:LIMIT]
    except Exception as e:
        print(f"An error occurred: {e}")
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
        room_list_str = "\n" + "\n".join([f"* 🚀 **{room}**" for room in rooms]) + "\n"
    else:
        room_list_str = "\n* No recent completed rooms found or profile is private.\n"

    pattern = f"{start_marker}.*?{end_marker}"
    new_content = re.sub(pattern, f"{start_marker}{room_list_str}{end_marker}", content, flags=re.DOTALL)

    with open("README.md", "w") as f:
        f.write(new_content)

if __name__ == "__main__":
    completed_rooms = get_completed_rooms()
    update_readme(completed_rooms)
