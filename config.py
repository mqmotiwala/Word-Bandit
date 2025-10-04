WORDS_FILE = "words.txt"
POINTS = {'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4, 'i': 1, 'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1, 'p': 3, 'q': 10, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8, 'y': 4, 'z': 10}

SCORE_MULTIPLIERS = {
    # Triple Word (TW)
    (1, 1): "TW", (1, 8): "TW", (1, 15): "TW",
    (8, 1): "TW", (8, 15): "TW",
    (15, 1): "TW", (15, 8): "TW", (15, 15): "TW",

    # Double Word (DW)
    (2, 2): "DW", (3, 3): "DW", (4, 4): "DW", (5, 5): "DW",
    (14, 14): "DW", (13, 13): "DW", (12, 12): "DW", (11, 11): "DW",
    (2, 14): "DW", (3, 13): "DW", (4, 12): "DW", (5, 11): "DW",
    (14, 2): "DW", (13, 3): "DW", (12, 4): "DW", (11, 5): "DW",
    (8, 8): "DW",  # center star

    # Triple Letter (TL)
    (2, 6): "TL", (2, 10): "TL",
    (6, 2): "TL", (6, 6): "TL", (6, 10): "TL", (6, 14): "TL",
    (10, 2): "TL", (10, 6): "TL", (10, 10): "TL", (10, 14): "TL",
    (14, 6): "TL", (14, 10): "TL",

    # Double Letter (DL)
    (1, 4): "DL", (1, 12): "DL",
    (3, 7): "DL", (3, 9): "DL",
    (4, 1): "DL", (4, 8): "DL", (4, 15): "DL",
    (7, 3): "DL", (7, 7): "DL", (7, 9): "DL", (7, 13): "DL",
    (8, 4): "DL", (8, 12): "DL",
    (9, 3): "DL", (9, 7): "DL", (9, 9): "DL", (9, 13): "DL",
    (12, 1): "DL", (12, 8): "DL", (12, 15): "DL",
    (13, 7): "DL", (13, 9): "DL",
    (15, 4): "DL", (15, 12): "DL",
}

MULTIPLIER_COLORS = {
    "TW": "#ff4d4d",
    "DW": "#ffb366",
    "TL": "#4da6ff",
    "DL": "#99e6ff",
    None:  "#f6f0e1",
}

MAX_GRID = 15
PIXEL_COUNT_PER_TILE = 44
HORIZONTAL_ANCHOR_DIR = "played horizontally"
VERTICAL_ANCHOR_DIR = "played vertically"

SCRABBLE_SHELF_NAME = "scrabble_shelf"

def tile_key(row, col):
    return f"R{row}C{col}"