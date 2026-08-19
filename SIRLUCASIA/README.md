# SIRLUCAS AI

Asistente personal local en Python. Combina un intérprete determinista de comandos con una capa generativa opcional basada en Ollama.

## Estado actual

La memoria persistente, los proyectos y el contexto de sesión están operativos. La memoria se guarda en `data/memory.json`; los proyectos usan la categoría `projects` y se recuperan entre ejecuciones.

Inicio e instalación:

```powershell
python -m pip install -r requirements.txt
python launcher.py
```

Para conversación generativa se necesita Ollama activo y un modelo disponible (por defecto, `llama3:latest`).

## Arquitectura

`launcher.py` inicia `app.main`, que crea `Assistant`.

1. `Parser` normaliza el mensaje y aplica reglas JSON.
2. `TaskPipeline` resuelve contexto, intención, plan y ejecución.
3. `Router` envía cada acción a su gestor.
4. `MemoryManager` y `ContextManager` conservan memoria persistente y contexto de sesión.
5. Los mensajes conversacionales se envían a `AIRouter` y Ollama.

- `app/core`: pipeline, contexto, memoria, historial y eventos.
- `app/modules`: parser, normalizador y reglas de proyectos.
- `app/service`: documentos y programas de Windows.
- `app/IA`: Ollama, prompt y construcción del contexto.
- `data`: memoria, conocimiento y configuraciones JSON.
- `tests`: pruebas automatizadas.

## Memoria y proyectos

`MemoryManager` usa escritura atómica de JSON. Con `autosave_enabled=True` (valor predeterminado), las operaciones estructurales se guardan de inmediato.

Frases como `mi proyecto es SIRLUCAS` se procesan mediante `ProjectMemoryHandler`, que guarda el proyecto en memoria. Se pueden consultar, listar, actualizar, buscar, olvidar y añadir detalles.

## Límites actuales

- El parser se basa principalmente en expresiones regulares; falta comprensión natural y referencias complejas.
- El comando de clima está definido en reglas, pero aún no tiene proveedor real de datos.
- Hay pruebas heredadas que esperan listas o strings en vez de `ActionResult`; deben unificarse.
- El entorno virtual local debe apuntar a un intérprete Python válido.

## Próximas prioridades

1. Pruebas aisladas de memoria entre sesiones y de proyectos.
2. Unificar pruebas alrededor de `ActionResult`.
3. Mejorar comprensión natural y resolución de contexto.
4. Medir latencia por módulo y ajustar Ollama/modelo.
5. Implementar proveedor real para clima/web.
