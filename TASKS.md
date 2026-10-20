# Team Task Allocation — Creating a Database

**Repository:** https://github.com/luciasantamari/creatingADataBase  
**Branch:** `main`  
**Current iteration:** E1 — basic persistent string database  
**Team:** Miguel, Hugo, Lucía, Miguelchi

## 1. Starting Point

The repository currently contains only:

```text
creatingADataBase/
├── README.md    # Product backlog
├── bbdd.py      # AlphabeticalDirectory implementation
└── tests.py     # Existing pytest tests
```

The existing implementation stores **strings only**, with `insert(word)`, `search(word)`, and `delete(word)`. It keeps 26 buckets in memory and rewrites a JSON file when data changes.

**This allocation describes work to do, not files that already exist.** The goal is to improve the existing code without adding features unrelated to this iteration.

## 2. Immediate Fix (Before Parallel Development)

Complete this small fix together or via one short pull request:

- Agree on the public interface and the storage record format before developing modules separately.

**Agreed public interface:** keep `AlphabeticalDirectory.insert(word)`, `.search(word)`, and `.delete(word)` for now. The group must agree whether `search()` returns a position, a Boolean, or `-1` before rewriting the index or tests. For minimal compatibility, retain `-1` for missing strings and document any change to the successful result.

## 3. Responsibilities

### Miguel — Intermediate 1: Persistent Storage

**Owns:** New `storage.py`; extraction of file I/O currently in `bbdd.py`.

**Tasks**

1. Design an append-only file format for inserting and deleting strings.
2. Implement byte-offset-based writes and reads in binary mode.
3. Implement sequential record iteration for index reconstruction at startup.
4. Define clear behavior for missing files and malformed records.
5. Document the storage format so the other members can integrate it.

**Acceptance criteria**

- Inserting a new string appends a record without rewriting earlier records.
- A record can be read back using its byte offset.
- Restarting the program allows records to be replayed.
- Deletion is represented by a record/tombstone, not by rewriting the whole file.

**Learning focus:** binary files, offsets, persistence, serialization.

### Lucía — Beginner 1: Hash Index

**Owns:** New `hash_index.py`; replacement of the 26-list index logic from `bbdd.py`.

**Tasks**

1. Implement an in-memory dictionary mapping each active string to its latest byte offset.
2. Implement `add`, `find`, `remove`, and `clear` operations with a small, documented interface.
3. Handle duplicate inserts without creating duplicate active entries.
4. Provide a way to rebuild the index by processing records supplied by Miguel's storage iterator.
5. Write a few focused index tests and explain the expected average-case search cost.

**Acceptance criteria**

- Finding an existing string returns its current offset.
- Missing or deleted strings are absent from the index.
- Replaying an insert and subsequent delete produces the correct final state.
- The index does not store the entire data file's contents as separate records.

**Learning focus:** Python dictionaries, hashing, interfaces, time complexity.

### Miguelchi — Beginner 2: Testing and Reliability

**Owns:** Existing `tests.py` (may later split tests into a `tests/` folder).

**Tasks**

1. Repair the current test imports and teardown behavior together with the team.
2. Add pytest coverage for insert, search, delete, duplicates, and missing strings.
3. Add restart/persistence tests using `tmp_path` and a new instance of the database.
4. Test edge cases such as empty strings, uppercase, accents, and special characters according to the team's agreed validation policy.
5. Test that old data remains accessible after several appended records and deletions.

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
4. Add a GitHub Actions workflow that runs `pytest` on pushes and pull requests.
5. Add a reproducible comparison of insertion and search speed between the original JSON implementation and the new append-only version.
6. Update `README.md` to reflect what is implemented and what remains planned.

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
├── bbdd.py                        # EXISTS — Hugo integrates modules
├── tests.py                       # EXISTS — Miguelchi expands tests
├── storage.py                     # NEW — Miguel
├── hash_index.py                  # NEW — Lucía
├── benchmarks/                   # OPTIONAL — Hugo
│   └── compare.py
└── .github/                      # NEW — Hugo
    └── workflows/
        └── tests.yml
```

## 5. Dependencies and Collaboration

| Dependency | Agreement | Owner(s) |
|---|---|---|
| Storage record format | How inserts/deletes are encoded and how offsets are read | Miguel + Lucía |
| Index interface | `add`, `find`, `remove`, `clear` and replay contract | Lucía + Hugo |
| Public return values | Keep existing API or document deliberate changes | Hugo + Miguelchi |
| Test scenarios | Agree on behavior for duplicates, invalid inputs, and restarts | All four |

**Review pairing:** Miguel reviews Lucía's index; Hugo reviews Miguelchi's tests. Lucía and Miguelchi should also review each other's pull requests to learn the full pipeline.

## 6. Suggested Development Order

1. **Stabilize current version:** fix imports and `close()`; run tests.
2. **Agree on contracts:** define record encoding, offsets, return values, and invalid-input behavior.
3. **Build in parallel:** Miguel works on `storage.py`, Lucía on `hash_index.py`, Miguelchi on tests; Hugo prepares integration and CI.
4. **Integrate:** Hugo joins the modules into `bbdd.py`, with support from the other three.
5. **Verify:** run tests, review pull requests, benchmark, and update the backlog status.

## 7. Out of Scope for This Iteration

- B or B+ trees
- SQL or query parsing
- General-purpose key-value or document objects
- Transactions, concurrency, or distributed storage
- Premature optimization beyond measuring the implemented version

## 8. Definition of Done

A task is complete when its code is merged, its agreed acceptance criteria pass, its tests run locally and in CI, and another team member has reviewed the change.
