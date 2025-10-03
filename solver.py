import uuid
import utils as u
import config as c


class Solver:
    def __init__(self, shelf, anchors={}, words=None):
        # initialize shelf and anchor game states and ensure casing is lowered 
        self.shelf = shelf.lower()
        self.anchors = [{**a, "letters": a.get("letters", "").lower()} for a in anchors]

        self.words = u.load_words() if words is None else words
        self.all_playable_words = self.get_all_playable_words()
        self.anchored_playable_words = self.get_anchored_playable_words()

    def get_all_playable_words(self):
        return [word for word in self.words if u.is_playable(word, self.shelf)]
    
    def get_anchored_playable_words(self):
        res = {}
        for anchor in self.anchors:
            letters = anchor["letters"]
            anchor_position = anchor.get("anchor_position", uuid.uuid4())
            relative_anchors = anchor.get('relative_anchors', [])
            relative_letters = "".join([ra[0] for ra in relative_anchors])

            prefix_permitted = anchor.get("prefix_permitted", c.MAX_GRID)
            prefix_required = anchor.get("prefix_required", 0)

            postfix_permitted = anchor.get("postfix_permitted", c.MAX_GRID)
            postfix_required = anchor.get("postfix_required", 0)

            pWords = []
            for word in self.words:
                # if word == anchored letters
                if word == letters:
                    continue

                # if word contains anchored letters
                if not letters in word:
                    continue

                # if we can play the word with current shelf
                if not u.is_playable(word, self.shelf + letters + relative_letters):
                    continue

                # if word is long enough to meet prefix/postfix requirements
                required_length = len(letters) + prefix_required + postfix_required
                if not len(word) >= required_length:
                    continue

                # if required prefix/postfix constraints are met 
                # and relative anchor constraints are met 
                if not u.fits_anchor(word, letters, relative_anchors, prefix_required, prefix_permitted, postfix_required, postfix_permitted):
                    continue

                pWords.append(word)

            # use anchor metadata as unique fingerprint for anchor
            if pWords:
                res[anchor_position] = pWords

        return res
    
    def get_ranked_results(self):
        ranked_words = []
        for anchor_position, pWords in self.anchored_playable_words.items():
            for word in pWords:
                ranked_words.append((word, u.score_value(word, anchor_position), anchor_position))

        res = []
        for i, (word, score, anchor_position) in enumerate(sorted(ranked_words, key = lambda x: x[1], reverse=True)):
            res.append(f"{i+1}. {word} ({score} points) @ ({anchor_position[0]}, {anchor_position[1]}) {anchor_position[2]}")

        return res