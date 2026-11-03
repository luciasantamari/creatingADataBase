import unicodedata


def normalize(word):
    decomposed = unicodedata.normalize("NFD", word.lower())
    result = []
    for ch in decomposed:
        if unicodedata.category(ch) == "Mn":
            if ch == "\u0303" and result and result[-1] == "n":
                result.append(ch)
            continue
        result.append(ch)
    return unicodedata.normalize("NFC", "".join(result))


class HashIndex:
    """In-memory index: normalized word -> {exact word: offset}."""

    def __init__(self):
        self._index = {}

    def add(self, word, offset):
        """Saves the exact word with its offset. Updates the offset if it already existed."""
        key = normalize(word)
        if key not in self._index:
            self._index[key] = {}
        self._index[key][word] = offset

    def find(self, word, case_sensitive=False):
        """Returns a list of offsets (lowest first), or [] if no match is found."""
        variants = self._index.get(normalize(word))
        if variants is None:
            return []
        if case_sensitive:
            if word in variants:
                return [variants[word]]
            return []
        return sorted(variants.values())

    def remove(self, word):
        """Deletes the exact word. Does nothing if it does not exist."""
        key = normalize(word)
        variants = self._index.get(key)
        if variants is None or word not in variants:
            return
        del variants[word]
        if not variants:
            del self._index[key]

    def clear(self):
        """Clears the entire index."""
        self._index.clear()

    def rebuild(self, records):
        """Rebuilds the index from storage.records().

        Each record is a tuple (offset, word, deleted), in file order.
        If deleted is False, the word is added; if True, it is removed.
        """
        self.clear()
        for offset, word, deleted in records:
            if deleted:
                self.remove(word)
            else:
                self.add(word, offset)