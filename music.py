"""
music.py — Study Music Player (Lo-fi, Nature Sounds, White Noise)
"""
import streamlit as st

LOFI_PLAYLISTS = [
    {"name": "☕ Lo-fi Hip Hop - Study Beats", "url": "https://www.youtube.com/embed/jfKfPfyJRdk?autoplay=0"},
    {"name": "🌙 Late Night Lo-fi Chill",      "url": "https://www.youtube.com/embed/lTRiuFIWV54?autoplay=0"},
    {"name": "📚 Study Music - Focus Flow",     "url": "https://www.youtube.com/embed/5qap5aO4i9A?autoplay=0"},
    {"name": "🎹 Piano Study Music",            "url": "https://www.youtube.com/embed/UuEcADpUo6k?autoplay=0"},
    {"name": "🌿 Chillhop Essentials",          "url": "https://www.youtube.com/embed/7NOSDKb0HlU?autoplay=0"},
]

NATURE_SOUNDS = [
    {"name": "🌧️ Rain on Window",     "url": "https://www.youtube.com/embed/mPZkdNFkNps?autoplay=0"},
    {"name": "🌊 Ocean Waves",         "url": "https://www.youtube.com/embed/bn9F19Hi1Lk?autoplay=0"},
    {"name": "🌲 Forest Birds",        "url": "https://www.youtube.com/embed/xNN7iTA57jM?autoplay=0"},
    {"name": "☕ Coffee Shop Ambience", "url": "https://www.youtube.com/embed/gaGrHPKBgIU?autoplay=0"},
    {"name": "🔥 Fireplace Crackling",  "url": "https://www.youtube.com/embed/L_LUpnjgPso?autoplay=0"},
]

WHITE_NOISE = [
    {"name": "⬜ Pure White Noise",    "url": "https://www.youtube.com/embed/nMfPqeZjc2c?autoplay=0"},
    {"name": "🌬️ Brown Noise",         "url": "https://www.youtube.com/embed/RqzGzwTY-6w?autoplay=0"},
    {"name": "🌀 Pink Noise",           "url": "https://www.youtube.com/embed/ZXtimhT-ff4?autoplay=0"},
    {"name": "🖥️ Fan / AC Noise",       "url": "https://www.youtube.com/embed/4hzSmBfZHRs?autoplay=0"},
]

SPOTIFY_PLAYLISTS = [
    {"name": "🎵 Lo-Fi Studying",        "url": "https://open.spotify.com/embed/playlist/0vvXsWCC9xrXsKd4euo32U"},
    {"name": "🧠 Deep Focus",            "url": "https://open.spotify.com/embed/playlist/37i9dQZF1DWZeKCadgRdKQ"},
    {"name": "📖 Peaceful Piano",        "url": "https://open.spotify.com/embed/playlist/37i9dQZF1DX4sWSpwq3LiO"},
    {"name": "🌿 Nature & Chill Study",  "url": "https://open.spotify.com/embed/playlist/37i9dQZF1DX3Ogo9pFvBkY"},
]

def music_player_page():
    st.title("🎵 Study Music Player")
    st.markdown("Pick your vibe and stay in the zone! 🎧")

    tab1, tab2, tab3, tab4 = st.tabs(["☕ Lo-fi Beats", "🌿 Nature Sounds", "⬜ White Noise", "🎵 Spotify"])

    with tab1:
        st.markdown("### ☕ Lo-fi Beats")
        st.markdown("Perfect background music for deep focus studying.")
        choice = st.selectbox("Choose a playlist", [p["name"] for p in LOFI_PLAYLISTS], key="lofi")
        selected = next(p for p in LOFI_PLAYLISTS if p["name"] == choice)
        st.components.v1.iframe(selected["url"], height=200)
        st.caption("▶️ Click play inside the player above")

    with tab2:
        st.markdown("### 🌿 Nature Sounds")
        st.markdown("Ambient sounds to help you concentrate.")
        choice = st.selectbox("Choose a sound", [p["name"] for p in NATURE_SOUNDS], key="nature")
        selected = next(p for p in NATURE_SOUNDS if p["name"] == choice)
        st.components.v1.iframe(selected["url"], height=200)

    with tab3:
        st.markdown("### ⬜ White / Brown / Pink Noise")
        st.markdown("Blocks out distractions with consistent background noise.")
        choice = st.selectbox("Choose noise type", [p["name"] for p in WHITE_NOISE], key="white")
        selected = next(p for p in WHITE_NOISE if p["name"] == choice)
        st.components.v1.iframe(selected["url"], height=200)

    with tab4:
        st.markdown("### 🎵 Spotify Study Playlists")
        st.markdown("Requires Spotify account. Opens embedded player.")
        choice = st.selectbox("Choose a playlist", [p["name"] for p in SPOTIFY_PLAYLISTS], key="spotify")
        selected = next(p for p in SPOTIFY_PLAYLISTS if p["name"] == choice)
        st.components.v1.iframe(selected["url"], height=380)

    st.markdown("---")
    st.markdown("### 💡 Tips for Study Music")
    st.markdown("""
    - **Lo-fi** works best for reading and note-taking
    - **Nature sounds** help during writing and essays  
    - **White noise** is best for deep problem solving
    - Keep volume **low** — music should fade into the background
    - Use **headphones** for best focus effect
    """)
