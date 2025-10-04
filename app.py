import css
import solver
import utils as u
import config as c
import streamlit as st

st.set_page_config(layout="centered")
css.set_app_wide_styling()

with st.container(key="saves", horizontal=True, horizontal_alignment="center", gap="small", border=False, width=c.MAX_GRID*c.PIXEL_COUNT_PER_TILE):
    if st.button("Load Game"):
        pass

    if st.button("Save Game"):
        pass

with st.form(key="scrabble_board", clear_on_submit=False, enter_to_submit=False, border=True, width="content"):
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
        grid = []
        for i in range(c.MAX_GRID):
            grid.append([])
            for j in range(c.MAX_GRID):
                grid[i].append(st.session_state[c.tile_key(i, j)])
 
        anchors = u.get_anchors(grid)
        s = solver.Solver(shelf, anchors)
        
        res = s.get_ranked_results()
        for r in res:
            st.write(r)
