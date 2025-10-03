import config as c
import streamlit as st

def set_app_wide_styling():
    """
    Applies specific styling choices app wide.
    """
    
    css = ["<style>"]

    # create the base scrabble board using streamlit text input elements
    # sets grid-like structure, constraints text input elements to be square and centers text within
    css.append(f"""
        div[data-testid="stHorizontalBlock"] {{
            display:grid !important;
            grid-template-columns: repeat({c.MAX_GRID}, {c.PIXEL_COUNT_PER_TILE}px);
        }}

        div[data-testid="stHorizontalBlock"] {{
            width:{c.PIXEL_COUNT_PER_TILE}px !important;
            height:{c.PIXEL_COUNT_PER_TILE}px !important;
            padding:0 !important;
            text-align:center;
            border:1px solid #000;
            border-radius:1px;
        }}
    """)

    # per-cell background by key
    for i in range(0, c.MAX_GRID):
        for j in range(0, c.MAX_GRID):
            mult = c.SCORE_MULTIPLIERS.get((i+1, j+1)) # SCORE_MULTIPLIERS is 1-based
            color = c.MULTIPLIER_COLORS.get(mult)

            key = f"r{i}c{j}"
            css.append(
                f'div.st-key-{key} input[type="text"]'
                f'{{ background-color:{color} !important; }}'
            )

    css.append("</style>")
    st.html("".join(css))