import streamlit as st
import json
import os

# ----------------------------- CONFIG & DATA LOADING -----------------------------
ASSETS_PATH = "assets"
BACKGROUNDS_PATH = os.path.join(ASSETS_PATH, "backgrounds")
CHARACTERS_PATH = os.path.join(ASSETS_PATH, "characters")

@st.cache_data
def load_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

scenes = load_json("scenes.json")["scenes"]
characters = load_json("characters.json")["characters"]

config = {}
if os.path.exists("config.json"):
    config = load_json("config.json")

# ----------------------------- SESSION STATE -----------------------------
if "current_scene" not in st.session_state:
    st.session_state.current_scene = "start"
if "sidebar_expanded" not in st.session_state:
    st.session_state.sidebar_expanded = False  # Start collapsed

current_scene_id = st.session_state.current_scene
scene = scenes.get(current_scene_id)

if scene is None:
    st.error(f"Scene '{current_scene_id}' not found!")
    st.stop()

# ----------------------------- PAGE CONFIG -----------------------------
st.set_page_config(
    page_title=config.get("gameTitle", "My Visual Novel"),
    layout="wide",  # Needed for better control with sidebar
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Hide default Streamlit menu & footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar toggle button styling */
    .sidebar-toggle {
        position: fixed;
        top: 50%;
        left: 0;
        z-index: 1000;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 15px 8px;
        border-radius: 0 10px 10px 0;
        cursor: pointer;
        font-size: 18px;
        writing-mode: vertical-rl;
        text-orientation: mixed;
    }

    /* Text box */
    .textbox {
        background: rgba(0, 0, 0, 0.75);
        padding: 20px;
        border-radius: 10px;
        margin: 10px 20px;
        color: white;
        font-size: 24px;
        min-height: 120px;
        backdrop-filter: blur(4px);
    }
    .namebox {
        background: rgba(50, 50, 50, 0.9);
        padding: 8px 15px;
        border-radius: 8px;
        display: inline-block;
        margin: 10px 20px 0;
        font-weight: bold;
        color: #fff;
    }

    /* Sidebar content when expanded */
    .sidebar-content {
        background: rgba(20, 20, 40, 0.9);
        padding: 20px;
        border-radius: 0 15px 15px 0;
        color: white;
        height: 100vh;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------- SIDEBAR TOGGLE -----------------------------
if st.session_state.sidebar_expanded:
    # Expanded: Show full sidebar on the left
    with st.sidebar:
        st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
        st.markdown("### 📊 Game Info")

        st.markdown("**Location**")
        st.info("Classroom (2F)")

        st.markdown("**Time of Day**")
        st.warning("🌅 Morning (08:45)")

        st.markdown("**Date**")
        st.info("Monday, April 15")

        st.markdown("### ❤️ Player Stats")
        st.progress(80)
        st.caption("Affection (Aiko): 80/100")

        st.progress(65)
        st.caption("Energy: 65/100")

        st.progress(40)
        st.caption("Confidence: 40/100")

        st.markdown("### 🎒 Inventory")
        st.write("- Student ID")
        st.write("- Bento Box")
        st.write("- Mystery Letter")

        st.markdown("---")
        if st.button("Close Sidebar ✕"):
            st.session_state.sidebar_expanded = False
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
else:
    # Collapsed: Just a thin toggle tab on the left
    st.markdown(
        """
        <div class='sidebar-toggle' onclick="document.getElementById('toggle-btn').click()">
            ► Game Info
        </div>
        """,
        unsafe_allow_html=True
    )

# Hidden button to trigger expand (triggered by CSS click)
if st.button("Toggle Sidebar", key="toggle-btn", help="Expand sidebar"):
    st.session_state.sidebar_expanded = True
    st.rerun()

# ----------------------------- MAIN GAME AREA -----------------------------
# Background
bg_file = scene.get("background")
if bg_file:
    bg_path = os.path.join(BACKGROUNDS_PATH, bg_file)
    if os.path.exists(bg_path):
        st.image(bg_path, use_column_width=True)
    else:
        st.warning(f"Background missing: {bg_file}")

# Characters
character_container = st.container()
with character_container:
    cols = st.columns([1, 3, 3, 3, 1])  # Better spacing: empty | left | center | right | empty
    position_map = {"left": 1, "center": 2, "right": 3}

    for char in scene.get("characters", []):
        char_id = char["id"]
        if char_id not in characters or characters[char_id].get("hidden"):
            continue

        expr = char.get("expression", characters[char_id]["defaultExpression"])
        sprite_file = characters[char_id]["expressions"].get(expr)
        pos = char.get("position", "center")

        col_idx = position_map.get(pos, 2)
        with cols[col_idx]:
            if sprite_file:
                sprite_path = os.path.join(CHARACTERS_PATH, sprite_file)
                if os.path.exists(sprite_path):
                    st.image(sprite_path, width=350)
                else:
                    st.caption(f"Missing sprite: {sprite_file}")

# Text Box
text = scene.get("text", "")
name = None

if ":" in text and text.split(":", 1)[0].strip() in [c["name"] for c in characters.values() if "name" in c]:
    name, dialogue = text.split(":", 1)
    name = name.strip()
    text = dialogue.strip()

if name:
    st.markdown(f"<div class='namebox'>{name}</div>", unsafe_allow_html=True)

st.markdown(f"<div class='textbox'>{text}</div>", unsafe_allow_html=True)

# Choices / Continue
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    choices = scene.get("choices", [])
    if choices:
        for choice in choices:
            if st.button(choice["text"], use_container_width=True):
                st.session_state.current_scene = choice["nextScene"]
                st.rerun()
    else:
        if st.button("Continue ►", use_container_width=True):
            next_scene = scene.get("nextScene")
            if next_scene:
                st.session_state.current_scene = next_scene
                st.rerun()
            elif scene.get("endGame"):
                st.balloons()
                st.success("The End! Thank you for playing!")
                if st.button("Restart Game"):
                    st.session_state.current_scene = "start"
                    st.rerun()
