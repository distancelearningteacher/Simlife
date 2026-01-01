import streamlit as st
import json
import os

# --- 1. SETUP & DATA ---
st.set_page_config(page_title="Mage Quest", layout="centered")

def load_data():
    with open("story.json", "r") as f:
        return json.load(f)

data = load_data()

# --- 2. INITIALIZE STATE ---
if "stats" not in st.session_state:
    st.session_state.stats = {
        "xp": 0, "magic": 50, "max_magic": 50, "suspicion": 0,
        "scene": "start",
        "view_mode": "GAME",  # Can be "GAME", "NPC_LIST", or "NPC_DETAIL"
        "selected_npc": None
    }

# --- 3. SIDEBAR MENU ---
with st.sidebar:
    st.title("📜 Game Menu")
    if st.button("👥 NPC Journal", use_container_width=True):
        st.session_state.stats["view_mode"] = "NPC_LIST"
        st.rerun()
    
    st.divider()
    st.write(f"✨ Magic: {st.session_state.stats['magic']}")
    st.write(f"🕵️ Suspicion: {st.session_state.stats['suspicion']}")

# --- 4. TOP NAVIGATION (Return Button) ---
if st.session_state.stats["view_mode"] != "GAME":
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔙 Back"):
            st.session_state.stats["view_mode"] = "GAME"
            st.rerun()

# --- 5. RENDER LOGIC ---

# MODE A: NPC LIST
if st.session_state.stats["view_mode"] == "NPC_LIST":
    st.header("Characters Met")
    for npc_name in data["npcs"].keys():
        if st.button(npc_name, use_container_width=True):
            st.session_state.stats["selected_npc"] = npc_name
            st.session_state.stats["view_mode"] = "NPC_DETAIL"
            st.rerun()

# MODE B: NPC DETAIL
elif st.session_state.stats["view_mode"] == "NPC_DETAIL":
    npc_name = st.session_state.stats["selected_npc"]
    npc_data = data["npcs"][npc_name]
    
    st.header(npc_name)
    
    # Logic for dynamic image selection
    mood = npc_data["current_mood"]
    img_path = npc_data["images"][mood]
    
    if os.path.exists(img_path) or img_path.startswith("http"):
        st.image(img_path, width=300)
    else:
        st.warning(f"Image not found: {img_path}")
        
    st.write(npc_data["bio"])

# MODE C: MAIN GAME
else:
    scene_key = st.session_state.stats["scene"]
    current = data["story"][scene_key]
    
    # (Your existing media and button rendering code goes here)
    st.image(current["media"], use_container_width=True)
    st.write(f"### {current['text']}")
    
    for option in current["options"]:
        if st.button(option["label"], key=option["label"], use_container_width=True):
            st.session_state.stats["scene"] = option["target"]
            st.rerun()
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
        # 1. Update Player Stats
        st.session_state.stats["xp"] += option.get("xp", 0)
        st.session_state.stats["magic"] += option.get("magic", 0)
        st.session_state.stats["suspicion"] += option.get("suspicion", 0)
        
        # 2. Update NPC Stats (New Logic)
        if "npc" in option:
            npc_name = option["npc"]
            stat_to_change = option["stat_change"]
            amount = option["val"]
            
            # This changes the stat inside our data dictionary
            data["npcs"][npc_name]["stats"][stat_to_change] += amount
            
            # Logic: If Mind Altered > 5, change mood to "altered"
            if data["npcs"][npc_name]["stats"].get("mind_altered", 0) > 5:
                 data["npcs"][npc_name]["current_mood"] = "altered"

        # 3. Change Scene
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
