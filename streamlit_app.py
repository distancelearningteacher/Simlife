import streamlit as st
import json
import os

# --- 1. SETUP & DATA LOADING ---
st.set_page_config(page_title="Mage Quest", layout="centered")

def load_data():
    with open("story.json", "r") as f:
        return json.load(f)

data = load_data()

# --- 2. INITIALIZE GLOBAL STATE ---
if "stats" not in st.session_state:
    st.session_state.stats = {
        "xp": 0, "magic": 50, "max_magic": 50, "suspicion": 0,
        "scene": "start",
        "view_mode": "GAME",
        "selected_npc": None
    }
    # Load NPC data from JSON into session state so it persists
    if "npc_data" not in st.session_state:
        st.session_state.npc_data = data["npcs"]

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🧙‍♂️ Character Sheet")
    lvl = (st.session_state.stats["xp"] // 10) + 1
    st.metric("Level", lvl)
    st.write(f"✨ Magic: {st.session_state.stats['magic']}")
    st.write(f"🕵️ Suspicion: {st.session_state.stats['suspicion']}")
    
    if st.button("👥 NPC Journal", use_container_width=True):
        st.session_state.stats["view_mode"] = "NPC_LIST"
        st.rerun()
    if st.button("♻️ Reset Game", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- 4. ENGINE LOGIC ---

# VIEW: NPC LIST
if st.session_state.stats["view_mode"] == "NPC_LIST":
    if st.button("🔙 Back to Game"):
        st.session_state.stats["view_mode"] = "GAME"
        st.rerun()
    st.header("Characters Met")
    for npc_id in st.session_state.npc_data.keys():
        name = st.session_state.npc_data[npc_id].get("name", npc_id)
        if st.button(name, key=f"btn_{npc_id}", use_container_width=True):
            st.session_state.stats["selected_npc"] = npc_id
            st.session_state.stats["view_mode"] = "NPC_DETAIL"
            st.rerun()

# VIEW: NPC DETAIL
elif st.session_state.stats["view_mode"] == "NPC_DETAIL":
    if st.button("🔙 Back to List"):
        st.session_state.stats["view_mode"] = "NPC_LIST"
        st.rerun()
    npc = st.session_state.npc_data[st.session_state.stats["selected_npc"]]
    st.header(npc["name"])
    st.image(npc["images"][npc["current_mood"]], width=300)
    st.write(npc["bio"])
    st.write("---")
    for s_name, s_val in npc["stats"].items():
        st.write(f"**{s_name.title()}:** {s_val}")

# VIEW: MAIN GAME
else:
    scene_key = st.session_state.stats["scene"]
    if scene_key not in data["story"]:
        st.error(f"Scene '{scene_key}' not found!")
        scene_key = "start"
    
    current = data["story"][scene_key]
    
    # Display Media
    if current.get("is_video"):
        st.video(current["media"], autoplay=True, loop=True, muted=True)
    else:
        st.image(current["media"], use_container_width=True)

    st.write(f"### {current['text']}")

    # Display Options
    for i, option in enumerate(current["options"]):
        # Unique key for every button to prevent Streamlit errors
        if st.button(option["label"], key=f"opt_{scene_key}_{i}", use_container_width=True):
            # Update Player
            st.session_state.stats["xp"] += option.get("xp", 0)
            st.session_state.stats["magic"] += option.get("magic", 0)
            st.session_state.stats["suspicion"] += option.get("suspicion", 0)
            
            # Update NPC if specified
            if "npc" in option:
                npc_id = option["npc"]
                stat = option["stat_change"]
                val = option["val"]
                st.session_state.npc_data[npc_id]["stats"][stat] += val
                
                # Check for mood change
                if st.session_state.npc_data[npc_id]["stats"].get("mind_altered", 0) > 5:
                    st.session_state.npc_data[npc_id]["current_mood"] = "altered"

            st.session_state.stats["scene"] = option["target"]
            st.rerun()
