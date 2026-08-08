# ==================================================
# IntentResolver
# Traduce el par (module, command) a un intent
# ==================================================

# Mapa explícito (module, command) -> intent.
# Debe cubrir exactamente lo que cada manager expone en su
# whitelist/dispatch. Un (module, command) fuera de este mapa se
# considera desconocido (UNKNOWN).
INTENT_MAP = {
    # ---- system ----
    ("system", "open"): "OPEN_PROGRAM",
    ("system", "close"): "CLOSE_PROGRAM",
    ("system", "restart"): "RESTART_PROGRAM",

    # ---- document ----
    ("document", "create"): "CREATE_DOCUMENT",
    ("document", "write"): "WRITE_DOCUMENT",
    ("document", "read"): "READ_DOCUMENT",
    ("document", "delete"): "DELETE_DOCUMENT",
    ("document", "rename"): "RENAME_DOCUMENT",
    ("document", "copy"): "COPY_DOCUMENT",
    ("document", "move"): "MOVE_DOCUMENT",
    ("document", "list_documents"): "LIST_DOCUMENTS",
    ("document", "info"): "INFO_DOCUMENT",
    ("document", "search"): "SEARCH_DOCUMENT",
    ("document", "modified"): "MODIFIED_DOCUMENT",
    ("document", "exists"): "EXISTS_DOCUMENT",

    # ---- memory ----
    ("memory", "remember"): "SAVE_MEMORY",
    ("memory", "recall"): "READ_MEMORY",
    ("memory", "forget"): "FORGET_MEMORY",
    ("memory", "update"): "UPDATE_MEMORY",
    ("memory", "search"): "SEARCH_MEMORY",
    ("memory", "list"): "LIST_MEMORY",
    ("memory", "count"): "COUNT_MEMORY",
    ("memory", "categories"): "CATEGORIES_MEMORY",
    ("memory", "export"): "EXPORT_MEMORY",
    ("memory", "import_memories"): "IMPORT_MEMORY",
    ("memory", "clear"): "CLEAR_MEMORY",

    # ---- history ----
    ("history", "history"): "READ_HISTORY",
    ("history", "last"): "LAST_HISTORY",
    ("history", "last_n"): "LAST_N_HISTORY",
    ("history", "search"): "SEARCH_HISTORY",
    ("history", "clear"): "CLEAR_HISTORY",
    ("history", "count"): "COUNT_HISTORY",
    ("history", "statistics"): "STATISTICS_HISTORY",
    ("history", "summary"): "SUMMARY_HISTORY",
    ("history", "export"): "EXPORT_HISTORY",
}

# Módulos donde el intent no depende del comando.
MODULE_INTENT_MAP = {
    "knowledge": "SEARCH_KNOWLEDGE",
    "web": "SEARCH_WEB",
    "calculator": "CALCULATE",
    "conversation": "CHAT",
}


class IntentResolver:

    def __init__(self):
        pass

    def resolve(self, data):

        if not isinstance(data, dict):
            return data

        module = data.get("module")
        command = data.get("command")

        intent = INTENT_MAP.get((module, command))

        if intent is None:
            intent = MODULE_INTENT_MAP.get(module)

        # Si no encontró ninguna intención,
        # marcar como desconocida.
        if intent is None:
            data["module"] = "unknown"
            data["intent"] = "UNKNOWN"
        else:
            data["intent"] = intent

        return data
