import json
import lmdb


class AlphabeticalDirectory:
    def __init__(self, filename="data"):
        self.filename = filename
        self.size = 26
        self.table = [[] for _ in range(self.size)]
        
        self.db = lmdb.open(filename)
        
        loaded_data = self.load(self.db, "directory")
        if loaded_data is not None:
            self.table = loaded_data

    def close(self):
        self.db.close()
        
    def _hash_letter(self, word):
        """Maps the first letter to index 0-25."""
        return ord(word[0].lower()) - 97

    def save(self, db, key, dictionary):
        with db.begin(write=True) as transaction:
            transaction.put(
                key.encode("utf-8"), 
                json.dumps(dictionary).encode("utf-8")
            )

    def load(self, db, key):
        with db.begin() as transaction:
            data = transaction.get(key.encode("utf-8"))
            
        if data is None:
            return None
        
        return json.loads(data.decode("utf-8"))

    def insert(self, word):
        index = self._hash_letter(word)

        if word in self.table[index]:
            return self.table[index].index(word)

        self.table[index].append(word)
        self.save(self.db, "directory", self.table)

        return len(self.table[index]) - 1

    def search(self, word):
        index = self._hash_letter(word)
        bucket = self.table[index]
        return bucket.index(word) if word in bucket else -1

    def delete(self, word):
        index = self._hash_letter(word)
        if word in self.table[index]:
            self.table[index].remove(word)
            self.save(self.db, "directory", self.table)

if __name__ == "__main__":
    directory = AlphabeticalDirectory("data")
    directory.insert("boat")
    directory.insert("from")
    directory.insert("sail")
    
    result = directory.search("sail")
    if result != -1:
        print(f"Word found at bucket position: {result}")
    else:
        print("Word not found.")
    
    directory.delete("sail")
    print("Word deleted.")
    directory.close()
