from directory import AlphabeticalDirectory


def test_insert(tmp_path):
    file = tmp_path / "test_data.txt"
    directory = AlphabeticalDirectory(file)

    directory.insert("boat")

    assert directory.search("boat") == 0


def test_search_not_found(tmp_path):
    file = tmp_path / "test_data.txt"
    directory = AlphabeticalDirectory(file)

    assert directory.search("sail") == -1


def test_delete(tmp_path):
    file = tmp_path / "test_data.txt"
    directory = AlphabeticalDirectory(file)

    directory.insert("sail")
    assert directory.search("sail") == 0

    directory.delete("sail")

    assert directory.search("sail") == -1


def test_multiple_words_same_letter(tmp_path):
    file = tmp_path / "test_data.txt"
    directory = AlphabeticalDirectory(file)

    directory.insert("boat")
    directory.insert("banana")
    directory.insert("book")

    assert directory.search("boat") == 0
    assert directory.search("banana") == 1
    assert directory.search("book") == 2


def test_no_duplicates(tmp_path):
    file = tmp_path / "test_data.txt"
    directory = AlphabeticalDirectory(file)

    directory.insert("boat")
    directory.insert("boat")

    index = directory._hash_letter("boat")

    assert directory.table[index].count("boat") == 1


def test_persistence(tmp_path):
    file = tmp_path / "test_data.txt"

    directory1 = AlphabeticalDirectory(file)
    directory1.insert("boat")

    directory2 = AlphabeticalDirectory(file)

    assert directory2.search("boat") == 0
