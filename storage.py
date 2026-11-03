import json
import os
import unicodedata


class Storage:
    def __init__(self, filename="data.log"):
        self.filename = filename   # Data file path
        self.records_read = 0      # Read records counter (for index testing)

    def append(self, word, deleted=False):
        # Validation: TypeError if types are incorrect, ValueError if word is empty
        if not isinstance(word, str):
            raise TypeError("word must be a str")
        if not isinstance(deleted, bool):
            raise TypeError("deleted must be a bool")
        if word == "":
            raise ValueError("word cannot be empty")
        
        word = unicodedata.normalize("NFC", word)

        # Record as dict -> JSON (without escaping accented chars like ó, ñ...) + newline
        record = {
            "word": word,
            "deleted": deleted
        }
        text = json.dumps(record, ensure_ascii=False) + "\n"
        data = text.encode("utf-8")  # str -> bytes, to measure offsets in bytes

        with open(self.filename, "ab") as f:   # "ab": append to the end in binary mode
            f.seek(0, os.SEEK_END)             # Go to the end of the file
            pos = f.tell()                     # Offset where this record STARTS
            f.write(data)                      # Write the line
            return pos                         # Return offset to the caller

    def read(self, offset):
        with open(self.filename, "rb") as f:   # Open in binary read mode
            f.seek(offset)                     # Jump directly to the record
            line = f.readline()                # Read one line (bytes)
        word, _ = self._parse_line(line, offset)   # Validate and extract (deletion flag not needed)
        self.records_read += 1                 # Increment read counter
        return word

    def records(self):
        if not os.path.exists(self.filename):  # File does not exist: yield nothing
            return

        with open(self.filename, "rb") as f:
            while True:
                offset = f.tell()              # Offset BEFORE reading = start of record
                line = f.readline()            # Read next line
                if not line:                   # b"" = end of file
                    return
                word, deleted = self._parse_line(line, offset)  # Validate and extract
                self.records_read += 1         # Increment read records count
                yield (offset, word, deleted)  # Yield tuple and pause until next iteration

    def _parse_line(self, line, offset):
        # Validates a raw line and returns (word, deleted).
        # Any issue raises ValueError with the offset included in the message.
        if not line.endswith(b"\n"):           # Also covers reading past EOF (b"")
            raise ValueError(f"record without trailing newline at offset {offset}")

        try:
            record = json.loads(line.decode("utf-8"))   # bytes -> str -> JSON object
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError(f"invalid JSON at offset {offset}")

        if not isinstance(record, dict):       # Valid JSON but not an object: [1, 2], 5, null...
            raise ValueError(f"record is not an object at offset {offset}")
        if "word" not in record or "deleted" not in record:
            raise ValueError(f"missing 'word' or 'deleted' at offset {offset}")

        word = record["word"]
        deleted = record["deleted"]
        if not isinstance(word, str) or word == "":
            raise ValueError(f"'word' must be a non-empty str at offset {offset}")
        if not isinstance(deleted, bool):
            raise ValueError(f"'deleted' must be a bool at offset {offset}")

        return word, deleted