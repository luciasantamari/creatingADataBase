import json
import lmdb

SEP = "/"  # separates the levels of a branch, e.g. "clientes/vip"


class BranchDB:
    """
    Every leaf is stored in LMDB under its full path ("branch/sub-branch/leaf")
    and its value is a dict (key-value) saved as JSON.

    A branch is just a path prefix: it exists while it has at least one leaf.
    LMDB keeps its keys sorted, so all the leaves of a branch sit together and
    can be read in one sweep.
    """

    def __init__(self, filename="data"):
        # map_size = maximum size of the database (1 GB is plenty to start with)
        self.env = lmdb.open(filename, map_size=2**30)

    def close(self):
        self.env.close()

    # ------------------------------------------------------------ helpers

    def _prefix(self, branch):
        """'clientes/vip' -> b'clientes/vip/' (the final '/' keeps 'cliente' apart from 'clientes')."""
        branch = (branch or "").strip(SEP)
        if not branch:
            raise ValueError("The branch cannot be empty")
        return (branch + SEP).encode()

    def _key(self, branch, key):
        """('clientes/vip', 'luis') -> b'clientes/vip/luis'"""
        if not key:
            raise ValueError("The key cannot be empty")
        if SEP in key:
            raise ValueError(f"The key cannot contain '{SEP}' (use a sub-branch instead)")
        return self._prefix(branch) + key.encode()

    def _scan(self, txn, prefix):
        """Yield (key, value) of every leaf under prefix: jump to the first one, read until it stops matching."""
        cursor = txn.cursor()
        if cursor.set_range(prefix):
            for k, v in cursor:
                if not k.startswith(prefix):
                    break
                yield k, v

    # ------------------------------------------------------------ main methods

    def insert(self, branch, key, value):
        """
        Insert a leaf (key -> dict of key-values) in a branch.
        The branch is created if it doesn't exist.
        Returns True if inserted, False if that leaf already exists (use update to change it).
        """
        if not isinstance(value, dict):
            raise ValueError("The value of a leaf must be a dict (key-value)")
        with self.env.begin(write=True) as txn:
            return txn.put(self._key(branch, key), json.dumps(value).encode(), overwrite=False)

    def search(self, branch, key=None):
        """
        search("clientes", "juan")  -> the value of that leaf, or None if it doesn't exist
        search("clientes")          -> {path: value} of everything inside the branch (sub-branches included)
        """
        with self.env.begin() as txn:
            if key is not None:
                data = txn.get(self._key(branch, key))
                return json.loads(data) if data is not None else None
            return {k.decode(): json.loads(v) for k, v in self._scan(txn, self._prefix(branch))}

    def delete(self, branch, key=None):
        """
        delete("clientes", "juan")  -> deletes that leaf
        delete("clientes")          -> deletes the whole branch with everything inside it
        Returns how many leaves were deleted. A branch left without leaves disappears by itself.
        """
        with self.env.begin(write=True) as txn:
            if key is not None:
                return int(txn.delete(self._key(branch, key)))
            keys = [k for k, _ in self._scan(txn, self._prefix(branch))]
            for k in keys:
                txn.delete(k)
            return len(keys)

    def update(self, branch, key=None, value=None, new_branch=None):
        """
        update("clientes", "juan", {"tel": "699"})     -> updates a LEAF: adds/changes those key-values, keeps the rest
        update("clientes", new_branch="clientes_vip")  -> updates a BRANCH: renames it, its leaves move with it
        Returns True if updated, False if not found (or if new_branch already exists).
        """
        with self.env.begin(write=True) as txn:
            if key is not None:  # ---- leaf
                k = self._key(branch, key)
                current = txn.get(k)
                if current is None:
                    return False
                data = json.loads(current)
                data.update(value)
                txn.put(k, json.dumps(data).encode())
                return True

            # ---- branch
            old, new = self._prefix(branch), self._prefix(new_branch)
            leaves = list(self._scan(txn, old))
            if not leaves or list(self._scan(txn, new)):
                return False  # the branch doesn't exist, or the new name is already taken
            for k, v in leaves:
                txn.delete(k)
                txn.put(new + k[len(old):], v)
            return True


if __name__ == "__main__":
    db = BranchDB("data")

    # INSERT: the branches are created on the fly
    db.insert("clientes", "juan", {"tel": "600111222", "ciudad": "Madrid"})
    db.insert("clientes", "ana", {"tel": "600333444", "ciudad": "Sevilla"})
    db.insert("clientes/vip", "luis", {"tel": "600555666", "ciudad": "Madrid"})  # a more specific branch
    db.insert("ventas", "v001", {"cliente": "juan", "total": 120})
    print("insert repeated :", db.insert("clientes", "juan", {"tel": "0"}))  # False, it already exists

    # SEARCH
    print("one leaf        :", db.search("clientes", "juan"))
    print("whole branch    :", db.search("clientes"))
    print("not found       :", db.search("clientes", "pepe"))

    # UPDATE
    db.update("clientes", "juan", {"tel": "699999999"})  # leaf: only tel changes, ciudad stays
    db.update("ventas", new_branch="ventas_2026")        # branch: renamed
    print("updated leaf    :", db.search("clientes", "juan"))
    print("renamed branch  :", db.search("ventas_2026"))

    # DELETE
    db.delete("clientes", "ana")                         # one leaf
    print("after leaf delete:", db.search("clientes"))
    db.delete("clientes")                                # a whole branch
    db.delete("ventas_2026")
    print("after branch delete:", db.search("clientes"))

    db.close()
