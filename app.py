import os
import css
import json
import time
import solver
import utils as u
import config as c
import streamlit as st

st.set_page_config(layout="wide")
css.set_app_wide_styling()

def save_game():
    save_name = st.session_state.get("saved_file_name", None)
    if save_name:
        file_name = f"save_{st.session_state.get("saved_file_name", int(time.time()))}.json"
        file_path = os.path.join(c.SAVES_DIR, file_name)

        # Create directory if it doesn't exist
        os.makedirs(c.SAVES_DIR, exist_ok=True)

        with open(file_path, "w") as f:
            json.dump(u.get_grid(), f, indent=4)
        
        st.session_state["saved_file_name"] = None

@st.dialog("💾 Save Game", on_dismiss=save_game)
def save_file_dialog():
    file_name = st.text_input("What should the save be called?")
    sanitize_name = lambda name: name.replace(" ", "_").lower()
    if st.button("Save"):
        st.session_state.saved_file_name = sanitize_name(file_name) if file_name else int(time.time())

board, results = st.columns(2)

with board:
    with st.container(key="saves", horizontal=True, horizontal_alignment="center", vertical_alignment="bottom", gap="small", border=False, width=c.MAX_GRID*c.PIXEL_COUNT_PER_TILE):

        if st.button("🔄 Reset Board"):
            st.session_state["load_game"] = None 
            u.set_grid(reset=True)
        
        # load
        saved_games = []
        if os.path.exists(c.SAVES_DIR):
            saved_games = sorted(
                os.listdir(c.SAVES_DIR),
                key=lambda f: os.path.getctime(os.path.join(c.SAVES_DIR, f)),
                reverse=True  # most recent first
            )

        saved_games = sorted(saved_games, reverse=True)
        loaded_game = st.selectbox(
            label="📂 Load Game", 
            options=saved_games, 
            key="load_game",
            placeholder="Pick a saved game" if saved_games else "No saved games found",
            index=None
        )
        if loaded_game:
            try:
                with open(os.path.join(f"{c.SAVES_DIR}", loaded_game), "r") as f:
                    grid_str = f.read()
                    grid = json.loads(grid_str)
                    u.set_grid(grid)

            except Exception as e:
                st.error(f"Unable to load game.")

        # save
        if st.button("💾 Save Game"):
            save_file_dialog()

    st.markdown("")

    with st.form(key="scrabble_board", clear_on_submit=False, enter_to_submit=False, border=False, width="content"):
        with st.container(gap=None):
            for i in range(c.MAX_GRID):
                with st.container(horizontal=True, gap=None):  # one row
                    for j in range(c.MAX_GRID):
                        tile_key = c.tile_key(i, j)
                        st.text_input(
                            key=tile_key,
                            label=tile_key,
                            label_visibility="collapsed",
                            max_chars=1
                        )

        with st.container():
            shelf = st.text_input(
                key=c.SCRABBLE_SHELF_NAME,
                label="What letters are on your shelf?",
                max_chars=7,
                width=c.MAX_GRID*c.PIXEL_COUNT_PER_TILE,
                placeholder="· · · · · · ·"
            )

        form_submitted = st.form_submit_button("Get playable words")

with results:
    st.header("Playable Words")
    st.markdown("") # for spacing

    if form_submitted:
        if len(shelf) == 0:
            st.error("Please enter letters on your shelf.")
            st.stop()
            
        progress_text = "Solving..."
        progress_bar = st.progress(0, text=progress_text)

        grid = u.get_grid()
        progress_bar.progress(10, text=progress_text)

        anchors = u.get_anchors(grid)
        progress_bar.progress(25, text=progress_text)

        s = solver.Solver(shelf, anchors)
        progress_bar.progress(75, text=progress_text)
        
        res = s.get_ranked_results()
        progress_bar.progress(100, text=progress_text)

        if res:
            st.success(f"Found {len(res)} playable words!")
            for r in res:
                st.write(r)
        else:
            st.info("Looks like it's a new game. You can start with any of these!")
            for r in sorted(s.get_all_playable_words(), key=lambda x: u.score_value(x), reverse=True)[:5]:
                st.write(f"- {r} ({u.score_value(r)} points)")

        progress_bar.empty()
    else:
        st.info("Enter your shelf letters and press 'Get playable words' to see possible plays.")