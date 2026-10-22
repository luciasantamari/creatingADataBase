import json
import random
import statistics
import tempfile
import time
from pathlib import Path

from bbdd import AlphabeticalDirectory


class OriginalJSONDirectory:

    def __init__(self, filename):
        self.filename = Path(filename)
        self.table = [[] for _ in range(26)]

        if self.filename.exists():
            with self.filename.open("r", encoding="utf-8") as file:
                self.table = json.load(file)

    @staticmethod
    def _bucket(word):
        return ord(word[0].lower()) - ord("a")

    def insert(self, word):
        bucket = self.table[self._bucket(word)]

        if word in bucket:
            return bucket.index(word)

        bucket.append(word)

        with self.filename.open("w", encoding="utf-8") as file:
            json.dump(self.table, file)

        return len(bucket) - 1

    def search(self, word):
        bucket = self.table[self._bucket(word)]
        return bucket.index(word) if word in bucket else -1

    def close(self):
        pass


def make_words(count):
    words = []
    number = 0

    while len(words) < count:
        word = chr(ord("a") + number % 26) + f"word{number}"
        words.append(word)
        number += 1
    return words


def benchmark(factory, words, repeats=3):
    insertion_times = []
    search_times = []

    for _ in range(repeats):
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = Path(temp_dir) / "database.json"
            db = factory(filename)
            start = time.perf_counter()
            
            for word in words:
                db.insert(word)
            insertion_times.append(time.perf_counter() - start)

            db.close()

            db = factory(filename)
            queries = words.copy()
            random.Random(42).shuffle(queries)

            start = time.perf_counter()
            for word in queries:
                db.search(word)
            search_times.append(time.perf_counter() - start)

            db.close()

    return (
        statistics.median(insertion_times),
        statistics.median(search_times),
    )


def main():
    count = 1000
    repeats = 3
    words = make_words(count)

    implementations = [
        ("Original JSON", OriginalJSONDirectory),
        ("Append-only", AlphabeticalDirectory),
    ]

    print(f"Chain: {count}")
    print(f"Repetition: {repeats}")
    print("Median of each measure.\n")

    for name, factory in implementations:
        insert_time, search_time = benchmark(
            factory, words, repeats
        )

        print(name)
        print(f"  Insert: {insert_time:.6f} s")
        print(f"  Search:  {search_time:.6f} s")


if __name__ == "__main__":
    main()