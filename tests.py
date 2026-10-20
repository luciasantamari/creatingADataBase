import pytest
from bbdd import AlphabeticalDirectory


@pytest.fixture 
def directory(tmp_path):
    d= AlphabeticalDirectory(str(tmp_path/"test_db"))
    yield d
    d.close()
   
                             
def test_insert(directory):
    directory.insert("boat")

    assert directory.search("boat") == 0


def test_search_not_found(directory):
    assert directory.search("sail") == -1


def test_delete(directory):
    directory.insert("sail")
    assert directory.search("sail") == 0

    directory.delete("sail")

    assert directory.search("sail") == -1


def test_multiple_words_same_letter(directory):
    
    directory.insert("boat")
    directory.insert("banana")
    directory.insert("book")

    assert directory.search("boat") == 0
    assert directory.search("banana") == 1
    assert directory.search("book") == 2


def test_no_duplicates(directory):
    directory.insert("boat")
    directory.insert("boat")

    index = directory._hash_letter("boat")

    assert directory.table[index].count("boat") == 1


def test_persistence(tmp_path):
    path = str(tmp_path / "test_db")

    directory1 = AlphabeticalDirectory(path)
    directory1.insert("boat")
    directory1.close()

    directory2 = AlphabeticalDirectory(path)
    try:
        assert directory2.search("boat") == 0
    finally:
        directory2.close()
    
