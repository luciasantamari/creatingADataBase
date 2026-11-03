import json
import os


class Storage:
    def __init__(self, filename="data.log"):
        self.filename = filename   # ruta del fichero de datos
        self.records_read = 0      # contador de registros leídos (para el test del índice)

    def append(self, word, deleted=False):
        # Validación: TypeError si no es str, ValueError si está vacío
        if not isinstance(word, str):
            raise TypeError("word is not a string")

        if word == "":
            raise ValueError("word is empty")

        # Registro como dict -> JSON (sin escapar la ó, ñ...) + salto de línea
        record = {
            "word": word,
            "deleted": deleted
        }
        text = json.dumps(record, ensure_ascii=False) + "\n"
        data = text.encode("utf-8")  # str -> bytes, para medir offsets en bytes

        with open(self.filename, "ab") as f:   # "ab": añadir al final, en binario
            f.seek(0, os.SEEK_END)             # ir al final del fichero
            pos = f.tell()                     # offset donde EMPIEZA este registro
            f.write(data)                      # escribir la línea
            return pos                         # devolver el offset al llamador

    def read(self, offset):
        with open(self.filename, "rb") as f:   # abrir en lectura binaria
            f.seek(offset)                     # saltar directamente al registro
            line = f.readline()                # leer una línea (bytes)
            text = line.decode("utf-8")        # bytes -> str
            record = json.loads(text)          # str JSON -> dict
            self.records_read += 1             # contar esta lectura
            return record["word"]              # devolver solo la palabra

    def records(self):
        if not os.path.exists(self.filename):  # sin fichero: no produce nada
            return

        with open(self.filename, "rb") as f:
            while True:
                offset = f.tell()              # offset ANTES de leer = inicio del registro
                line = f.readline()            # leer siguiente línea
                
                if not line:                   # b"" = fin de fichero
                    return
                if not line.endswith(b"\n"):
                    raise ValueError(f"registro corrupto en offset {offset}")
                
                text = line.decode("utf-8")    # bytes -> str
                try:
                    record = json.loads(text)      # str JSON -> dict
                    word = record["word"]          # extraer la palabra
                    deleted = record["deleted"]    # extraer la marca de borrado
                except (json.JSONDecodeError, KeyError):
                    raise ValueError(f"JSON Inválido")
                
                self.records_read += 1         # contar este registro leído
                
                yield (offset, word, deleted)  # entregar y pausar hasta la siguiente vuelta