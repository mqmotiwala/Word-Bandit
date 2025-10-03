import css
import solver
import utils as u
import config as c
import streamlit as st

st.set_page_config(layout="centered")
css.set_app_wide_styling()

with st.container(horizontal=True, horizontal_alignment="center", gap="small", border=True):
    st.button("Load Game")
    st.button("Save Game")

with st.form(key="scrabble_board", clear_on_submit=False, enter_to_submit=False, border=False):
    with st.container(gap=None):
        for i in range(15):
            with st.container(horizontal=True, gap=None):  # one row
                for j in range(15):
                    st.text_input(
                        key=f"r{i}c{j}",
                        label=f"r{i}c{j}",
                        label_visibility="collapsed",
                        max_chars=1
                    )

    with st.container():
        shelf = st.text_input(
            key="scrabble_shelf",
            label="What letters are on your shelf?",
            max_chars=7,
            width=c.MAX_GRID*c.PIXEL_COUNT_PER_TILE
        )

    if st.form_submit_button("Get playable words"):
        grid = []
        for i in range(15):
            grid.append([])
            for j in range(15):
                grid[i].append(st.session_state[f"r{i}c{j}"])
 
        anchors = u.get_anchors(grid)
        s = solver.Solver(shelf, anchors)
        
        res = s.get_ranked_results()
        for r in res:
            st.write(r)
