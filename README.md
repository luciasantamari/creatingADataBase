# Product Backlog — Lightweight Key-Value Database

## 1. Project Overview

The goal of this project is to develop a lightweight, persistent key-value database using Python.

The database should be simple to use, efficient for basic operations, and capable of storing data without loading all records into memory.

The initial version will use an append-only log file and an in-memory hash index. More advanced features may be implemented in later development phases.

### Main Objectives

- Provide fast key-value storage and retrieval.
- Preserve data between application restarts.
- Minimize memory usage.
- Keep the architecture simple and modular.
- Ensure reliability through automated testing.

## 2. Product Backlog

User stories follow the INVEST principles and are prioritized using the MoSCoW method.

Story points are preliminary estimates that should be validated by the development team.

| ID | User Story | Priority | Story Points |
|---|---|---|---:|
| US-01 | As a user, I want to store a key-value pair so that I can save information for later use. | Must | 3 |
| US-02 | As a user, I want to retrieve a value using its key so that I can access stored information quickly. | Must | 3 |
| US-03 | As a user, I want to delete a key-value pair so that I can remove information I no longer need. | Must | 3 |
| US-04 | As a user, I want my data to remain available after restarting the application so that I do not lose previously stored records. | Must | 5 |
| US-05 | As a developer, I want automated unit tests so that I can verify the database operations behave correctly. | Must | 3 |
| US-06 | As a developer, I want tests to run automatically on GitHub so that errors are detected before changes are merged. | Must | 2 |
| US-07 | As a user, I want to update an existing key so that I can modify information without creating duplicate active entries. | Should | 2 |
| US-08 | As a user, I want invalid inputs to be handled predictably so that incorrect operations do not corrupt the database. | Should | 3 |
| US-09 | As a user, I want the database to recover from an incomplete final record so that an interrupted write does not prevent startup. | Should | 5 |
| US-10 | As a user, I want obsolete records to be compacted so that the database does not waste unnecessary disk space. | Could | 8 |
| US-11 | As a user, I want an ordered index using a B+ tree so that I can efficiently search for keys within a range. | Won't (E1) | 13 |
| US-12 | As a user, I want to execute SQL-like queries so that I can interact with the database using a query language. | Won't (E1) | 13 |

## 3. Acceptance Criteria

### US-01 — Store Data
- The database accepts a valid key-value pair.
- The record is appended to the storage file.
- The hash index stores the record's file offset.
- The stored value can be retrieved immediately.

### US-02 — Retrieve Data
- Existing keys return their corresponding values.
- Missing keys return `None`.
- Retrieval uses the hash index rather than scanning the entire file.

### US-03 — Delete Data
- Existing keys can be deleted.
- A deletion marker is appended to the storage file.
- Deleted keys are removed from the active index.
- Retrieving a deleted key returns `None`.

### US-04 — Data Persistence
- Records remain available after restarting the application.
- The hash index is reconstructed from the storage file during startup.
- Deleted records remain logically deleted after restarting.
- The latest value of each key is recovered.

### US-05 — Unit Testing
- Tests cover insertion, retrieval, deletion, and persistence.
- Tests cover missing keys and repeated operations.
- Tests run successfully using `pytest`.

### US-06 — Continuous Integration
- GitHub Actions executes the test suite automatically.
- Tests run on pull requests targeting `main`.
- Failed tests are reported by the workflow.
- The workflow succeeds when all tests pass.

### US-07 — Update Existing Records
- Storing an existing key updates its current value.
- Retrieval returns the latest value.
- The index references the latest record.
- The updated value survives an application restart.

### US-08 — Input Validation
- Unsupported key types are rejected with a clear error.
- Values that cannot be serialized are rejected.
- A rejected operation does not modify the database.

### US-09 — Incomplete Write Recovery
- Startup detects an incomplete final record.
- Previously completed records remain accessible.
- Recovery does not silently ignore corruption in earlier records.

### US-10 — Storage Compaction
- Compaction removes obsolete and deleted records.
- The latest value of each active key is preserved.
- The index remains valid after compaction.
- The compacted file is not larger than the original file.

### US-11 — B+ Tree Index
- Keys are maintained in sorted order.
- Searching for existing keys returns the correct records.
- Range queries return matching records in order.
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

Must-have stories represent approximately **30% of the estimated total effort**, remaining below the 60% threshold discussed in class.

The Won't Have category refers to the first delivery, not necessarily to the entire project.

## 5. Definition of Done

A user story is considered complete when:

1. Its acceptance criteria have been satisfied.
2. The implementation includes appropriate unit tests.
3. All automated tests pass locally and in GitHub Actions.
4. The code has been reviewed and approved by another team member.
5. The changes have been merged into `main` through a pull request.
6. Any necessary documentation has been updated.

## 6. Initial Delivery — E1

**Deadline: November 3, 2026**

The first delivery focuses on the minimum functional database.

Required deliverables:

- Validated and prioritized product backlog.
- Documented story point estimates.
- Functional append-only storage with `set`, `get`, and `delete`.
- Automatic hash index reconstruction on startup.
- Unit tests using `pytest`.
- Working GitHub Actions continuous integration workflow.

Advanced indexing, compaction, and query language support are deferred until later phases.

## 7. Technical Constraints

- **Programming language:** Python 3.
- **Storage:** Local append-only file.
- **Indexing:** In-memory hash index.
- **Testing:** pytest.
- **Version control:** Git and GitHub.
- **Continuous integration:** GitHub Actions.
- **External dependencies:** Minimized wherever possible.

The database is intended primarily as an educational project. Simplicity, correctness, maintainability, and measured performance take priority over unnecessary features.
