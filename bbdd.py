import json
import os
import unicodedata
from storage import Storage
from hash_index import HashIndex

class AlphabeticalDirectory:
    def __init__(self, filename:str = "data.log", use_index:bool =True):
        self.use_index =use_index
        self.storage =Storage(filename)
        self.use_index=HashIndex()
        
        self.index.rebuild(self.storage.records())
    def close(self):
        pass
        
    def _hash_letter(self, word):
        """Maps the first letter to index 0-25."""
        return ord(word[0].lower()) - 97

    def _save_to_file(self):
        with open(self.filename, "w") as f:
            json.dump(self.table, f)

    def _load_from_file(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                self.table = json.load(f)

    def insert(self, word: str)-> int:
        word = unicodedata.normalize("NFC", word)
        existing = self.index.find(word, case_sensitive=True)
        
        #give back the offset if already exist
        if existing:
            return existing[0] 
        #if not exist
        offset = self.storage.append(word)
        self.index.add(word, offset)
        return offset

    def search(self, word):
        index = self._hash_letter(word)
        bucket = self.table[index]
        return bucket.index(word) if word in bucket else -1

    def delete(self, word):
        index = self._hash_letter(word)
        if word in self.table[index]:
            self.table[index].remove(word)
            self._save_to_file()

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
