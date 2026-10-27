# Product Backlog — Lightweight String Database

## 1. Project Overview

The goal of this project is to develop a lightweight, persistent database for **text strings** using Python.

The database should be simple to use, efficient for basic operations, and eventually capable of accessing stored data without loading every record into memory.

The **first iteration** provides an alphabetical directory with string insertion, searching, deletion, and JSON-based persistence. A **planned second iteration** will introduce an append-only log file and an in-memory hash index with file offsets. More advanced features may be implemented in later phases.

### Main Objectives

- Provide fast string insertion, searching, and deletion.
- Preserve data between application restarts.
- Reduce unnecessary disk writes and memory usage.
- Keep the architecture simple and modular.
- Ensure reliability through automated testing.

## 2. Product Backlog

User stories are written with the INVEST principles in mind and prioritized using the MoSCoW method.

Story points are preliminary estimates and should be validated by the development team.

### Development Status Definitions

| Status | Meaning |
|---|---|
| **DONE** | Implemented, verified against all acceptance criteria, reviewed, and merged. |
| **PARTIAL** | Basic functionality exists, but at least one acceptance criterion is not yet met. |
| **IN PROGRESS** | Work has begun, but the feature is not ready for acceptance. |
| **PLANNED** | Agreed upon but not started. |
| **BLOCKED** | Cannot proceed until another task or decision is completed. |
| **OUT OF SCOPE (E1)** | Intentionally excluded from the initial delivery; not necessarily excluded from the project. |

> **Important:** A method existing in the code does not make a story DONE. Status is based on its complete acceptance criteria. The six existing tests pass locally and in GitHub Actions, but they test the Iteration 1 alphabetical implementation. A passing CI run does not mean the append-only storage engine has been implemented or tested.

| ID | User Story | Priority | Story Points | Development Status | Current State |
|---|---|---|---:|---|---|
| US-01 | As a user, I want to store a string so that I can access it later. | Must | 3 | **PARTIAL** | `insert(word)` works with the in-memory alphabetical buckets, but writes the entire JSON file rather than appending a record. |
| US-02 | As a user, I want to find a stored string so that I can check whether it exists. | Must | 3 | **PARTIAL** | `search(word)` checks the relevant alphabetical bucket, not a disk-offset hash index. |
| US-03 | As a user, I want to delete a stored string so that it is no longer available. | Must | 3 | **PARTIAL** | `delete(word)` removes a string and rewrites JSON; there are no deletion markers yet. |
| US-04 | As a user, I want my strings to remain available after restarting the application so that they are not lost. | Must | 5 | **PARTIAL** | JSON persistence exists, but append-only replay and index reconstruction are not implemented. |
| US-05 | As a developer, I want automated unit tests so that I can verify database operations. | Must | 3 | **IN PROGRESS** | `tests.py` imports `AlphabeticalDirectory` from `bbdd.py` and all six tests pass (insertion, search, deletion, collisions, duplicates, persistence). They still assert the old bucket positions and read `directory.table`, so they must be rewritten against the public interface for Iteration 2. |
| US-06 | As a developer, I want tests to run automatically on GitHub so that errors are detected before changes are merged. | Must | 2 | **DONE** | `.github/workflows/tests.yml` runs `pytest` on every push and pull request. The latest run, on commit `3348f4f`, passed. |
| US-07 | As a user, I want duplicate insertions to have a predictable result so that no duplicate active strings are created. | Should | 2 | **PARTIAL** | The current implementation avoids duplicates in memory; this must be retained and tested with the new storage engine. |
| US-08 | As a user, I want invalid inputs to be handled predictably so that incorrect operations do not corrupt the database. | Should | 3 | **PLANNED** | Agreed policy (see `TASKS.md` §2): inserts are case-sensitive, accept UTF-8 and are stored in NFC form; search ignores case and accents (but not `ñ`) unless `-c` is given; empty strings and non-strings are rejected. Not implemented yet. |
| US-09 | As a user, I want the database to recover from an incomplete final record so that an interrupted write does not prevent startup. | Should | 5 | **PLANNED** | Incomplete-write recovery is not implemented. |
| US-10 | As a user, I want obsolete records to be compacted so that disk space is not unnecessarily wasted. | Could | 8 | **PLANNED** | Compaction is deferred until append-only storage exists. |
| US-11 | As a user, I want an ordered index using a B+ tree so that I can efficiently search strings within a range. | Won't (E1) | 13 | **OUT OF SCOPE (E1)** | An in-memory hash index is planned first. |
| US-12 | As a user, I want to execute SQL-like queries so that I can interact with the database using a query language. | Won't (E1) | 13 | **OUT OF SCOPE (E1)** | Not included in the initial delivery. |

## 3. Acceptance Criteria

### US-01 — Store Strings
- The database accepts a valid text string.
- A new insertion is appended to the storage file without rewriting earlier records.
- The index stores the inserted string's file offset.
- The string can be found immediately after insertion.

### US-02 — Find Strings
- Existing strings can be found using the index.
- Search returns a list of byte offsets; missing strings produce an empty list.
- Searching does not require scanning all stored records (O(1) with the index enabled, verified with the storage's own `records_read` counter with the index on and off).
- By default, search ignores case and accents (but not `ñ`) and can return several matches, such as `"boat"` and `"Boat"`; with `-c` (`case_sensitive=True`) it requires an exact match.

### US-03 — Delete Strings
- Existing strings can be deleted.
- A deletion marker is appended to the storage file.
- Deleted strings are removed from the active index.
- A deleted string is no longer found, including after restart.

### US-04 — Data Persistence
- Strings remain available after restarting the application.
- The in-memory hash index is reconstructed from the storage file at startup.
- Deleted strings remain logically deleted after restart.
- Duplicate insertions do not create multiple active entries.

### US-05 — Unit Testing
- Tests cover insertion, searching, deletion, and persistence.
- Tests cover missing strings and repeated operations.
- Tests run successfully using `pytest`.

### US-06 — Continuous Integration
- GitHub Actions runs the test suite automatically.
- Tests run on pull requests targeting `main`.
- Failed tests are reported by the workflow.
- The workflow succeeds when all tests pass.

### US-07 — Duplicate Handling
- Inserting an existing string does not create another active entry.
- Searching still returns the existing string's recorded location or agreed result.
- Behavior is consistent after restarting.

### US-08 — Input Validation
- Non-string inputs are rejected with clear errors.
- Empty strings are handled according to a documented policy.
- Invalid operations do not modify stored data.
- Unicode (UTF-8) characters are handled consistently.

### US-09 — Incomplete Write Recovery
- Startup detects an incomplete final record.
- Previously completed records remain accessible.
- Recovery does not silently ignore corruption in earlier records.

### US-10 — Storage Compaction
- Compaction removes obsolete or deleted records.
- All active strings remain available.
- The index is correctly rebuilt or updated after compaction.
- The compacted file is not larger than the original file.

### US-11 — B+ Tree Index
- Strings are maintained in sorted key order.
- Searching for existing strings returns the correct results.
- Range queries return matching strings in order.
- Node splitting preserves the tree's structural invariants.

### US-12 — SQL-like Query Interface
- The database accepts a documented subset of SQL-like commands.
- Supported commands produce the same results as the underlying database operations.
- Invalid commands produce understandable errors.

## 4. Priority Summary

| Priority | Stories | Story Points |
|---|---|---:|
| Must Have | US-01 to US-06 | 19 |
| Should Have | US-07 to US-09 | 10 |
| Could Have | US-10 | 8 |
| Won't Have (E1) | US-11 to US-12 | 26 |
| **Total** | **12 stories** | **63** |

Must-have stories account for approximately **30% of the total estimated story points**, based on preliminary estimates. This percentage does not mean that 30% of the work is complete.

The Won't Have category refers to the first delivery, not necessarily the entire project.

## 5. Development Progress

### Iteration 1 — Basic Alphabetical Directory

**Current implementation:** `bbdd.py` uses 26 alphabetical buckets in memory, saves them as JSON, and supports the public operations `insert(word)`, `search(word)`, and `delete(word)`.

**Implemented in the initial prototype:**
- String insertion and duplicate checks.
- String lookup within the bucket selected by the first character.
- String deletion.
- Saving/loading the directory as JSON.
- Six pytest tests in `tests.py`, passing locally and in CI.
- GitHub Actions workflow (`.github/workflows/tests.yml`) running the tests on every push and pull request.
- A first benchmark script in `benchmarks/compare.py`.

**Fixes completed before parallel development:**
- `tests.py` now imports from `bbdd` instead of the nonexistent `directory` module.
- `close()` no longer references the undefined `self.db` attribute. It is currently a no-op because every write uses a `with` block that closes the file.

**Known limitations:**
- The entire database is loaded into RAM.
- Insertions and deletions rewrite the entire JSON file.
- Lookups are linear within each bucket.
- Empty strings and strings not starting with a letter are not validated (the bucket index can be out of range).
- `benchmarks/compare.py` labels the current `AlphabeticalDirectory` as "Append-only", but it still rewrites JSON. The label must be fixed, or the comparison deferred until the new engine exists.

### Iteration 2 — Storage and Indexing Improvements (Planned)

- Implement an append-only storage layer (`storage.py`) with byte offsets, using one JSON record per line in a new `data.log` file.
- Replace the 26-bucket structure with an in-memory dictionary mapping strings to offsets (`hash_index.py`).
- Rebuild the index by replaying the storage log when opening the database.
- Preserve the simple string-only public API. `insert()` will return the record's byte offset instead of a bucket position, `search()` a list of offsets (`[]` when nothing matches, instead of `-1`), and `delete()` `True`/`False`. `delete()` matches the exact string only.
- Make search case- and accent-insensitive by default (keeping `ñ` distinct), with a `-c` flag for exact search.
- Add a command-line interface with `argparse`.
- Add a flag to disable the index (`use_index=False` / `--no-cache`), so that a sequential O(n) scan can be compared with the O(1) indexed search.
- Rewrite and extend the pytest suite against the public interface, including persistence and deletion-after-restart tests.
- ~~Configure GitHub Actions for continuous integration.~~ Done in Iteration 1.
- Measure insertion and search performance against Iteration 1.

The agreed module interfaces, record format and allowed modules are in `TASKS.md` §2.

> A feature moves to **DONE** only when its acceptance criteria pass, tests have been verified, and the change has been reviewed and merged.

## 6. Definition of Done

A user story is complete when:

1. Its acceptance criteria have been satisfied.
2. Appropriate automated tests exist.
3. All relevant tests pass locally and in GitHub Actions.
4. Code has been reviewed and approved by another team member.
5. Changes have been merged into `main` through a pull request.
6. Documentation has been updated where necessary.

## 7. Initial Delivery — E1

**Deadline: November 3, 2026**

Target deliverables:
- Validated and prioritized product backlog.
- Documented story point estimates.
- Functional append-only string storage with `insert`, `search`, and `delete`.
- Automatic in-memory hash index reconstruction on startup.
- Unit tests using `pytest`.
- Working GitHub Actions workflow.

Advanced indexing, compaction, and query-language support are deferred until later phases.

## 8. Technical Constraints

- **Programming language:** Python 3.
- **Stored data:** Text strings only in the current scope.
- **Current storage:** JSON file rewritten on changes.
- **Planned storage:** Local append-only file (`data.log`, JSON Lines, opened in binary mode so offsets are byte positions).
- **Current indexing:** 26 alphabetical buckets in memory.
- **Planned indexing:** In-memory dictionary mapping strings to byte offsets.
- **Testing:** pytest.
- **Version control:** Git and GitHub.
- **Continuous integration:** GitHub Actions (implemented; Python 3.12, runs on every push and pull request).
- **External dependencies:** Minimized wherever possible.

This is an educational project. Simplicity, correctness, maintainability, and measured performance take priority over unnecessary features.
