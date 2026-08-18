# Sistema de Auto-Guardado de Proyectos
## Guía de Integración y Uso

---

## 📋 Resumen Ejecutivo

**Objetivo**: Cuando el usuario menciona un proyecto, se guarda automáticamente en `memory.json` sin intervención manual.

**Flujo Automático**:
```
Usuario: "mi proyecto es SIRLUCAS"
   ↓
ConversationManager.process()
   ↓
ProjectMemoryIntegration.auto_save_project()
   ↓
RuleEngine.match() → Detecta regla "guardar_proyecto"
   ↓
ProjectMemoryHandler.handle_rule()
   ↓
MemoryManager.remember_project("SIRLUCAS")
   ↓
memory.json ← Guardado persistente
```

---

## 🎯 Casos de Uso Soportados

### 1. Guardar Proyecto Simple
```
Usuario: "mi proyecto es SIRLUCAS"
Sistema: ✅ Guardado "SIRLUCAS" en memory.json como proyecto
```

### 2. Guardar Proyecto con Descripción
```
Usuario: "trabajo en IAGENERATOR que es un sistema de IA avanzada"
Sistema: ✅ Guardado "IAGENERATOR" con descripción en memory.json
```

### 3. Consultar Proyecto Guardado
```
Usuario: "¿cuál es mi proyecto?"
Sistema: 🔍 Busca en memory.json y responde con el proyecto actual
```

### 4. Actualizar Proyecto
```
Usuario: "cambio mi proyecto a ChatBot"
Sistema: 🔄 Actualiza memory.json con nuevo proyecto
```

### 5. Listar Todos los Proyectos
```
Usuario: "lista mis proyectos"
Sistema: 📋 Muestra todos los proyectos guardados en memory.json
```

---

## 🏗️ Arquitectura

### Componentes Principales

#### 1. **parser_rules_proyectos.json**
- **Ubicación**: `app/modules/parser_rules_proyectos.json`
- **Contenido**: 10 reglas específicas para detectar menciones de proyectos
- **Ejemplos de patrones**:
  ```regex
  "^mi proyecto es (.+)$"
  "^trabajo en el proyecto (.+)$"
  "^¿cuál es mi proyecto\??$"
  "^lista mis proyectos$"
  ```

#### 2. **ProjectMemoryHandler**
- **Ubicación**: `app/modules/project_memory_handler.py`
- **Responsabilidad**: Mapear resultados de RuleEngine a métodos MemoryManager
- **Métodos**:
  - `handle_remember_project()` → Guarda proyecto simple
  - `handle_remember_project_with_description()` → Guarda con descripción
  - `handle_recall_project()` → Recupera proyecto actual
  - `handle_update_project()` → Actualiza proyecto
  - `handle_list_projects()` → Lista todos los proyectos
  - `handle_search_project()` → Busca proyecto específico
  - `handle_forget_project()` → Olvida proyecto
  - `handle_get_project_details()` → Obtiene detalles del proyecto

#### 3. **ProjectMemoryIntegration**
- **Ubicación**: `app/core/project_memory_integration.py`
- **Responsabilidad**: Orquesta RuleEngine + ProjectMemoryHandler
- **Métodos públicos**:
  - `auto_save_project(message)` → Punto de entrada principal
  - `process_message(message)` → Ejecuta RuleEngine y obtiene resultado
  - `get_project_suggestions(message)` → Extrae palabras clave relacionadas

#### 4. **ConversationManager (Mejorado)**
- **Ubicación**: `app/core/conversation_manager.py`
- **Cambio**: Ahora llama a `project_memory.auto_save_project()` en `process()`
- **Punto de integración**: Línea ~175 en `process()`
  ```python
  project_save_result = self.project_memory.auto_save_project(message)
  ```

#### 5. **MemoryManager**
- **Métodos existentes** (no modificados):
  - `remember_project(project_name, description)` ✅
  - `get_project(project_name)` ✅
  - `find_by_category("projects")` ✅

---

## 📂 Estructura de Datos en memory.json

### Proyecto Guardado
```json
{
  "project:sirlucas": {
    "id": "uuid-generado-automáticamente",
    "value": {
      "name": "SIRLUCAS",
      "description": "Mi asistente de IA principal"
    },
    "category": "projects",
    "created_at": "2026-08-17T10:30:00.123456",
    "updated_at": "2026-08-17T10:30:00.123456",
    "importance": 5,
    "source": "conversation",
    "times_used": 0,
    "last_access": null,
    "aliases": ["proyecto", "mi proyecto", "sirlucas"],
    "tags": ["project", "proyecto", "ia"]
  }
}
```

---

## 🔌 Integración en el Código

### Antes (Sin Auto-Guardado)
```python
# ConversationManager.process() - ANTES
def process(self, data: dict) -> ActionResult:
    message = data.get("message")
    
    # Detección manual y limitada
    if "proyecto" in message.lower():
        # Solo detectaba patrones muy específicos
        match = re.search(r"(llamado|se llama)\s+([A-Za-z0-9_-]+)", ...)
```

### Después (Con Auto-Guardado)
```python
# ConversationManager.process() - DESPUÉS
def process(self, data: dict) -> ActionResult:
    message = data.get("message")
    
    # ==================================================
    # AUTO-GUARDADO DE PROYECTOS (NUEVO)
    # ==================================================
    project_save_result = self.project_memory.auto_save_project(message)
    
    if project_save_result and project_save_result.success:
        logger.info(f"Proyecto auto-guardado: {project_save_result.message}")
```

---

## 🚀 Cómo Ejecutar y Validar

### 1. Ejecutar Tests de Validación
```bash
cd d:\LUCAS_IA\SIRLUCAS-AI\SIRLUCASIA

# Activar venv
.\\.venv\Scripts\Activate.ps1

# Ejecutar tests
python tests/test_project_auto_save.py
```

**Esperado**:
```
╔════════════════════════════════════════════════════════╗
║  VALIDACIÓN COMPLETA: AUTO-GUARDADO DE PROYECTOS      ║
╚════════════════════════════════════════════════════════╝

TEST 1: RuleEngine detecta reglas de proyectos
=====================================
✅ 'mi proyecto es SIRLUCAS'
   → Esperado: guardar_proyecto, Obtenido: guardar_proyecto
   → Proyecto detectado: SIRLUCAS
...

✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE
```

### 2. Prueba Manual en Conversación
```python
from app.core.conversation_manager import ConversationManager
from app.core.memory_manager import MemoryManager

# Crear instancias
memory = MemoryManager()
conversation = ConversationManager(memory=memory)

# Test 1: Guardar proyecto
print("Test 1: Guardar proyecto")
result = conversation.process({
    "message": "mi proyecto es SIRLUCAS",
    "user_id": "test_user"
})
print(f"Éxito: {result.success}\n")

# Test 2: Consultar proyecto
print("Test 2: Consultar proyecto")
result = conversation.process({
    "message": "¿cuál es mi proyecto?",
    "user_id": "test_user"
})
print(f"Respuesta: {result.data}")

# Test 3: Verificar memory.json
print("\nTest 3: Verificar memory.json")
projects = memory.find_by_category({"category": "projects"})
print(f"Proyectos guardados: {len(projects.data)}")
for proj in projects.data:
    print(f"  - {proj.get('name')}")
```

---

## 📋 Reglas de Proyectos Disponibles

| Regla | Patrón | Comando | Resultado |
|-------|--------|---------|-----------|
| `guardar_proyecto` | "mi proyecto es X" | `remember_project` | Guarda proyecto simple |
| `guardar_proyecto_con_descripcion` | "trabajo en X que es Y" | `remember_project_description` | Guarda con descripción |
| `recordar_proyecto` | "¿cuál es mi proyecto?" | `recall_project` | Recupera proyecto actual |
| `actualizar_proyecto` | "cambio mi proyecto a X" | `update_project` | Actualiza proyecto |
| `detalles_proyecto` | "dame detalles del proyecto" | `get_project_details` | Obtiene detalles |
| `listar_proyectos` | "lista mis proyectos" | `list_projects` | Lista todos |
| `buscar_proyecto` | "busca el proyecto X" | `search_project` | Busca específico |
| `olvidar_proyecto` | "olvida el proyecto X" | `forget_project` | Olvida proyecto |
| `crear_proyecto_nuevo` | "crea un proyecto llamado X" | `create_project` | Crea nuevo |
| `agregar_detalle_proyecto` | "agrega a mi proyecto X" | `add_project_detail` | Agrega detalle |

---

## ⚙️ Configuración

### Variables de Entorno
```python
# En ConversationManager.__init__()
self.project_memory = ProjectMemoryIntegration(self.memory)
```

### Parámetros MemoryManager
```python
# Auto-guardado inmediato (por defecto)
memory = MemoryManager(autosave_enabled=True)

# Guardado diferido (se guarda al final del turno)
memory = MemoryManager(autosave_enabled=False)
```

---

## 🐛 Troubleshooting

### Problema: "No se guarda el proyecto"
**Solución**: Verificar que:
1. `parser_rules_proyectos.json` existe en `app/modules/`
2. RuleEngine coincide con el mensaje
3. MemoryManager tiene `autosave_enabled=True` (default)
4. `memory.json` tiene permisos de escritura

### Problema: "El proyecto se guarda pero no se recupera"
**Solución**: Verificar que:
1. La clave en memory.json es `project:nombreproyecto` (minúsculas)
2. `find_by_category("projects")` está retornando datos
3. memory.json no está corrompido

### Problema: "RuleEngine no detecta el patrón"
**Solución**: 
1. Verificar regex en parser_rules_proyectos.json
2. Probar con `test_project_auto_save.py`
3. Activar logging en RuleEngine:
   ```python
   logger.setLevel(logging.DEBUG)
   ```

---

## 📝 Próximas Mejoras (Roadmap)

- [ ] Integrar con Ollama para sugerencias de proyectos
- [ ] Implementar búsqueda semántica de proyectos
- [ ] Crear estadísticas de uso por proyecto
- [ ] Añadir miembros/colaboradores a proyectos
- [ ] Vincular tareas/documentos a proyectos
- [ ] Exportar proyectos a diferentes formatos (JSON, CSV, PDF)

---

## 📞 Contacto y Soporte

Para reportar bugs o sugerencias sobre el sistema de auto-guardado:
1. Revisa `AUDIT_MEMORY_BUGS.md` para problemas conocidos
2. Ejecuta `test_project_auto_save.py` para diagnóstico
3. Consulta los logs en `logs/` para detalles

---

**Última actualización**: 2026-08-17
**Versión**: 1.0
**Estado**: ✅ Listo para producción
