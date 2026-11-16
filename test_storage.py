"""Miguelchi — standalone Storage contract tests.

Run: python -m pytest -v test_storage.py
These can run before bbdd.py is integrated.
"""

import json
import unicodedata

import pytest

from storage import Storage


@pytest.fixture
def storage(tmp_path):
    return Storage(str(tmp_path / "data.log"))


def test_missing_file_has_no_records(storage):
    assert list(storage.records()) == []
    assert storage.records_read == 0


def test_append_offsets_and_direct_read(storage):
    first = storage.append("boat")
    second = storage.append("sail")
    assert first == 0
    assert second > first
    assert storage.read(second) == "sail"
    assert storage.read(first) == "boat"
    assert storage.records_read == 2


def test_byte_offsets_with_utf8(storage, tmp_path):
    first = storage.append("canción")
    second = storage.append("你好")
    data = (tmp_path / "data.log").read_bytes()
    assert first == 0
    assert second == data.index(b"\n") + 1
    assert storage.read(second) == "你好"


def test_nfc_normalization(storage):
    storage.append("cancio\u0301n")
    assert storage.read(0) == unicodedata.normalize("NFC", "cancio\u0301n")


def test_json_lines_and_deletion_marker(storage, tmp_path):
    first = storage.append("boat")
    marker = storage.append("boat", deleted=True)
    raw = (tmp_path / "data.log").read_bytes()
    assert raw.endswith(b"\n")
    parsed = [json.loads(line) for line in raw.splitlines()]
    assert parsed == [
        {"word": "boat", "deleted": False},
        {"word": "boat", "deleted": True},
    ]
    assert list(storage.records()) == [
        (first, "boat", False),
        (marker, "boat", True),
    ]


def test_append_only_preserves_earlier_records(storage, tmp_path):
    storage.append("old")
    original = (tmp_path / "data.log").read_bytes()
    storage.append("new")
    storage.append("old", deleted=True)
    assert (tmp_path / "data.log").read_bytes().startswith(original)
    assert storage.read(0) == "old"


def test_persistence_after_reopening(tmp_path):
    path = str(tmp_path / "data.log")
    writer = Storage(path)
    first = writer.append("Ñandú")
    second = writer.append("hello 🌍")
    reader = Storage(path)
    assert list(reader.records()) == [
        (first, "Ñandú", False),
        (second, "hello 🌍", False),
    ]
    assert reader.records_read == 2


@pytest.mark.parametrize("word, exception", [("", ValueError), (None, TypeError), (1, TypeError)])
def test_append_rejects_invalid_word_without_writing(storage, tmp_path, word, exception):
    storage.append("first")
    before = (tmp_path / "data.log").read_bytes()
    with pytest.raises(exception):
        storage.append(word)
    assert (tmp_path / "data.log").read_bytes() == before


@pytest.mark.parametrize("deleted", [None, 0, 1, "true"])
def test_append_rejects_invalid_deleted_type(storage, tmp_path, deleted):
    with pytest.raises(TypeError):
        storage.append("boat", deleted=deleted)
    assert not (tmp_path / "data.log").exists()


@pytest.mark.parametrize(
    "bad_line",
    [
        b'{"word":"boat","deleted":false}',  # incomplete final line
        b"\xff\n",  # non UTF-8
        b"{bad json}\n",
        b"[]\n",
        b"null\n",
        b'{"deleted":false}\n',
        b'{"word":"boat"}\n',
        b'{"word":"","deleted":false}\n',
        b'{"word":8,"deleted":false}\n',
        b'{"word":"boat","deleted":0}\n',
        b'{"word":"boat","deleted":"false"}\n',
    ],
)
def test_malformed_record_reports_byte_offset(tmp_path, bad_line):
    path = tmp_path / "data.log"
    writer = Storage(str(path))
    writer.append("valid")
    bad_offset = path.stat().st_size
    with path.open("ab") as handle:
        handle.write(bad_line)
    reader = Storage(str(path))
    with pytest.raises(ValueError, match=f"offset {bad_offset}"):
        list(reader.records())
    with pytest.raises(ValueError, match=f"offset {bad_offset}"):
        reader.read(bad_offset)


def test_read_past_end_reports_offset(storage, tmp_path):
    storage.append("boat")
    end_offset = (tmp_path / "data.log").stat().st_size
    with pytest.raises(ValueError, match=f"offset {end_offset}"):
        storage.read(end_offset)


def test_records_read_counter_on_scan_and_direct_read(storage):
    """The counter measures decoded records, not the number of queries."""
    offsets = [storage.append(word) for word in ("boat", "sail", "canción")]
    assert storage.records_read == 0  # append() does not read records
    assert list(storage.records()) == [
        (offsets[0], "boat", False),
        (offsets[1], "sail", False),
        (offsets[2], "canción", False),
    ]
    assert storage.records_read == 3
    assert storage.read(offsets[1]) == "sail"
    assert storage.records_read == 4