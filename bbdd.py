from storage import Storage
from hash_index import HashIndex
import os


class AlphabeticalDirectory:
    def __init__(self, filename="data.db"):
        self.storage = Storage(filename)
        self.index = HashIndex()
        self._rebuild_index()

    def close(self):
        #code...
        pass
        
    def insert(self, word):
        #code...
       pass

    def search(self, word):
        #code...
        pass
       

    def delete(self, word):
        #code...
        pass
            
    def _rebuild_index(self):
        #code...
        pass
       
    
       

#if __name__ == "__main__":
