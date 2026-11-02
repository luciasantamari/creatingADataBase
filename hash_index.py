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
    """Índice en memoria: palabra normalizada -> {palabra exacta: offset}."""

    def __init__(self):
        self._index = {}

    def add(self, word, offset):
        """Guarda la palabra exacta con su offset. Si ya existía, actualiza el offset."""
        key = normalize(word)
        if key not in self._index:
            self._index[key] = {}
        self._index[key][word] = offset

    def find(self, word, case_sensitive=False):
        """Devuelve una lista de offsets (el menor primero), o [] si no hay nada."""
        variants = self._index.get(normalize(word))
        if variants is None:
            return []
        if case_sensitive:
            if word in variants:
                return [variants[word]]
            return []
        return sorted(variants.values())

    def remove(self, word):
        """Borra la palabra exacta. Si no existe, no hace nada."""
        key = normalize(word)
        variants = self._index.get(key)
        if variants is None or word not in variants:
            return
        del variants[word]
        if not variants:
            del self._index[key]

    def clear(self):
        """Vacía el índice entero."""
        self._index.clear()