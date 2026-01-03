import streamlit as st
import json
import os

# --- 1. SETUP & DATA LOADING ---
st.set_page_config(page_title="Mage Quest", layout="centered")

def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)

# Load both data files
story_data = load_json("story.json")
char_images = load_json("characters.json")

# --- 2. INITIALIZE SESSION STATE ---
if "stats" not in st.session_state:
    st.session_state.stats = {
        "xp": 0, "magic": 50, "max_magic": 100, "suspicion": 0,
        "scene": "start", "view_mode": "GAME", "selected_npc": None
    }
    # Clone NPC data into session so changes persist
    st.session_state.npc_data = story_data["npcs"]

# --- 3. SIDEBAR (The Stats Bar) ---
with st.sidebar:
    st.title("🧙‍♂️ Mage Quest")
    lvl = (st.session_state.stats["xp"] // 10) + 1
    st.metric("Level", lvl)
    st.write(f"✨ Magic: {st.session_state.stats['magic']}/{st.session_state.stats['max_magic']}")
    st.write(f"🕵️ Suspicion: {st.session_state.stats['suspicion']}")
    
    st.divider()
    if st.button("👥 NPC Journal", use_container_width=True):
        st.session_state.stats["view_mode"] = "NPC_LIST"
        st.rerun()
    if st.button("♻️ Reset Game", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- 4. ENGINE LOGIC ---

# MODE: NPC LIST
if st.session_state.stats["view_mode"] == "NPC_LIST":
    if st.button("🔙 Back to Game"):
        st.session_state.stats["view_mode"] = "GAME"
        st.rerun()
    st.header("Journal")
    for npc_id in st.session_state.npc_data.keys():
        npc = st.session_state.npc_data[npc_id]
        if st.button(npc.get("name", npc_id), key=f"list_{npc_id}", use_container_width=True):
            st.session_state.stats["selected_npc"] = npc_id
            st.session_state.stats["view_mode"] = "NPC_DETAIL"
            st.rerun()

# MODE: NPC DETAIL
elif st.session_state.stats["view_mode"] == "NPC_DETAIL":
    if st.button("🔙 Back to List"):
        st.session_state.stats["view_mode"] = "NPC_LIST"
        st.rerun()
    
    npc_id = st.session_state.stats["selected_npc"]
    npc = st.session_state.npc_data[npc_id]
    
    st.header(npc.get("name", npc_id))
    
    # PULL IMAGE FROM CHARACTERS.JSON
    mood = npc["current_mood"]
    img_path = char_images.get(npc_id, {}).get(mood, "assets/placeholder.png")
    st.image(img_path, width=300)
    
    st.write(npc["bio"])
    st.write("---")
    for s_name, s_val in npc["stats"].items():
        st.write(f"**{s_name.replace('_', ' ').title()}:** {s_val}")

# MODE: MAIN GAME
else:
    scene_key = st.session_state.stats["scene"]
    current = story_data["story"].get(scene_key, story_data["story"]["start"])

    # 1. Media Display
    media = current.get("media")

    if not media:
        st.image("assets/placeholder.png", use_container_width=True)
    
    elif current.get("is_video"):
        st.video(media, autoplay=True, loop=True, muted=True)
    
    elif isinstance(media, str) and media.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        if os.path.exists(media):
            st.image(media, use_container_width=True)
        else:
            st.image("assets/placeholder.png", use_container_width=True)
    
    else:
        st.warning("⚠️ Invalid media format for this scene.")

    # 2. Options Display
    for i, opt in enumerate(current["options"]):
        if st.button(opt["label"], key=f"btn_{scene_key}_{i}", use_container_width=True):
            # Update Player
            st.session_state.stats["xp"] += opt.get("xp", 0)
            st.session_state.stats["magic"] += opt.get("magic", 0)
            st.session_state.stats["suspicion"] += opt.get("suspicion", 0)
            
            # Update NPC if specified
            if "npc" in opt:
                target_npc = opt["npc"]
                stat = opt["stat_change"]
                st.session_state.npc_data[target_npc]["stats"][stat] += opt["val"]
                
                # Logic: Update mood based on stat
                if st.session_state.npc_data[target_npc]["stats"].get("mind_altered", 0) > 5:
                    st.session_state.npc_data[target_npc]["current_mood"] = "dazed"

            st.session_state.stats["scene"] = opt["target"]
            st.rerun()
