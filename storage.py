import json
import os


class Storage:
    def __init__(self, filename="data.log"):
        self.filename = filename
        self.records_read = 0

    def append(self, word, deleted=False):
        if not isinstance(word, str):
            raise TypeError("word is not a string")
        
        if word == "":
            raise ValueError("word is empty")
        
        record = {
            "word": word,
            "deleted": deleted
        }
        text = json.dumps(record, ensure_ascii=False) + "\n"
        data = text.encode("utf-8")

        with open(self.filename, "ab") as f:
            f.seek(0, os.SEEK_END)
            pos = f.tell()
            f.write(data)
            return pos
        
        
    def read(self, offset):
        with open (self.filename, "rb") as f:
            f.seek(offset)
            line = f.readline()
            text = line.decode("utf-8")
            record = json.loads(text)
            self.records_read += 1
            return record["word"]
    
    def records(self):
        if not os.path.exists(self.filename):
            return
        
        with open(self.filename, "rb") as f:
            while True:
                offset = f.tell()
                line = f.readline()
                if not line:
                    return
                text = line.decode("utf-8")
                record = json.loads(text)
                word = record["word"]
                deleted = record["deleted"]
                self.records_read += 1
                yield (offset, word, deleted)
            
        