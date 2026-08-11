import re
import requests

# 🚨 CHANGE THIS: Replace with your actual TryHackMe username
USERNAME = "Blueeech0"  
LIMIT = 10  # Number of recent completed rooms to show

def get_completed_rooms():
    # Public endpoint for user recent activities
    url = f"https://tryhackme.com/p/Blueeech0"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            return []
        
        data = response.json()
        rooms = []
        
        # Parse activity logs for completed rooms
        for activity in data.get("data", []):
            text = activity.get("text", "")
            if "completed the room" in text.lower():
                # Extract room name inside markdown brackets [Room Name]
                match = re.search(r"\[(.*?)\]", text)
                room_name = match.group(1) if match else text.split("room")[-1].strip()
                if room_name not in rooms:
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
        print("README.md file not found. Creating a blank one.")
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
