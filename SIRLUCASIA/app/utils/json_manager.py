import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class JSONManager:

    @staticmethod
    def _encode_json_value(value):
        if isinstance(value, dict):
            return {str(k): JSONManager._encode_json_value(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [JSONManager._encode_json_value(v) for v in value]
        if isinstance(value, set):
            return [JSONManager._encode_json_value(v) for v in sorted(value, key=lambda item: str(item))]
        if isinstance(value, datetime):
            return value.isoformat()
        if hasattr(value, "__dict__") and type(value).__name__ not in {"str", "int", "float", "bool"}:
            data = getattr(value, "__dict__", None)
            if isinstance(data, dict):
                return {str(k): JSONManager._encode_json_value(v) for k, v in data.items()}
        return value

    @staticmethod
    def _json_default(value):
        if isinstance(value, set):
            return list(value)
        if isinstance(value, datetime):
            return value.isoformat()
        if hasattr(value, "__dict__"):
            data = getattr(value, "__dict__", None)
            if isinstance(data, dict):
                return {str(k): JSONManager._encode_json_value(v) for k, v in data.items()}
        return str(value)

    @staticmethod
    def _ensure_parent_dir(path):
        directory = os.path.dirname(path)
        if directory and not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)

    @staticmethod
    def load(path):

        try:
            JSONManager._ensure_parent_dir(path)

            for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
                try:
                    with open(path, "r", encoding=encoding) as file:
                        content = file.read().strip()
                    if not content:
                        return {}
                    return json.loads(content)
                except UnicodeDecodeError:
                    continue
                except FileNotFoundError:
                    logger.info(
                        "No existe el archivo '%s'. Se creará uno nuevo.",
                        path
                    )
                    return {}
                except json.JSONDecodeError as e:
                    logger.error(
                        "Error en el JSON '%s' (línea %s, columna %s): %s",
                        path,
                        e.lineno,
                        e.colno,
                        e.msg,
                    )
                    return None

            return None

        except FileNotFoundError:

            logger.info(
                "No existe el archivo '%s'. Se creará uno nuevo.",
                path
            )
            return {}

    @staticmethod
    def save(path, data):

        # Escritura atómica:
        # primero se escribe completamente un archivo temporal
        # y después se reemplaza el archivo original.
        JSONManager._ensure_parent_dir(path)
        tmp_path = f"{path}.tmp"

        try:
            serialized = JSONManager._encode_json_value(data)

            with open(tmp_path, "w", encoding="utf-8") as file:

                json.dump(
                    serialized,
                    file,
                    indent=4,
                    ensure_ascii=False,
                    default=JSONManager._json_default,
                )

                file.flush()
                os.fsync(file.fileno())

            os.replace(tmp_path, path)

            return True

        except Exception as e:

            logger.error(
                "Error al guardar '%s': %s",
                path,
                e
            )

            try:
                os.remove(tmp_path)
            except OSError:
                pass

            return False

    @staticmethod
    def exists(path):
        return os.path.isfile(path)