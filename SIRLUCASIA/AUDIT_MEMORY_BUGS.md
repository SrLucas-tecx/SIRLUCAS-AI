# Auditoría de Bugs - MemoryManager

## 🔴 BUGS CRÍTICOS ENCONTRADOS

### 1. **Bug en `execute()` - Manejo de TypeError confuso**
**Líneas:** 266-280
**Problema:** La lógica de fallback es peligrosa:
```python
try:
    result = method(data)
except TypeError:
    try:
        result = method()  # ← Intenta sin argumentos
    except Exception as exc:
        return ActionResult(...)
```

**Impacto:** Si un método espera `data` pero recibe argumentos inválidos, silenciosamente intenta sin argumentos. Esto **enmascarará errores reales**.

**Ejemplo de problema:**
- `remember({"key": None})` → TypeError interno → intenta `remember()` sin args → devuelve error confuso

---

### 2. **Bug en `rank_memories()` - Indentación incorrecta**
**Líneas:** 1016-1045
**Problema:** La función está indentada con 4 espacios extra (8 en total en la definición)
```python
    def rank_memories(self, data: dict) -> ActionResult:
            """Indentada incorrectamente (extra espacios)"""
```

**Impacto:** Aunque Python lo permite, **es inconsistente** con el resto del código y dificulta el mantenimiento.

---

### 3. **Bug en `_trim_conversation_turns()` - Race condition potencial**
**Líneas:** 1612-1632
**Problema:** Se usa `self._lock` pero la función modifica `self.memory` mientras itera:
```python
with self._lock:
    keys = list(self._category_index.get("conversation", ()))
    if len(keys) <= MAX_CONVERSATION_TURNS:
        return  # ← Sale del lock pero pudo modificar índices
    
    turns = [(key, self.memory[key]) for key in keys if key in self.memory]
    turns.sort(...)
    
    for key, record in turns[:excess]:
        self.memory.pop(key, None)  # ← Modifica mientras está dentro del lock
        self._index_remove(key, record)
```

**Impacto:** Si `self.memory` cambia durante la iteración, `self.memory.pop()` podría fallar silenciosamente porque el registro ya no existe (después de `_index_remove`).

---

### 4. **Bug de inconsistencia en firmas - `find_by_importance()`**
**Líneas:** 800-803
**Problema:** La firma acepta `data: dict | int | None` pero el cuerpo trata como `int`:
```python
def find_by_importance(self, data: dict | int | None = None) -> dict:
    importance = data.get("importance") if isinstance(data, dict) else data
    # ↑ Si data es int, .get() fallará y no hay error
```

**Impacto:** Si se pasa `int`, `data.get()` lanzará AttributeError.

---

### 5. **Falta validación en `get_relevant_memory()`**
**Líneas:** 1195-1260
**Problema:** Accede a `ranked.data` sin verificar que `rank_memories()` fue exitoso:
```python
ranked = self.rank_memories({...})
for key, score, record in ranked.data or []:  # ← Asume estructura correcta
```

**Impacto:** Si `rank_memories()` devuelve `data=[]` con `success=False`, el bucle falla silenciosamente.

---

### 6. **Bug de integración - JSONManager no existe en el repositorio**
**Líneas:** 101, 1554-1559
**Problema:** El código asume `JSONManager.load()` y `JSONManager.save()`, pero no se ve la implementación:
```python
from app.utils.json_manager import JSONManager  # ← ¿Existe este archivo?
```

**Impacto:** En tiempo de ejecución: `ModuleNotFoundError` o `AttributeError`.

---

### 7. **Bug en `suggest_memories()` - Estructura de datos inconsistente**
**Líneas:** 1047-1063
**Problema:** Devuelve `ranked.data` que es lista de tuplas, pero el comando espera dict:
```python
ranked = self.rank_memories(...)  # data = [(key, score, record), ...]
return ActionResult(
    ...
    data=ranked.data  # ← Tuplas, no dict
)
```

**Impacto:** Código cliente esperaría `data` como dict, pero obtiene lista de tuplas.

---

### 8. **Falta validación en `restore()` - Backup corrupto**
**Líneas:** 1471-1503
**Problema:** No valida que el backup tenga la estructura correcta:
```python
contenido = self._read_storage(path)
if contenido is None:
    return ActionResult(...)

with self._lock:
    self.memory = {
        self._normalize(key): self._normalize_record(record) 
        for key, record in contenido.items()  # ← Si contenido no es dict, falla
    }
```

**Impacto:** Si el backup es una lista o JSON corrupto, el error se propaga sin manejo.

---

### 9. **Inconsistencia en parámetros - `find_by_category()` vs `find_by_tag()`**
**Líneas:** 774-781
**Problema:** Ambas funciones aceptan argumentos diferentes:
```python
def find_by_category(self, category: str) -> dict:
    # Acepta STRING directo
    
def find_by_tag(self, tag: str) -> dict:
    # Acepta STRING directo
```

Pero en `COMMANDS` están listadas y se llaman via `execute(data)`:
```python
"find_by_category",
"find_by_tag",
```

**Impacto:** Si se llaman via `execute()`, fallarán porque esperan argumentos posicionales, no `data: dict`.

---

### 10. **Falta sincronización en `from_dict()`**
**Líneas:** 1716-1740
**Problema:** No sincroniza el estado completamente:
```python
self.memory = {...}
self._index_rebuild()
# ← Pero _dirty siempre se marca sin importar el estado anterior
self.mark_dirty()  # ← Siempre marca como dirty, incluso si se restauró limpio
```

**Impacto:** Después de `from_dict()`, siempre marca como dirty aunque el contenido sea idéntico.

---

## ⚠️ PROBLEMAS DE INTEGRACIÓN

### Con `ollama_client.py`:
- ✅ `get_relevant_memory()` devuelve `list[str]`, compatible con prompts
- ❌ No maneja timeout de Ollama correctamente (memoria podría quedarse sin guardar)

### Con `rule_engine.py`:
- ✅ Acepta `data: dict` desde dispatcher
- ❌ Algunos comandos (`find_by_category`, `find_by_tag`) no son invocables via `execute()`

### Con `conversation_manager.py`:
- ✅ `consult()` y `remember_turn()` son puntos de integración claros
- ❌ No hay manejo de límites de turnos en tiempo real

---

## 📋 RECOMENDACIONES DE FIX

| # | Bug | Severidad | Fix |
|---|-----|-----------|-----|
| 1 | Manejo de TypeError en execute() | CRÍTICA | Remover fallback silencioso, lanzar error específico |
| 2 | Indentación en rank_memories() | MEDIA | Normalizar indentación (4 espacios) |
| 3 | Race condition en _trim_conversation_turns() | CRÍTICA | Usar guard adicional antes de pop() |
| 4 | Firma inconsistente find_by_importance() | MEDIA | Definir firma clara y documentar |
| 5 | Falta validación en get_relevant_memory() | MEDIA | Verificar success antes de iterar |
| 6 | JSONManager no existe | CRÍTICA | Verificar que el archivo existe |
| 7 | suggest_memories() devuelve tuplas | MEDIA | Convertir a dict en execute() |
| 8 | Falta validación en restore() | MEDIA | Validar estructura de backup antes de restaurar |
| 9 | Comandos con firma incompatible | MEDIA | Envolver find_by_category/tag en wrapper que acepte data |
| 10 | from_dict() marca siempre dirty | BAJA | Preservar flag original si contenido es idéntico |

