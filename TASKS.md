# Team Task Allocation — Creating a Database

**Repository:** https://github.com/luciasantamari/creatingADataBase  
**Branch:** `main`  
**Current iteration:** E1 — basic persistent string database  
**Team:** Miguel, Hugo, Lucía, Miguelchi

## 1. Starting Point

The repository currently contains:

```text
creatingADataBase/
├── .github/
│   └── workflows/
│       └── tests.yml   # CI: runs pytest on every push and pull request
├── benchmarks/
│   └── compare.py      # First insert/search benchmark
├── README.md           # Product backlog
├── TASKS.md            # This file
├── bbdd.py             # AlphabeticalDirectory implementation
├── hash_index.py       # HashIndex and normalize(), not used by bbdd.py yet
├── storage.py          # Append-only Storage, not used by bbdd.py yet
├── test_hash_index.py  # Index tests (7 passing locally, not run by CI yet)
└── tests.py            # Existing pytest tests (6 passing)
```

The public implementation in `bbdd.py` stores **strings only**, with `insert(word)`, `search(word)`, and `delete(word)`. It keeps 26 buckets in memory and rewrites a JSON file when data changes. `storage.py` and `hash_index.py` are merged into `main`, but `bbdd.py` does not use them yet.

The goal is to improve the existing code without adding features unrelated to this iteration.

## 2. Immediate Fixes (Before Parallel Development)

The goal is to get the existing database working correctly before Miguel, Hugo, Lucía and Miguelchi start modifying separate modules. Steps 1–3 fix the current iteration. Steps 4–5 define how the next iteration will work.

| Step | Task | Status |
|---|---|---|
| 1 | Fix the import in `tests.py`: `from bbdd import AlphabeticalDirectory` | **DONE** |
| 2 | Fix `close()` in `bbdd.py`, which referenced the undefined `self.db` (now a no-op) | **DONE** |
| 3 | Run the tests: `python -m pytest -v tests.py` | **DONE**: 6 passing, locally and in CI |
| 4 | Agree on the module interfaces | **AGREED** |
| 5 | Agree on the storage record format | **AGREED** |

`close()` is a no-op for now because every write uses a `with` block that closes the file. Miguel can give it a real implementation later if `storage.py` keeps a file handle open.

### Team decisions

- **The database is built from scratch.** We write the storage, the index and the O(1) check ourselves instead of relying on helper libraries.
- **Allowed modules:** Python's standard library (`json`, `os`, `argparse`, `unicodedata`), which ships with Python and needs no installation, plus `pytest` only for running tests. Nothing installed with `pip` goes into the database code.
- `insert()` returns the record's **byte offset**.
- **`search()` can return more than one result:** a list of byte offsets, in insertion order (lowest offset first). Not found is an empty list `[]`, which replaces the old `-1`.
- `delete()` returns `True` if the string existed and `False` otherwise.
- **Inserts are case-sensitive and accept any UTF-8 text.** `"Boat"` and `"boat"` are two different strings and both can be stored.
- **Words are stored in NFC form**, so the two Unicode spellings of `"canción"` (one character `ó`, or `o` + combining accent) count as the same word.
- **No duplicates:** inserting an exact string that is already active writes nothing and returns its existing offset.
- **Search is case-insensitive and accent-insensitive by default** for ease of use: `search("CANCION")` finds `"canción"`, and `search("BOAT")` finds both `"Boat"` and `"boat"`.
- **`ñ` stays a separate letter.** Accents (`á é í ó ú ü`) are ignored, but `search("ano")` does not find `"año"`.
- **The `-c` flag means exact search:** both case and accents must match. It returns at most one offset.
- **`delete()` always uses the exact string.** `delete("boat")` does not delete `"Boat"`.
- **Empty strings are rejected.**
- **Deleting a string that does not exist returns `False`** and writes nothing.
- **Storage is `data.log` in JSON Lines** (step 5).
- **The index can be switched off with a flag**, as the professor suggested. With the index enabled, search is O(1). With it disabled, search scans `data.log` sequentially, which is O(n). A test compares the two (see "Testing" below).
- **There will be a command-line interface** built with `argparse` (Hugo): `-c` → `case_sensitive=True`, `--no-cache` → `use_index=False`.

### `delete` vs `remove`

They live at different levels and do different jobs:

| | `AlphabeticalDirectory.delete(word)` | `HashIndex.remove(word)` |
|---|---|---|
| Owner | Hugo (`bbdd.py`) | Lucía (`hash_index.py`) |
| Who calls it | The user (public API) | Only `bbdd.py` (internal) |
| Touches the disk? | **Yes**: appends a deletion marker to `data.log` | **No**: only edits the dictionary in memory |
| Returns | `True` / `False` | Nothing |
| Survives a restart? | Yes, because the marker is in the file | No; the index is rebuilt from the file on restart |

`delete()` uses `remove()`. Rough sketch:

```python
def delete(self, word):
    if not self.index.find(word, case_sensitive=True):
        return False                         # does not exist (exact match): write nothing
    self.storage.append(word, deleted=True)  # 1. record the deletion on disk
    self.index.remove(word)                  # 2. forget it in memory
    return True
```

At startup `remove()` is also called on its own: replaying `data.log`, each deletion marker calls `index.remove(word)`, with no new write, because the marker is already in the file.

Analogy: `delete()` is filing an official "deleted" record, and `remove()` is crossing the name out of your own notebook. If the notebook is lost (a restart), you rewrite it from the official records, and crossed-out names stay crossed out.

### Step 4 — Agreed interfaces

**Public database interface (Hugo, `bbdd.py`)**

```python
class AlphabeticalDirectory:
    def __init__(self, filename: str = "data.log", use_index: bool = True): ...
    def insert(self, word: str) -> int: ...
    def search(self, word: str, case_sensitive: bool = False) -> list[int]: ...
    def delete(self, word: str) -> bool: ...
```

- `insert()` returns the byte offset of the record on disk. Inserting an exact string that is already active appends nothing and returns its existing offset. The word is converted to NFC before anything else.
- `search()` returns the byte offsets of every active string that matches, lowest offset first, or `[]` if there are none. By default it ignores case and accents (but not `ñ`). `case_sensitive=True` (the `-c` flag) requires an exact match and returns at most one offset.
- `delete()` matches the exact string only. It returns `True` if the string was active and a deletion marker was appended. It returns `False` and writes nothing otherwise.
- `use_index=False` (the `--no-cache` flag) disables the hash index: `insert`, `search` and `delete` scan `storage.records()` from the start instead. This mode exists to show the difference between O(n) and O(1). It must give the same results as the indexed mode, only slower.
- **This is a deliberate API change.** Today `insert()` and `search()` return the position inside a bucket, and `search()` returns `-1` when nothing is found. Miguelchi will update the tests.
- `insert()` can return offset `0` (the first record), so do not treat its result as true/false. For `search()`, `if results:` is safe, because `[0]` is a non-empty list.

**Storage interface (Miguel, `storage.py`)**

```python
class Storage:
    def __init__(self, filename: str = "data.log"): ...
    def append(self, word: str, deleted: bool = False) -> int: ...
    def read(self, offset: int) -> str: ...
    def records(self): ...

    records_read: int   # how many records have been decoded from the file
```

- `append(word, deleted=False)` encodes one record, appends it to the file and returns the record's starting byte offset.
- `read(offset)` uses `seek(offset)` to read one record directly, without scanning the file, and returns its word.
- `records()` is a generator that reads the file sequentially and yields `(offset, word, deleted)` for each record.
- `records_read` starts at `0`. `read()` and `records()` add `1` for every record they decode. The O(1) test uses this counter (see "Testing" below), so we measure the work ourselves without any test helper.
- Storage does not hash anything or decide whether a string already exists. That is the index's and `bbdd.py`'s job.

**Hash index interface (Lucía, `hash_index.py`)**

```python
def normalize(word: str) -> str: ...   # lowercase, accents removed, ñ kept

class HashIndex:
    def add(self, word: str, offset: int): ...
    def find(self, word: str, case_sensitive: bool = False) -> list[int]: ...
    def remove(self, word: str): ...
    def clear(self): ...
```

- So that a search ignoring case and accents is still O(1), the dictionary key is the **normalized** word, and each key holds the exact variants stored under it:

  ```python
  {
      "boat":    {"boat": 0, "Boat": 41},
      "cancion": {"canción": 82},
  }
  ```

  (The offsets are illustrative.) `normalize(word)` gives the outer key in one dictionary lookup:
  - **Default search** returns every offset under that key, sorted: `find("BOAT")` → `[0, 41]`.
  - **Exact search** (`case_sensitive=True`) does a second lookup with the exact word: `find("Boat", case_sensitive=True)` → `[41]`.

  The number of variants per key is tiny (the capitalizations and accent placements of one word), so search stays O(1) in the number of stored words.
- `normalize()` lowercases the word and removes accents but keeps `ñ`. Using `unicodedata`: decompose with `"NFD"`, drop combining marks except the tilde (U+0303) after `n`, then recompose with `"NFC"`.
- `find()` returns `[]` for missing strings. `remove()` takes the exact word, and calling it on a missing word does nothing. When the last variant of a key is removed, the key is deleted too.

**Testing (Miguelchi, `tests.py`)**

Tests must use the public interface only, not internal details such as `directory.table` or `_hash_letter()`, because those disappear when the hash index replaces the buckets. For example:

```python
def test_insert_and_search(directory):
    lower = directory.insert("boat")
    upper = directory.insert("Boat")

    assert directory.search("BOAT") == [lower, upper]
    assert directory.search("Boat", case_sensitive=True) == [upper]
    assert directory.search("BOAT", case_sensitive=True) == []
    assert directory.search("missing") == []
```

**O(1) test, comparing the index on and off.** Do not measure time in a pass/fail test, because CI machines vary too much. Count how many records are read from the file instead, using our own `Storage.records_read` counter:

- Insert N words (for example 1,000) and reopen the database.
- Save `before = storage.records_read`, search for the last word, then compute `storage.records_read - before`.
- With `use_index=True`, the search reads **0** records: the offsets are already in memory, whatever N is.
- With `use_index=False`, the search reads **N** records (a sequential scan).
- Both modes must return the same list of offsets.

Repeat with a larger N to show that the indexed count stays at 0 while the sequential count grows. Real timings can go in `benchmarks/compare.py` as information, outside the pass/fail tests.

### Step 5 — Agreed storage format

- A new file, `data.log`. Do not reuse the existing JSON database file: its format is incompatible and would need a separate migration.
- One JSON record per line (JSON Lines), encoded as UTF-8 and terminated by `\n`:

  ```text
  {"word": "boat", "deleted": false}
  {"word": "sail", "deleted": false}
  {"word": "boat", "deleted": true}
  ```

- Deleting `"boat"` does not remove its original record. It appends a deletion marker. This is the central idea of append-only storage.
- The file is opened in binary mode (`"ab"` to append, `"rb"` to read), so offsets are byte positions and `seek()` can locate records reliably.
- **Startup replay:** `bbdd.py` calls `index.clear()`, then walks `storage.records()` in order. Each insert record calls `index.add(word, offset)` and each deletion marker calls `index.remove(word)`. With `use_index=False` there is no replay; each operation scans the file itself.
- Records store the word as inserted, converted to NFC (case and accents preserved). Lowercasing and accent removal exist only inside the index.
- **Malformed records** raise a `ValueError` whose message contains the byte offset, in both `records()` and `read()`. A record is malformed if it does not end in `\n`, is not valid UTF-8 or JSON, is not a JSON object, lacks `word` or `deleted`, has an empty or non-string `word`, or has a non-boolean `deleted`. Recovering from an interrupted final write is a separate backlog item (US-09), because it needs careful handling so that a later append cannot make corruption worse.

**Validation policy (applies to the whole database):**

- Stored strings are case-sensitive (`"Boat"` and `"boat"` are different strings). Search ignores case and accents unless `case_sensitive=True` / `-c` is used.
- Empty strings are rejected with `ValueError`, and non-strings with `TypeError`. `Storage.append()` also rejects a non-boolean `deleted` with `TypeError`. Invalid operations write nothing.
- Any UTF-8 text is accepted (for example `"canción"` or `"Ñandú"`) and stored in NFC form.

## 3. Responsibilities

### Miguel — Intermediate 1: Persistent Storage

**Owns:** New `storage.py`; extraction of file I/O currently in `bbdd.py`.

Implements the `Storage` class and the JSON Lines format proposed in §2 (steps 4 and 5).

**Tasks**

1. Implement `append()` with binary file mode (`"ab"`), returning the record's starting byte offset.
2. Implement `read()` using `"rb"` and `seek()`.
3. Implement `records()` as a generator yielding `(offset, word, deleted)`, and keep the `records_read` counter up to date in `read()` and `records()`.
4. Add validation for invalid strings, define behavior for a missing file (treat as empty), and raise an explicit error for malformed records.
5. Test Unicode strings, deletion markers, offsets, and persistence after reopening the file.

**Status (3 November 2026):** tasks 1–4 are implemented in `storage.py` and merged in PR #11, with one `_parse_line()` shared by `read()` and `records()` for validating records. PR #12 adds NFC conversion in `append()`, also checked by hand: both spellings of `canción` are written identically. `bbdd.py` must still convert words to NFC before passing them to the index, because otherwise an exact search differs before and after a restart. Checked by hand: offsets `0 35 70 109` for `boat`, `sail`, `canción`, `x`; Unicode round trip; deletion markers; reopening the file; a missing file yields nothing; and 11 corrupt-record cases plus `read()` past the end all raise `ValueError` with the offset. Still pending: task 5 (pytest tests, assigned to Miguelchi in `test_storage.py`) and a review, because PRs #11 and #12 have none recorded on GitHub. So nothing is DONE yet.

**Acceptance criteria**

- Inserting a new string appends a record without rewriting earlier records.
- A record can be read back using its byte offset.
- Restarting the program allows records to be replayed.
- Deletion is represented by a record/tombstone, not by rewriting the whole file.

**Learning focus:** binary files, offsets, persistence, serialization.

### Lucía — Beginner 1: Hash Index

**Owns:** New `hash_index.py`; replacement of the 26-list index logic from `bbdd.py`.

**Tasks**

1. Implement an in-memory dictionary keyed by the normalized word (lowercase, no accents), whose values map each exact active string to its byte offset (§2, step 4).
2. Implement `normalize()` and the `add`, `find` (with `case_sensitive`), `remove`, and `clear` operations with a small, documented interface.
3. Handle duplicate inserts without creating duplicate active entries.
4. Provide a way to rebuild the index by processing records supplied by Miguel's storage iterator.
5. Write a few focused index tests and explain the expected average-case search cost.

**Status (3 November 2026):** tasks 1–4 are implemented in `hash_index.py` and merged in PR #10, with `rebuild(records)` for task 4. The seven tests in `test_hash_index.py` pass locally but are not run by CI yet. Still pending: the search-cost explanation from task 5, and a review, because PR #10 has none recorded on GitHub. `bbdd.py` does not use the index yet, so nothing is DONE.

**Acceptance criteria**

- Finding an existing string returns its current offset in a list, both with and without `case_sensitive`.
- `find("CANCION")` finds `"canción"`; `find("CANCION", case_sensitive=True)` does not; `find("ano")` does not find `"año"`.
- With `"boat"` and `"Boat"` stored, `find("BOAT")` returns both offsets, lowest first.
- Missing or deleted strings are absent from the index.
- Replaying an insert and subsequent delete produces the correct final state.
- The index does not store the entire data file's contents as separate records.

**Learning focus:** Python dictionaries, hashing, interfaces, time complexity.

### Miguelchi — Beginner 2: Testing and Reliability

**Owns:** Existing `tests.py` (may later split tests into a `tests/` folder).

**Tasks**

1. ~~Repair the current test imports and teardown behavior together with the team.~~ Done: all six tests pass.
2. Rewrite the existing tests against the public interface (§2, step 4): replace the hard-coded bucket positions (`== 0`, `== 1`, …) and the `directory.table` check with offset-based assertions.
3. Add pytest coverage for insert, search, delete, duplicates, and missing strings.
4. Add restart/persistence tests using `tmp_path` and a new instance of the database.
5. Test edge cases such as empty strings, uppercase, accents, and special characters according to the team's agreed validation policy, including default search vs `case_sensitive=True`.
6. Test that old data remains accessible after several appended records and deletions.
7. Write the O(1) test from §2: use `Storage.records_read` to count records read with `use_index=True` (0) and `use_index=False` (N), and check that both modes return the same results.

**Acceptance criteria**

- `pytest` runs without import or teardown errors.
- Tests use isolated temporary files and do not affect real user data.
- Persistence and deletion behavior is tested across restarts.
- Tests express public behavior rather than relying on the old `table` implementation.

**Learning focus:** pytest, fixtures, edge cases, regression testing, debugging.

### Hugo — Intermediate 2: Integration, CI, and Performance

**Owns:** Existing `bbdd.py`, new GitHub Actions workflow, optional benchmark script.

**Tasks**

1. Keep `AlphabeticalDirectory` as the public entry point and connect storage and index modules.
2. Preserve the simple string-only API; do not add key-value objects, SQL, or B+ trees yet.
3. Coordinate the record format and method signatures before module implementation.
4. Implement the `use_index` switch: with the index off, `insert`, `search` and `delete` scan `storage.records()` sequentially.
5. Add a command-line interface with `argparse`: `-c` for exact search and `--no-cache` to disable the index. When a search returns several offsets, print each matching word using `storage.read(offset)`.
6. ~~Add a GitHub Actions workflow that runs `pytest` on pushes and pull requests.~~ Done: `.github/workflows/tests.yml`, the run on `a36040f` passed. It only runs `tests.py`, so `test_hash_index.py` must be added now and `test_storage.py` when it exists. Plain `python -m pytest` would skip `tests.py`, because that name does not match `test_*.py`.
7. Add a reproducible comparison of insertion and search speed between the original JSON implementation and the new append-only version. `benchmarks/compare.py` exists, but it labels the current `AlphabeticalDirectory` as "Append-only" although it still rewrites JSON. Fix the label or defer the comparison until the new engine exists.
8. Update `README.md` to reflect what is implemented and what remains planned.

**Acceptance criteria**

- Users interact through one documented database class.
- Insert, search, delete, and restart behavior work end to end.
- CI runs the same tests developers run locally.
- Performance results describe dataset size and measurement method, without unsupported speed claims.

**Learning focus:** modular architecture, integration, CI, benchmarking.

## 4. Planned Repository Layout

Files below marked **NEW** are deliverables, not existing files.

```text
creatingADataBase/
├── README.md                      # EXISTS — update when behavior changes
├── TASKS.md                       # EXISTS — this file
├── bbdd.py                        # EXISTS — Hugo integrates modules
├── tests.py                       # EXISTS — Miguelchi rewrites and expands tests
├── storage.py                     # EXISTS — Miguel (tests pending)
├── hash_index.py                  # EXISTS — Lucía
├── test_hash_index.py             # EXISTS — Lucía
├── test_storage.py                # NEW — Miguelchi
├── benchmarks/                    # EXISTS — Hugo (fix label)
│   └── compare.py
└── .github/                       # EXISTS — Hugo (CI done)
    └── workflows/
        └── tests.yml
```

## 5. Dependencies and Collaboration

| Dependency | Agreement | Owner(s) | Status |
|---|---|---|---|
| Storage record format | How inserts/deletes are encoded and how offsets are read | Miguel + Lucía | Agreed: JSON Lines in `data.log`, binary mode (§2, step 5) |
| Index interface | `add`, `find`, `remove`, `clear` and replay contract | Lucía + Hugo | Agreed (§2, step 4); `normalize()` uses `unicodedata` |
| Public return values | Keep existing API or document deliberate changes | Hugo + Miguelchi | Agreed: `insert()` → offset, `search()` → list of offsets (`[]` when missing), `delete()` → `bool` |
| Test scenarios | Agree on behavior for duplicates, invalid inputs, and restarts | All four | Agreed: case-sensitive inserts, case- and accent-insensitive search (`-c` for exact), reject empty strings, UTF-8, no duplicates, O(1) test with the index on/off |

**Review pairing:** Miguel reviews Lucía's index; Hugo reviews Miguelchi's tests. Lucía and Miguelchi should also review each other's pull requests to learn the full pipeline.

## 6. Suggested Development Order

1. ~~**Stabilize current version:** fix imports and `close()`; run tests.~~ Done.
2. **Agree on contracts:** define record encoding, offsets, return values, and invalid-input behavior. *(Agreed: see §2.)*
3. **Build in parallel:** Miguel works on `storage.py`, Lucía on `hash_index.py`, Miguelchi on tests; Hugo prepares integration and CI. *(`storage.py` and `hash_index.py` merged; storage tests and the rewrite of `tests.py` pending.)*
4. **Integrate:** Hugo joins the modules into `bbdd.py`, with support from the other three. *(Pending: `bbdd.py` on `main` still uses the 26 buckets.)*
5. **Verify:** run tests, review pull requests, benchmark, and update the backlog status.

## 7. Out of Scope for This Iteration

- B or B+ trees
- SQL or query parsing
- General-purpose key-value or document objects
- Transactions, concurrency, or distributed storage
- Premature optimization beyond measuring the implemented version

## 8. Definition of Done

A task is complete when its code is merged, its agreed acceptance criteria pass, its tests run locally and in CI, and another team member has reviewed the change.

PRs #10, #11 and #12 are merged, but that alone does not complete their tasks: none has a review recorded on GitHub, and their tests do not all run in CI yet.
