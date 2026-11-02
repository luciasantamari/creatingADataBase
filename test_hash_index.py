from hash_index import HashIndex, normalize


def test_normalize():
    assert normalize("Canción") == "cancion"
    assert normalize("AÑO") == "año"


def test_find_existing():
    index = HashIndex()
    index.add("hola", 10)
    assert index.find("hola") == [10]
    assert index.find("hola", case_sensitive=True) == [10]


def test_accents_and_case():
    index = HashIndex()
    index.add("canción", 5)
    index.add("año", 20)
    assert index.find("CANCION") == [5]
    assert index.find("CANCION", case_sensitive=True) == []
    assert index.find("ano") == []


def test_boat_and_Boat():
    index = HashIndex()
    index.add("boat", 100)
    index.add("Boat", 40)
    assert index.find("BOAT") == [40, 100]


def test_duplicate_insert():
    index = HashIndex()
    index.add("sol", 1)
    index.add("sol", 99)
    assert index.find("sol") == [99]


def test_remove_and_missing():
    index = HashIndex()
    index.add("luna", 7)
    index.remove("luna")
    assert index.find("luna") == []
    assert index.find("nunca_existio") == []


def test_rebuild_insert_then_delete():
    index = HashIndex()
    records = [
        (0, "a", False),
        (10, "b", False),
        (20, "a", True),
        (30, "c", False),
    ]
    index.rebuild(records)
    assert index.find("a") == []
    assert index.find("b") == [10]
    assert index.find("c") == [30]