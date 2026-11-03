import json
import os


class Storage:
    def __init__(self, filename="data.log"):
        self.filename = filename   # ruta del fichero de datos
        self.records_read = 0      # contador de registros leídos (para el test del índice)

    def append(self, word, deleted=False):
        # Validación: TypeError si los tipos son incorrectos, ValueError si word está vacío
        if not isinstance(word, str):
            raise TypeError("word debe ser un str")
        if not isinstance(deleted, bool):
            raise TypeError("deleted debe ser un bool")
        if word == "":
            raise ValueError("word no puede estar vacío")

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
        word, _ = self._parse_line(line, offset)   # validar y extraer (el borrado no hace falta)
        self.records_read += 1                 # contar esta lectura
        return word

    def records(self):
        if not os.path.exists(self.filename):  # sin fichero: no produce nada
            return

        with open(self.filename, "rb") as f:
            while True:
                offset = f.tell()              # offset ANTES de leer = inicio del registro
                line = f.readline()            # leer siguiente línea
                if not line:                   # b"" = fin de fichero
                    return
                word, deleted = self._parse_line(line, offset)  # validar y extraer
                self.records_read += 1         # contar este registro leído
                yield (offset, word, deleted)  # entregar y pausar hasta la siguiente vuelta

    def _parse_line(self, line, offset):
        # Valida una línea cruda y devuelve (word, deleted).
        # Cualquier problema lanza ValueError con el offset en el mensaje.
        if not line.endswith(b"\n"):           # también cubre leer más allá del final (b"")
            raise ValueError(f"registro sin salto de línea final en offset {offset}")

        try:
            record = json.loads(line.decode("utf-8"))   # bytes -> str -> objeto JSON
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError(f"JSON inválido en offset {offset}")

        if not isinstance(record, dict):       # JSON válido pero no es un objeto: [1, 2], 5, null...
            raise ValueError(f"el registro no es un objeto en offset {offset}")
        if "word" not in record or "deleted" not in record:
            raise ValueError(f"falta 'word' o 'deleted' en offset {offset}")

        word = record["word"]
        deleted = record["deleted"]
        if not isinstance(word, str) or word == "":
            raise ValueError(f"'word' debe ser un str no vacío en offset {offset}")
        if not isinstance(deleted, bool):
            raise ValueError(f"'deleted' debe ser un bool en offset {offset}")

        return word, deleted
