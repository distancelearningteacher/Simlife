import streamlit as st

# --- 1. SET UP THE PAGE ---
st.set_page_config(page_title="My Adventure", layout="centered")

# --- 2. THE STORY DATA (The "JSON-like" part) ---
# You can easily move this to an external .json file later!
story = {
    "start": {
        "text": "You stand before a massive stone door in the Godot Forest.",
        "image": "https://porngipfy.com/wp-content/uploads/2018/09/august-ames_001.gif", # Replace with your URL or local path
        "options": [
            {"label": "Push the door", "target": "cave"},
            {"label": "Search the bushes", "target": "item_found"},
            {"label": "Run away", "target": "start"}
        ]
    },
    "cave": {
        "text": "The door creaks open. It's pitch black inside. You hear a low growl.",
        "image": "assets/grok_video_2025-12-31-18-14-00.mp4",
        "options": [
            {"label": "Light a torch", "target": "start"},
            {"label": "Step inside", "target": "start"},
            {"label": "Close the door", "target": "start"}
        ]
    },
    "item_found": {
        "text": "You found a glowing blue crystal! It feels warm to the touch.",
        "image": "https://placekitten.com/802/400",
        "options": [
            {"label": "Take it", "target": "start"},
            {"label": "Leave it", "target": "start"},
            {"label": "Smash it", "target": "start"}
        ]
    }
}

# --- 3. GAME ENGINE (The Logic) ---
# Initialize the "Autoload" state
if "scene" not in st.session_state:
    st.session_state.scene = "start"

def move_to(target):
    st.session_state.scene = target

# Get current scene data
current = story[st.session_state.scene]

# --- UPDATED DISPLAY LOGIC ---

# Get the file path from your story data
media_file = current["image"] 

# Check if the file is a video
if media_file.endswith(".mp4"):
    st.video(media_file, autoplay=True, loop=True, muted=True)
else:
    st.image(media_file, use_container_width=True)

# DISPLAY: Text in the middle
st.write(f"### {current['text']}")

# DISPLAY: 3 Options at the bottom
for option in current["options"]:
    # use_container_width=True makes buttons big and easy to tap on mobile
    if st.button(option["label"], use_container_width=True):
        move_to(option["target"])
        st.rerun()
