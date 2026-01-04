import streamlit as st
import json
import os
from pathlib import Path

# ----------------------------- CONFIG & DATA LOADING -----------------------------
ASSETS_PATH = Path("assets")
BG_PATH = ASSETS_PATH / "backgrounds"
CHAR_PATH = ASSETS_PATH / "characters"
MUSIC_PATH = ASSETS_PATH / "music"

# Load JSON files
@st.cache_data
def load_json(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)

scenes = load_json("scenes.json")["scenes"]
characters = load_json("characters.json")["characters"]
try:
    config = load_json("config.json")
except FileNotFoundError:
    config = {"textSpeed": 50, "resolution": {"width": 1280, "height": 720}}

# ----------------------------- SESSION STATE INITIALIZATION -----------------------------
if "current_scene" not in st.session_state:
    st.session_state.current_scene = "start"
if "history" not in st.session_state:
    st.session_state.history = []  # For save/load later if you want

current_scene_id = st.session_state.current_scene
scene = scenes.get(current_scene_id, {})

# ----------------------------- PAGE CONFIG -----------------------------
st.set_page_config(
    page_title=config.get("gameTitle", "Visual Novel"),
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit's default menu and footer
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ----------------------------- BACKGROUND -----------------------------
background_file = scene.get("background", "")
bg_path = BG_PATH / background_file if background_file else None

if bg_path and bg_path.exists():
    st.image(str(bg_path), use_column_width=True)
else:
    st.markdown(
        "<div style='height: 400px; background: #333; display: flex; align-items: center; justify-content: center; color: white; font-size: 24px;'>"
        f"No background: {background_file}</div>",
        unsafe_allow_html=True
    )

# ----------------------------- CHARACTER SPRITES -----------------------------
character_container = st.container()

with character_container:
    cols = st.columns(5)  # left, far-left, center, right, far-right – adjust as needed
    position_map = {"left": 0, "far_left": 0, "center": 2, "right": 4, "far_right": 4}

    displayed_chars = scene.get("characters", [])
    for char in displayed_chars:
        char_id = char["id"]
        if char_id not in characters or characters[char_id].get("hidden"):
            continue

        expression = char.get("expression", characters[char_id]["defaultExpression"])
        sprite_file = characters[char_id]["expressions"].get(expression)
        pos_name = char.get("position", "center")
        col_idx = position_map.get(pos_name, 2)

        if sprite_file:
            sprite_path = CHAR_PATH / sprite_file
            if sprite_path.exists():
                with cols[col_idx]:
                    st.image(str(sprite_path), width=300)  # Adjust size as needed

# ----------------------------- TEXT BOX -----------------------------
text = scene.get("text", "")
name = None

# Detect if text is dialogue: "Character: Text"
if ":" in text and text.split(":")[0].strip() in [c["name"] for c in characters.values() if "name" in c]:
    name_part, dialogue = text.split(":", 1)
    name = name_part.strip()
    text = dialogue.strip()

# Dark semi-transparent text box
st.markdown(
    f"""
    <div style="
        background: rgba(0,0,0,0.75);
        padding: 20px;
        border-radius: 10px;
        margin: 20px;
        min-height: 150px;
        color: white;
        font-size: 24px;
    ">
    """,
    unsafe_allow_html=True
)

if name:
    st.markdown(f"**{name}**")
st.markdown(text)

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------- CHOICES & NAVIGATION -----------------------------
choices = scene.get("choices", [])
auto_advance = scene.get("autoAdvance")
end_game = scene.get("endGame", False)

if end_game:
    st.success("The End")
    if st.button("Restart"):
        st.session_state.current_scene = "start"
        st.rerun()

elif choices:
    st.markdown("<br>", unsafe_allow_html=True)
    for choice in choices:
        if st.button(choice["text"], use_container_width=True):
            st.session_state.current_scene = choice["nextScene"]
            st.rerun()

else:
    # Auto-advance or continue button
    if st.button("Continue ►", use_container_width=True):
        next_scene = scene.get("nextScene")
        if next_scene:
            st.session_state.current_scene = next_scene
            st.rerun()
        else:
            st.info("End of current content.")

# Optional: Auto-advance with delay (Streamlit doesn't support sleep directly, but we can simulate)
# Not implemented here to avoid complexity, but you can add with st.empty() + time.sleep if needed.

# ----------------------------- MUSIC (optional) -----------------------------
music_file = scene.get("music")
if music_file:
    music_path = MUSIC_PATH / music_file
    if music_path.exists():
        audio_bytes = open(music_path, 'rb').read()
        st.audio(audio_bytes, format='audio/mp3', autoplay=True)
