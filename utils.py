import config as c
import streamlit as st

def load_words():
    with open (c.WORDS_FILE, "r") as f:
        words = [line.strip() for line in f.readlines()]

    return words

def is_playable(word, letters):
    """
        Args:
            word (str): 
                word to check against

            letters (str | dict):
                if letters is a str, its interpreted as the current scrabble shelf
                    and a dict of schema {letter: cnt of letter on shelf} is created  

        Returns (bool):
            True if word is playable with given letters else False
    """

    if not isinstance(letters, (str, dict)):
        raise ValueError(f"letters is of invalid type {type(letters)}")

    if isinstance(letters, str):
        letters = {k: letters.count(k) for k in letters}

    word_breakdown = {w: word.count(w) for w in word}
    for w, cnt in word_breakdown.items():
        if w not in letters or cnt > letters[w]:
            # checks if letter in word exists on shelf
            # and if the word needs more of a given letter than we have on shelf
            return False 
        
    return True

def score_value(word, anchor_position=None):
    """
    Calculate the Scrabble score for a word.

    If no anchor position is given, the function simply sums the base
    letter values. If an anchor position is provided, the function
    applies board multipliers (Double/Triple Letter, Double/Triple Word)
    according to the standard Scrabble board layout.

    Args:
        word (str): The word being scored.
        anchor_position (tuple or None): Optional tuple of the form 
            (row, col, direction) using 1-based coordinates.
            - row (int): starting row of the first letter (1-15).
            - col (int): starting column of the first letter (1-15).
            - direction (int/enum): c.HORIZONTAL_ANCHOR_DIR or c.VERTICAL_ANCHOR_DIR.

    Returns:
        int: Total Scrabble score, including applicable multipliers.
    """

    if anchor_position is None:
        return sum([c.POINTS[letter] for letter in word])
    
    row, col, direction = anchor_position

    # Collect board positions for each letter
    if direction == c.HORIZONTAL_ANCHOR_DIR:
        tiles = [(row, col + i) for i in range(len(word))]
    elif direction == c.VERTICAL_ANCHOR_DIR:
        tiles = [(row + i, col) for i in range(len(word))]
    else:
        raise ValueError(f"Invalid anchor direction: {direction}")

    word_multiplier = 1
    total_points = 0

    for letter, tile in zip(word, tiles):
        base_points = c.POINTS[letter]
        multiplier = c.SCORE_MULTIPLIERS.get(tile)

        if multiplier == "TW":
            word_multiplier *= 3
        elif multiplier == "DW":
            word_multiplier *= 2
        elif multiplier == "TL":
            base_points *= 3
        elif multiplier == "DL":
            base_points *= 2

        total_points += base_points

    return total_points * word_multiplier

def sort(lst):
    """returns lst sorted in descending order of score value for words in list"""
    
    return sorted(lst, key=lambda word: score_value(word), reverse=True)

def get_indices_of_substr(s, sub):
    "returns a list of indices at which substring exists in string"
    indices = []
    start = 0
    while True:
        i = s.find(sub, start)
        if i == -1:
            break
        indices.append(i)
        start = i + 1   # move forward so overlaps are found too

    return indices

def fits_anchor(word, sub, rel_anchors, pre_req, pre_perm, post_req, post_perm):
    """
    Check whether a given substring appears in `word` such that:
      1. The number of characters before and after the substring falls within allowed bounds.
      2. All relative anchors are present at their specified offsets from the substring start.

    For each occurrence of `sub` inside `word`:
      - `prefix` is the number of characters before the substring.
      - `postfix` is the number of characters after the substring.
      - Each relative anchor is a tuple (substr, offset), where `substr` must
        appear at index (i + offset), with `i` being the start index of `sub`.

    The function returns True if at least one occurrence satisfies both
    the prefix/postfix constraints and the relative anchor constraints.

    Args:
        word (str): The string to search in.
        sub (str): The base substring to locate inside `word`.
        rel_anchors (list[tuple[str, int]]): List of (substring, relative_index) pairs.
            Each substring must match `word` starting at (i + relative_index).
        pre_req (int): Minimum number of characters required before `sub`.
        pre_perm (int): Maximum number of characters permitted before `sub`.
        post_req (int): Minimum number of characters required after `sub`.
        post_perm (int): Maximum number of characters permitted after `sub`.

    Returns:
        bool: True if at least one occurrence of `sub` in `word` meets both
              the prefix/postfix constraints and all relative anchor constraints,
              False otherwise.
    """
    word_len = len(word)
    sub_len = len(sub)

    for i in get_indices_of_substr(word, sub):
        prefix = i
        postfix = word_len - sub_len - i

        # Check prefix/postfix constraints
        if not (pre_req <= prefix <= pre_perm and post_req <= postfix <= post_perm):
            continue

        # Check relative anchors
        valid = True
        for rel_sub, offset in rel_anchors:
            start = i + offset
            end = start + len(rel_sub)
            if start < 0 or end > word_len or word[start:end] != rel_sub:
                valid = False
                break

        if valid:
            return True

    return False

def generate_anchors_from_slice(arr, arr_attrs):
    """
    Generate anchor definitions from a 1D slice of the Scrabble board
    (either a row or a column). Anchors represent placed tiles that can
    serve as fixed points for generating playable words, along with the
    space available before and after them.

    Args:
        arr (list[str]): A 1D view of the board row/column. Each element
            should be either a single character string (letter tile) or an
            empty string/whitespace if the square is unoccupied.
        arr_attrs (tuple[str, int]): Metadata describing the slice.
            - arr_type (str): "row" or "col", indicating whether this is a
              horizontal or vertical slice.
            - arr_index (int): The index of the row or column in the full
              2D board (0-based).

    Returns:
        list[dict]: A list of anchor definitions. Each anchor dict includes:
            - "anchor_position" (tuple[int, int]): The (row, col) position
              of the anchor on the full board (1-based indices).
            - "letters" (str): The base letter at the anchor position.
            - "prefix_permitted" (int): Number of tiles available before
              the anchor in this row/column.
            - "postfix_permitted" (int): Number of tiles available after
              the anchor in this row/column.
            - "relative_anchors" (list[tuple[str, int]]): Additional
              anchors relative to the base anchor when gaps exist. Each
              tuple contains:
                * The relative anchor letter (str).
                * The relative offset from the base anchor (int).

    Notes:
        - Prefix and postfix values represent the maximum playable space
          around an anchor, constrained by either the start/end of the row/
          column or other placed tiles.
        - Relative anchors capture additional placed tiles between the base
          anchor and the current endpoint being considered.
        - A final check ensures that if the last played tile in the slice
          has open space after it, an anchor is created extending to the
          end of the row/column.
    """

    def _get_prefix(arr, i):
      # identify characters directly preceding anchor
      # appended to rel_anchors downstream
      prefix = ""
      while i > 0 and arr[i-1].strip():
          prefix += arr[i-1]
          i -= 1

      return prefix[::-1]

    arr_type, arr_index = arr_attrs
    lng = len(arr)

    # get all indices of arr with played tiles
    positions = []
    for i in range(lng):
        letter = arr[i].strip()
        
        if letter:
            positions.append((letter, i))

    anchors = []
    for p1 in range(len(positions)):

        p2 = 0
        prefix_permitted = (positions[p1][1] - 0) if p1 == 0 else max(positions[p1][1] - positions[p1-1][1] - 2, 0)
        prefix = _get_prefix(arr, positions[p1][1])
        while p2 < len(positions):
            playable_space = max(positions[p2][1] - positions[p1][1] - 2, 0)
            
            rel_anchors = []
            num_rel_anchors = max(p2 - p1, 0)
            for i in range(1, num_rel_anchors + 1):
                rel_anchors.append((positions[p1 + i][0], positions[p1 + i][1] - positions[p1][1]))

            if playable_space and ((positions[p1][1] + playable_space) not in [pos[1] for pos in positions]) :
                if prefix:
                  rel_anchors.append((prefix, -len(prefix)))

                anchors.append({
                    "anchor_position": (arr_index + 1, positions[p1][1] + 1) if arr_type == "row" else (positions[p1][1] + 1, arr_index + 1),
                    "letters": positions[p1][0],
                    "prefix_permitted": prefix_permitted,
                    "postfix_permitted": playable_space,
                    "relative_anchors": rel_anchors
                })

            p2 += 1

    # check for a gap between last played tile and end of arr
    if positions and positions[-1][1] < len(arr) - 1:
        prefix_permitted = (positions[-1][1] - 0) if len(positions) == 1 else max(positions[-1][1] - positions[-2][1] - 2, 0)
        
        prefix = _get_prefix(arr, positions[-1][1])
        rel_anchors = [(prefix, -len(prefix))] if prefix else []

        playable_space = len(arr) - positions[-1][1] - 1
        anchors.append({
            "anchor_position": (arr_index + 1, positions[-1][1] + 1, c.HORIZONTAL_ANCHOR_DIR) if arr_type == "row" else (positions[-1][1] + 1, arr_index + 1, c.VERTICAL_ANCHOR_DIR),
            "letters": positions[-1][0],
            "prefix_permitted": prefix_permitted,
            "postfix_permitted": playable_space,
            "relative_anchors": rel_anchors
        })
    
    return anchors

def get_anchors(grid):
    
    anchors = []

    for i, row in enumerate(grid):
        anchors += generate_anchors_from_slice(row, ("row", i))

    cols = [list(col) for col in zip(*grid)]
    for i, col in enumerate(cols):
        anchors += generate_anchors_from_slice(col, ("col", i))

    return anchors

def get_grid(session_state=st.session_state):
    """
        Extracts the current Scrabble board state from Streamlit session_state.
        Args:
            session_state (st.session_state): The Streamlit session state object.
    """
    
    grid = []
    for i in range(c.MAX_GRID):
        grid.append([])
        for j in range(c.MAX_GRID):
            grid[i].append(session_state.get(str(c.tile_key(i, j)), ""))

    return grid

def set_grid(grid=None, session_state=st.session_state, reset=False):
    """
    Sets or resets the Scrabble board state in Streamlit session_state.

    Args:
        grid (list[list[str]] or None): 2D list representing the Scrabble board.
                                        If None and reset=True, initializes with empty strings.
        session_state (st.session_state): The Streamlit session state object.
        reset (bool): If True, resets the board to empty strings.
    """
    for i in range(c.MAX_GRID):
        for j in range(c.MAX_GRID):
            key = str(c.tile_key(i, j))
            if reset or grid is None:
                session_state[key] = ""
            else:
                session_state[key] = grid[i][j]