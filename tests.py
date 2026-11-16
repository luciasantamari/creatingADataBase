"""Miguelchi — Beginner 2: Testing and Reliability.

Public API regression tests for AlphabeticalDirectory.

Expected contract: TASKS.md, E1 step 4. These tests are for the integrated
append-only engine; the old 26-bucket implementation will not pass them.
Run: python -m pytest -v tests.py test_storage.py test_hash_index.py
"""

import pytest

from bbdd import AlphabeticalDirectory


@pytest.fixture(params=[True, False], ids=["indexed", "sequential"])
def directory(tmp_path, request):
    database = AlphabeticalDirectory(
        filename=str(tmp_path / "data.log"), use_index=request.param
    )
    yield database
    database.close()


def test_insert_and_search_offsets(directory):
    first = directory.insert("boat")
    second = directory.insert("sail")
    assert first == 0
    assert second > first
    assert directory.search("boat") == [first]
    assert directory.search("sail") == [second]

def test_missing_search(directory):
    assert directory.search("missing") == []

def test_delete_and_missing_delete(directory):
    offset = directory.insert("sail")
    assert directory.search("sail") == [offset]
    assert directory.delete("sail") is True
    assert directory.search("sail") == []
    assert directory.delete("sail") is False

def test_multiple_words_no_bucket_assumptions(directory):
    offsets = [directory.insert(word) for word in ("boat", "banana", "book")]
    assert offsets == sorted(offsets)
    assert len(set(offsets)) == 3
    for word, offset in zip(("boat", "banana", "book"), offsets):
        assert directory.search(word, case_sensitive=True) == [offset]

def test_duplicate_does_not_append(directory, tmp_path):
    first = directory.insert("boat")
    file_path = tmp_path / "data.log"
    size_before = file_path.stat().st_size
    assert directory.insert("boat") == first
    assert file_path.stat().st_size == size_before
    assert directory.search("boat", case_sensitive=True) == [first]

def test_case_insensitive_and_exact_search(directory):
    lower = directory.insert("boat")
    upper = directory.insert("Boat")
    assert lower != upper
    assert directory.search("BOAT") == [lower, upper]
    assert directory.search("Boat", case_sensitive=True) == [upper]
    assert directory.search("BOAT", case_sensitive=True) == []

def test_accent_insensitive_default_but_exact_when_requested(directory):
    accent = directory.insert("canción")
    plain = directory.insert("cancion")
    assert directory.search("CANCION") == [accent, plain]
    assert directory.search("canción", case_sensitive=True) == [accent]
    assert directory.search("cancion", case_sensitive=True) == [plain]

def test_enye_remains_distinct(directory):
    year = directory.insert("año")
    assert directory.search("ANO") == []
    assert directory.search("AÑO") == [year]


def test_unicode_nfc_equivalence(directory, tmp_path):
    composed = directory.insert("canción")
    size_before = (tmp_path / "data.log").stat().st_size
    decomposed = directory.insert("cancio\u0301n")
    assert decomposed == composed
    assert (tmp_path / "data.log").stat().st_size == size_before
    assert directory.search("cancio\u0301n", case_sensitive=True) == [composed]


def test_exact_delete_only(directory):
    upper = directory.insert("Boat")
    lower = directory.insert("boat")
    assert directory.delete("boat") is True
    assert directory.search("boat") == [upper]
    assert directory.search("Boat", case_sensitive=True) == [upper]
    assert directory.search("boat", case_sensitive=True) == []
    assert directory.delete("boat") is False
    assert lower != upper


@pytest.mark.parametrize("word", ["", None, 42, ["boat"]])
def test_invalid_insert_does_not_write(directory, tmp_path, word):
    file_path = tmp_path / "data.log"
    before = file_path.stat().st_size if file_path.exists() else 0
    expected = ValueError if word == "" else TypeError
    with pytest.raises(expected):
        directory.insert(word)
    after = file_path.stat().st_size if file_path.exists() else 0
    assert after == before

@pytest.mark.parametrize("word", ["", None, 42])
def test_invalid_search_and_delete(directory, word):
    expected = ValueError if word == "" else TypeError
    with pytest.raises(expected):
        directory.search(word)
    with pytest.raises(expected):
        directory.delete(word)

@pytest.mark.parametrize("word", ["Ñandú", "你好 🌍", "a/b:c?", "hello world", "😀"])
def test_utf8_and_special_characters(directory, word):
    offset = directory.insert(word)
    assert directory.search(word, case_sensitive=True) == [offset]

@pytest.mark.parametrize("use_index", [True, False], ids=["indexed", "sequential"])
def test_restart_persistence(tmp_path, use_index):
    path = str(tmp_path / "data.log")
    first_db = AlphabeticalDirectory(path, use_index=use_index)
    offset = first_db.insert("canción")
    first_db.insert("boat")
    first_db.close()

    second_db = AlphabeticalDirectory(path, use_index=use_index)
    try:
        assert second_db.search("CANCION") == [offset]
    finally:
        second_db.close()

@pytest.mark.parametrize("use_index", [True, False], ids=["indexed", "sequential"])
def test_deletion_persists_after_restart(tmp_path, use_index):
    path = str(tmp_path / "data.log")
    first_db = AlphabeticalDirectory(path, use_index=use_index)
    first_db.insert("boat")
    surviving = first_db.insert("sail")
    assert first_db.delete("boat") is True
    first_db.close()

    second_db = AlphabeticalDirectory(path, use_index=use_index)
    try:
        assert second_db.search("boat") == []
        assert second_db.search("sail") == [surviving]
    finally:
        second_db.close()

@pytest.mark.parametrize("use_index", [True, False], ids=["indexed", "sequential"])
def test_appended_records_and_reinsertion(tmp_path, use_index):
    path = str(tmp_path / "data.log")
    db = AlphabeticalDirectory(path, use_index=use_index)
    old = db.insert("old")
    removed = db.insert("remove")
    for i in range(10):
        db.insert(f"item{i}")
    assert db.delete("remove") is True
    new = db.insert("remove")
    assert new > removed
    assert db.search("old", case_sensitive=True) == [old]
    assert db.search("remove", case_sensitive=True) == [new]
    db.close()

    reopened = AlphabeticalDirectory(path, use_index=use_index)
    try:
        assert reopened.search("old", case_sensitive=True) == [old]
        assert reopened.search("remove", case_sensitive=True) == [new]
        assert reopened.search("item9", case_sensitive=True)
    finally:
        reopened.close()


@pytest.mark.parametrize("size", [100, 1000])
def test_index_reads_zero_records_vs_scan_reads_n(tmp_path, size):
    """Measure record decoding, not elapsed time (stable across CI machines)."""
    path = str(tmp_path / "data.log")
    writer = AlphabeticalDirectory(path, use_index=True)
    offsets = [writer.insert(f"word{i}") for i in range(size)]
    writer.close()

    indexed = AlphabeticalDirectory(path, use_index=True)
    sequential = AlphabeticalDirectory(path, use_index=False)
    try:
        indexed_before = indexed.storage.records_read
        indexed_result = indexed.search(f"word{size - 1}")
        indexed_delta = indexed.storage.records_read - indexed_before

        sequential_before = sequential.storage.records_read
        sequential_result = sequential.search(f"word{size - 1}")
        sequential_delta = sequential.storage.records_read - sequential_before

        assert indexed_result == sequential_result == [offsets[-1]]
        assert indexed_delta == 0
        assert sequential_delta == size
    finally:
        indexed.close()
        sequential.close()
