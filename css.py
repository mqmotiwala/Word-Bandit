import config as c
import streamlit as st

def set_app_wide_styling():
    """
    Applies specific styling choices app wide.
    """
    
    styling_css = ["<style>"]

    # create the base scrabble board using streamlit text input elements
    # sets grid-like structure, constraints text input elements to be square
    # css styling is scoped to stForm only
    styling_css.append(f"""
        div.stForm div[data-testid="stHorizontalBlock"] {{
            display:grid !important;
            grid-template-columns: repeat({c.MAX_GRID}, {c.PIXEL_COUNT_PER_TILE}px);
        }}
    """)

    # styling applied to each scrabble tile 
    for i in range(0, c.MAX_GRID):
        for j in range(0, c.MAX_GRID):
            mult = c.SCORE_MULTIPLIERS.get((i+1, j+1)) # SCORE_MULTIPLIERS is 1-based
            color = c.MULTIPLIER_COLORS.get(mult)

            styling_css.append(f"""
                /* tile container; positioning attr is required for tile multiplier text anchoring */
                div.st-key-{c.tile_key(i, j)} {{
                    position: relative;
                    display: inline-block;
                }}         

                div.st-key-{c.tile_key(i, j)} input[type="text"] {{
                    background-color: {color} !important;
                    border: 1px solid #000;
                    border-radius: 6px;

                    /* Horizontal centering */
                    text-align: center !important;

                    /* Vertical centering */
                    padding: 0 !important;

                    text-transform: uppercase;
                    font-size: 24px !important;
                    font-family: 'Fira Code', monospace;
                    font-weight: 900;
                }}

                /* tile hover effects */
                div.st-key-{c.tile_key(i, j)} input[type="text"]:hover {{
                    box-shadow: 0 0 8px #888888;
                    transform: scale(1.25);
                    transition: all 0.1s ease-in-out;
                }}   

                /* tile multiplier text */
                div.st-key-{c.tile_key(i, j)}::before {{
                    content: "{mult if mult else ''}"; 
                    position: absolute; 
                    top: 2px; 
                    left: 4px; 
                    font-size: 8px; 
                    font-weight: 700; 
                    color: #222; 
                    z-index: 2; 
                    pointer-events: none;
                }}
            """)

            if j == 0 or j == c.MAX_GRID-1:
                # endpoint columns - add text for row index beside it
                direction = "right" if j == 0 else "left"

                styling_css.append(f"""
                    div.st-key-{c.tile_key(i, j)} {{
                        position: relative;             /* ensures ::after is anchored to this tile */
                    }}

                    /* row label (to the left of first column tile) */
                    div.st-key-{c.tile_key(i, j)}::after {{
                        content: "{i+1}";
                        position: absolute;
                        padding: 2px 4px;
                        top: 50%;                           /* vertical center */
                        {direction}: 100%;                  /* move completely to the left of tile */
                        transform: translateY(-50%);        /* align vertically */
                        text-align: {direction};            /* right-align the text within that box */
                        font-size: 8px;
                        font-weight: 700;
                        color: #222;
                        z-index: 2;
                        pointer-events: none;
                        white-space: nowrap;
                    }}
                """)

            # --- Top & bottom row labels ---
            if i == 0 or i == c.MAX_GRID - 1:
                vertical_side = "top" if i == 0 else "bottom"
                percentage = "-100%" if i == 0 else "100%"

                styling_css.append(f"""
                    div.st-key-{c.tile_key(i, j)} {{
                        position: relative;
                    }}

                    div.st-key-{c.tile_key(i, j)}::after {{
                        content: "{j+1}";
                        position: absolute;
                        padding: 2px 4px;
                        {vertical_side}: 0;
                        left: 50%;
                        transform: translate(-50%, {percentage});
                        font-size: 8px; 
                        font-weight: 700;
                        color: #222;
                        z-index: 2;
                        pointer-events: none;
                        white-space: nowrap;
                    }}
                """)

    # styling applied to the shelf
    styling_css.append(f"""
        div.st-key-{c.SCRABBLE_SHELF_NAME} input[type="text"] {{
            border: 0.5px solid #000;
            border-radius: 6px;

            /* Horizontal centering */
            text-align: center !important;

            /* Vertical centering */
            padding: 0 !important;

            text-transform: uppercase;
            font-size: 32px !important;
            font-family: 'Fira Code', monospace;
            font-weight: 900;

            background: linear-gradient(to top, #fffdf5, #f2e8c9);
            box-shadow: 2px 2px 0px #aaa;
            letter-spacing: 20px
        }}

        div.st-key-{c.SCRABBLE_SHELF_NAME} input[type="text"]:hover {{
            box-shadow: 0 0 8px rgba(0,0,0,0.3);
            transform: scale(1.05);
            transition: all 0.1s ease-in-out;
        }}
    """)

    styling_css.append("</style>")
    st.html("".join(styling_css))