import unicodedata
from storage import Storage
from hash_index import HashIndex, normalize

class AlphabeticalDirectory:
    def __init__(self, filename:str = "data.log", use_index:bool =True):
        self.use_index =use_index
        self.storage =Storage(filename)
        #only if use index is true
        if self.use_index:
            self.index = HashIndex()
            self.index.rebuild(self.storage.records())
        else:
            self.index = None
        
    def close(self):
        pass
        
    def normalization(self, word):
        word = unicodedata.normalize("NFC", word)
        return word
    

    def insert(self, word: str)-> int:
        word = self.normalization(word)
        existing = self.index.find(word, case_sensitive=True)
        
        #give back the offset if already exist
        if existing:
            return existing[0] 
        #if not exist
        offset = self.storage.append(word)
        self.index.add(word, offset)
        return offset


    def search(self, word: str, case_sensitive: bool = False) -> list[int]:#ToDo:Fragment code
        word = self.normalization(word)
        
        # Index on = O(1):
        if self.use_index:
            return self.index.find(word, case_sensitive=case_sensitive)
        # Index of = O(n):
        active_words = {}  
        
        for offset, rec_word, deleted in self.storage.records():
            if deleted:
                active_words.pop(rec_word, None)
            else:
                active_words[rec_word] = offset
                
       
        results = []
        for active_word, offset in active_words.items():
            if case_sensitive:
                if active_word == word:
                    results.append(offset)
            else:
                
                if normalize(active_word) == normalize(word):
                    results.append(offset)
        
        return sorted(results)
 
                

    def delete(self, word):
    #word exist?
        if self.use_index:
            if not self.index.find(word, case_sensitive=True): 
                return False
        else:
            # if not index manual search
            is_active = False
            for offset, rec_word, is_deleted in self.storage.records():
                if rec_word == word:
                    is_active = not is_deleted
            if not is_active:
                return False

        
        self.storage.append(word, deleted=True)
        
        #delete from memorie
        if self.use_index:
            self.index.remove(word) 
            
        return True
if __name__ == "__main__":
    print("Word deleted.")

