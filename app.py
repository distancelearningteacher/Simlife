import streamlit as st
import json
import os

# ----------------------------- CONFIG & DATA LOADING -----------------------------
ASSETS_PATH = "assets"
BACKGROUNDS_PATH = os.path.join(ASSETS_PATH, "backgrounds")
CHARACTERS_PATH = os.path.join(ASSETS_PATH, "characters")

# Load JSON files
@st.cache_data
def load_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

scenes = load_json("scenes.json")["scenes"]
characters = load_json("characters.json")["characters"]

# Optional config
config = {}
if os.path.exists("config.json"):
    config = load_json("config.json")

# Game state (saved in session_state)
if "current_scene" not in st.session_state:
    st.session_state.current_scene = "start"
if "history" not in st.session_state:
    st.session_state.history = []  # For log/back later if you want

current_scene_id = st.session_state.current_scene
scene = scenes.get(current_scene_id)

if scene is None:
    st.error(f"Scene '{current_scene_id}' not found!")
    st.stop()

# ----------------------------- PAGE CONFIG -----------------------------
st.set_page_config(
    page_title=config.get("gameTitle", "My Visual Novel"),
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit menu and footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ----------------------------- BACKGROUND -----------------------------
bg_file = scene.get("background", None)
if bg_file:
    bg_path = os.path.join(BACKGROUNDS_PATH, bg_file)
    if os.path.exists(bg_path):
        st.image(bg_path, use_column_width=True)
    else:
        st.warning(f"Background not found: {bg_file}")
else:
    st.markdown("<div style='height: 400px; background: #222;'></div>", unsafe_allow_html=True)

# ----------------------------- CHARACTERS -----------------------------
character_container = st.container()
with character_container:
    cols = st.columns(3)  # Left, Center, Right
    position_map = {"left": 0, "center": 1, "right": 2}

    displayed_chars = scene.get("characters", [])
    for char in displayed_chars:
        char_id = char["id"]
        if char_id not in characters or characters[char_id].get("hidden"):
            continue

        expr = char.get("expression", characters[char_id]["defaultExpression"])
        sprite_file = characters[char_id]["expressions"].get(expr)
        pos = char.get("position", "center")

        col_idx = position_map.get(pos, 1)
        with cols[col_idx]:
            if sprite_file:
                sprite_path = os.path.join(CHARACTERS_PATH, sprite_file)
                if os.path.exists(sprite_path):
                    st.image(sprite_path, width=300)
                else:
                    st.caption(f"Missing: {sprite_file}")

# ----------------------------- TEXT BOX -----------------------------
text = scene.get("text", "")
name = None

# Detect if it's dialogue (format: "Character: Text")
if ":" in text and text.split(":", 1)[0].strip() in [c["name"] for c in characters.values() if "name" in c]:
    name, dialogue = text.split(":", 1)
    name = name.strip()
    text = dialogue.strip()
else:
    text = text

# Text box styling
st.markdown("""
<style>
.textbox {
    background: rgba(0, 0, 0, 0.7);
    padding: 20px;
    border-radius: 10px;
    margin: 10px;
    color: white;
    font-size: 24px;
    min-height: 120px;
}
.namebox {
    background: rgba(50, 50, 50, 0.8);
    padding: 8px 15px;
    border-radius: 8px;
    display: inline-block;
    margin-bottom: 5px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

if name:
    st.markdown(f"<div class='namebox'>{name}</div>", unsafe_allow_html=True)

st.markdown(f"<div class='textbox'>{text}</div>", unsafe_allow_html=True)

# ----------------------------- CHOICES / ADVANCE -----------------------------
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    choices = scene.get("choices", [])
    
    if choices:
        for choice in choices:
            if st.button(choice["text"], use_container_width=True):
                next_scene = choice["nextScene"]
                st.session_state.current_scene = next_scene
                st.rerun()
    else:
        # Auto-advance or manual next
        if st.button("Continue ►", use_container_width=True):
            next_scene = scene.get("nextScene")
            if next_scene:
                st.session_state.current_scene = next_scene
                st.rerun()
            elif scene.get("endGame"):
                st.balloons()
                st.success("The End. Thank you for playing!")
                if st.button("Restart"):
                    st.session_state.current_scene = "start"
                    st.rerun()

# Optional: Music (autoplay not reliable in browsers, but you can add a toggle)
# if scene.get("music"):
#     music_path = os.path.join("assets/music", scene["music"])
#     if os.path.exists(music_path):
#         st.audio(music_path, autoplay=True)
