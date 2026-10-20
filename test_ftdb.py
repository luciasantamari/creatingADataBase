import pytest
from ftdb import BranchDB


@pytest.fixture
def db(tmp_path):
    d = BranchDB(str(tmp_path / "test_db"))
    yield d
    d.close()


# ------------------------------------------------------------ _key

def test_key_simple_branch(db):
    assert db._key("clientes", "juan") == b"clientes/juan"


def test_key_nested_branch(db):
    assert db._key("clientes/vip", "luis") == b"clientes/vip/luis"


def test_key_strips_slashes_of_branch(db):
    assert db._key("/clientes/vip/", "luis") == b"clientes/vip/luis"


def test_key_keeps_similar_branches_apart(db):
    # "cliente" must not be a prefix of "clientes"
    assert not db._key("clientes", "a").startswith(db._prefix("cliente"))


def test_key_accents_and_symbols(db):
    assert db._key("clientes", "muñoz@€") == "clientes/muñoz@€".encode()


@pytest.mark.parametrize("branch", ["", None, "/", "///"])
def test_key_empty_branch(db, branch):
    with pytest.raises(ValueError):
        db._key(branch, "juan")


def test_key_empty_key(db):
    with pytest.raises(ValueError):
        db._key("clientes", "")


def test_key_with_separator(db):
    with pytest.raises(ValueError):
        db._key("clientes", "vip/luis")


# ------------------------------------------------------------ delete

def test_delete_leaf(db):
    db.insert("clientes", "juan", {"tel": "600"})

    assert db.delete("clientes", "juan") == 1
    assert db.search("clientes", "juan") is None


def test_delete_leaf_not_found(db):
    assert db.delete("clientes", "pepe") == 0


def test_delete_leaf_keeps_the_rest(db):
    db.insert("clientes", "juan", {"tel": "600"})
    db.insert("clientes", "ana", {"tel": "700"})

    db.delete("clientes", "juan")

    assert db.search("clientes", "ana") == {"tel": "700"}
    assert db.search("clientes", "juan") is None


def test_delete_branch_returns_count(db):
    db.insert("clientes", "juan", {"tel": "600"})
    db.insert("clientes", "ana", {"tel": "700"})

    assert db.delete("clientes") == 2
    assert db.search("clientes") == {}


def test_delete_branch_includes_subbranches(db):
    db.insert("clientes", "juan", {"tel": "600"})
    db.insert("clientes/vip", "luis", {"tel": "800"})

    assert db.delete("clientes") == 2
    assert db.search("clientes/vip") == {}


def test_delete_subbranch_keeps_parent(db):
    db.insert("clientes", "juan", {"tel": "600"})
    db.insert("clientes/vip", "luis", {"tel": "800"})

    assert db.delete("clientes/vip") == 1
    assert db.search("clientes", "juan") == {"tel": "600"}


def test_delete_branch_does_not_touch_similar_name(db):
    db.insert("clientes", "juan", {"tel": "600"})
    db.insert("clientes_vip", "luis", {"tel": "800"})
    db.insert("cliente", "ana", {"tel": "700"})

    db.delete("clientes")

    assert db.search("clientes_vip", "luis") == {"tel": "800"}
    assert db.search("cliente", "ana") == {"tel": "700"}


def test_delete_branch_not_found(db):
    assert db.delete("inexistente") == 0


def test_delete_branch_does_not_affect_other_branches(db):
    db.insert("clientes", "juan", {"tel": "600"})
    db.insert("ventas", "v001", {"total": 120})

    db.delete("clientes")

    assert db.search("ventas", "v001") == {"total": 120}


def test_delete_twice(db):
    db.insert("clientes", "juan", {"tel": "600"})

    assert db.delete("clientes", "juan") == 1
    assert db.delete("clientes", "juan") == 0


def test_delete_then_insert_again(db):
    db.insert("clientes", "juan", {"tel": "600"})
    db.delete("clientes", "juan")

    assert db.insert("clientes", "juan", {"tel": "999"}) is True
    assert db.search("clientes", "juan") == {"tel": "999"}


def test_delete_empty_branch_raises(db):
    with pytest.raises(ValueError):
        db.delete("")


def test_delete_persists_after_restart(tmp_path):
    path = str(tmp_path / "test_db")

    db1 = BranchDB(path)
    db1.insert("clientes", "juan", {"tel": "600"})
    db1.insert("clientes", "ana", {"tel": "700"})
    db1.delete("clientes", "juan")
    db1.close()

    db2 = BranchDB(path)
    try:
        assert db2.search("clientes", "juan") is None
        assert db2.search("clientes", "ana") == {"tel": "700"}
    finally:
        db2.close()
