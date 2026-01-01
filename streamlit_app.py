import streamlit as st
import json
import os

# --- 1. SETUP & DATA LOADING ---
st.set_page_config(page_title="Mage Quest", layout="centered")

def load_data():
    with open("story.json", "r") as f:
        return json.load(f)

# Load the single JSON file that contains both 'story' and 'npcs'
data = load_data()

# --- 2. INITIALIZE GLOBAL STATE (The "Autoload") ---
if "stats" not in st.session_state:
    st.session_state.stats = {
        "xp": 0, 
        "magic": 50, 
        "max_magic": 50, 
        "suspicion": 0,
        "scene": "start",
        "view_mode": "GAME",  # Modes: "GAME", "NPC_LIST", "NPC_DETAIL"
        "selected_npc": None
    }
    # Initialize NPC stats in session state so they persist during the session
    if "npc_data" not in st.session_state:
        st.session_state.npc_data = data["npcs"]

# Shortcut for level calculation
current_level = (st.session_state.stats["xp"] // 10) + 1

# --- 3. SIDEBAR (The Collapsing Bar) ---
with st.sidebar:
    st.title("🧙‍♂️ Character Sheet")
    st.metric("Level", current_level)
    
    st.write(f"XP: {st.session_state.stats['xp'] % 10} / 10")
    st.progress((st.session_state.stats["xp"] % 10) / 10)
    
    st.divider()
    st.write(f"✨ Magic: {st.session_state.stats['magic']} / {st.session_state.stats['max_magic']}")
    st.write(f"🕵️ Suspicion: {st.session_state.stats['suspicion']}")
    
    st.divider()
    if st.button("👥 NPC Journal", use_container_width=True):
        st.session_state.stats["view_mode"] = "NPC_LIST"
        st.rerun()

    if st.button("♻️ Reset Game", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- 4. NAVIGATION LOGIC (The Switcher) ---

# Mode: NPC LIST
if st.session_state.stats["view_mode"] == "NPC_LIST":
    col1, col2 = st.columns([4, 1])
    col2.button("🔙", on_click=lambda: st.session_state.stats.update({"view_mode": "GAME"}))
    
    st.header("Characters Met")
    for npc_name in st.session_state.npc_data.keys():
        if st.button(npc_name, use_container_width=True):
            st.session_state.stats["selected_npc"] = npc_name
            st.session_state.stats["view_mode"] = "NPC_DETAIL"
            st.rerun()

# Mode: NPC DETAIL
elif st.session_state.stats["view_mode"] == "NPC_DETAIL":
    col1, col2 = st.columns([4, 1])
    col2.button("🔙", on_click=lambda: st.session_state.stats.update({"view_mode": "NPC_LIST"}))
    
    npc_name = st.session_state.stats["selected_npc"]
    npc = st.session_state.npc_data[npc_name]
    
    st.header(npc_name)
    mood = npc["current_mood"]
    st.image(npc["images"][mood], width=300)
    st.write(npc["bio"])
    
    # Display NPC Stats
    st.write("---")
    for s_name, s_val in npc["stats"].items():
        st.write(f"**{s_name.title()}:** {s_val}")

# Mode: MAIN GAME
else:
    scene_key = st.session_state.stats["scene"]
    # Ensure scene exists to prevent KeyError
    if scene_key not in data["story"]:
        st.error(f"Scene '{scene_key}' not found!")
        if st.button("Emergency Return to Start"):
            st.session_state.stats["scene"] = "start"
            st.rerun()
    else:
        current = data["story"][scene_key]

        # 1. DISPLAY MEDIA
        media_path = current["media"]
        if media_path.endswith(".mp4"):
            st.video(media_path, autoplay=True, loop=True, muted=True)
        else:
            st.image(media_path, use_container_width=True)

        # 2. DISPLAY TEXT
        st.write(f"### {current['text']}")

        # 3. DISPLAY OPTIONS
        for option in current["options"]:
            # Logic for conditional options (Requirement Check)
            can_afford = True
            if "req_magic" in option and st.session_state.stats["magic"] < option["req_magic"]:
                can_afford = False

            btn_label = option["label"] if can_afford else f"🔒 {option['label']} (Need {option.get('req_magic')} Magic)"
            
            if st.button(btn_label, use_container_width=True, disabled=not can_afford):
                # Update Player Stats
                st.session_state.stats["xp"] += option.get("xp", 0)
                st.session_state.stats["magic"] += option.get("magic", 0)
                st.session_state.stats["suspicion"] += option.get("suspicion", 0)
                
                # Update NPC Stats
                if "npc" in option:
                    n_target = option["npc"]
                    s_target = option["stat_change"]
                    st.session_state.npc_data[n_target]["stats"][s_target] += option["val"]
                    
                    # Check for Mood Evolution
                    if st.session_state.npc_data[n_target]["stats"].get("mind_altered", 0) > 5:
                        st.session_state.npc_data[n_target]["current_mood"] = "altered"

                # Move to next scene
                st.session_state.stats["scene"] = option["target"]
                st.rerun()
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
