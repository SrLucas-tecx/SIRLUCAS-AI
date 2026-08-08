import json
import logging
import os

logger = logging.getLogger(__name__)


class JSONManager:

    @staticmethod
    def load(path):

        try:

            with open(path, "r", encoding="utf-8") as file:

                content = file.read().strip()

                if not content:
                    return {}

                return json.loads(content)

        except FileNotFoundError:

            logger.info("No existe el archivo '%s'. Se creará uno nuevo.", path)
            return {}

        except json.JSONDecodeError as e:

            logger.error(
                "Error en el JSON '%s' (línea %s, columna %s): %s",
                path, e.lineno, e.colno, e.msg,
            )

            return None

    @staticmethod
    def save(path, data):

        # Escritura atómica: se vuelca a un temporal y se reemplaza el
        # destino de una sola vez, para que una interrupción no deje el
        # archivo original a medio escribir.
        tmp_path = f"{path}.tmp"

        try:

            with open(tmp_path, "w", encoding="utf-8") as file:

                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

                file.flush()
                os.fsync(file.fileno())

            os.replace(tmp_path, path)

            return True

        except Exception as e:

            logger.error("Error al guardar '%s': %s", path, e)

            try:
                os.remove(tmp_path)
            except OSError:
                pass

            return False

    @staticmethod
    def exists(path):
        return os.path.isfile(path)
