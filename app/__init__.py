"""Compatibilidad para importar el paquete app desde la raíz del repositorio.

Esto permite que el proyecto funcione tanto con:
- import app.core...
- import SIRLUCASIA.app.core...

sin cambiar la arquitectura interna.
"""

from pathlib import Path
import sys

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_REAL_APP_DIR = _PROJECT_ROOT / "SIRLUCASIA" / "app"

if _REAL_APP_DIR.exists():
    __path__ = [str(_REAL_APP_DIR)]
    if str(_PROJECT_ROOT / "SIRLUCASIA") not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT / "SIRLUCASIA"))
