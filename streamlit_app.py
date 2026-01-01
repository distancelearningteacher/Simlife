import streamlit as st
import json

# --- 1. SETUP ---
st.set_page_config(page_title="Mage Quest", layout="centered")

# --- 2. INITIALIZE GLOBAL STATS (The "Autoload") ---
if "stats" not in st.session_state:
    st.session_state.stats = {
        "xp": 0,
        "magic": 50,
        "max_magic": 50,
        "suspicion": 0,
        "scene": "room"
    }

# --- 3. CALCULATE LEVEL ---
# Level 1 = 0-9 XP, Level 2 = 10-19 XP, etc.
current_level = (st.session_state.stats["xp"] // 10) + 1

# --- 4. SIDEBAR (The Collapsing Bar) ---
with st.sidebar:
    st.title("🧙‍♂️ Character Sheet")
    st.metric("Level", current_level)
    
    # Progress bar for XP
    xp_progress = (st.session_state.stats["xp"] % 10) / 10
    st.write(f"XP: {st.session_state.stats['xp'] % 10} / 10")
    st.progress(xp_progress)
    
    st.divider()
    
    # Magic and Suspicion
    st.write(f"✨ Magic: {st.session_state.stats['magic']} / {st.session_state.stats['max_magic']}")
    st.write(f"🕵️ Suspicion: {st.session_state.stats['suspicion']}")
    
    if st.button("Reset Game"):
        st.session_state.clear()
        st.rerun()

# --- 5. LOAD STORY ---
def load_story():
    with open("story.json", "r") as f:
        return json.load(f)

story = load_story()
current = story[st.session_state.stats["scene"]]

# --- 6. RENDER ENGINE ---
# Media
if current.get("is_video"):
    st.video(current["media"], autoplay=True, loop=True, muted=True)
else:
    st.image(current["media"], use_container_width=True)

# Scene Text
st.write(f"### {current['text']}")

# Options Logic
for option in current["options"]:
    if st.button(option["label"], use_container_width=True):
        # Update Stats based on the JSON choice
        st.session_state.stats["xp"] += option.get("xp", 0)
        st.session_state.stats["magic"] += option.get("magic", 0)
        st.session_state.stats["suspicion"] += option.get("suspicion", 0)
        
        # Clamp Magic so it doesn't exceed max or go below 0
        st.session_state.stats["magic"] = max(0, min(st.session_state.stats["magic"], st.session_state.stats["max_magic"]))
        
        # Change Scene
        st.session_state.stats["scene"] = option["target"]
        st.rerun()

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
