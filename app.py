import css
import json
import time
import solver
import utils as u
import config as c
import streamlit as st

st.set_page_config(layout="centered")
css.set_app_wide_styling()

with st.container(key="saves", horizontal=True, horizontal_alignment="center", vertical_alignment="center", gap="small", border=False, width=c.MAX_GRID*c.PIXEL_COUNT_PER_TILE):
    
    # load
    uploaded_file = st.file_uploader(key=c.FILE_UPLOADER_KEY, label=":material/upload: Load Game", type=["json"], label_visibility="collapsed")
    if uploaded_file is not None:
        try:
            grid_str = uploaded_file.getvalue().decode("utf-8")
            grid = json.loads(grid_str)
            u.set_grid(grid)

        except Exception as e:
            st.error(f"Error loading game: {e}")

    if st.button("🔄 Reset Board"):            
        u.set_grid(reset=True)

    # save
    st.download_button(
        label="📥 Save Game", 
        data=json.dumps(u.get_grid(), indent=4), 
        file_name=f"scrabble_save_{int(time.time())}.json", 
        mime="application/json", 
    )

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

    if st.form_submit_button("Get playable words"):
        if len(shelf) == 0:
            st.error("Please enter letters on your shelf.")
            st.stop()
            
        grid = u.get_grid()
 
        anchors = u.get_anchors(grid)
        s = solver.Solver(shelf, anchors)
        
        res = s.get_ranked_results()
        for r in res:
            st.write(r)