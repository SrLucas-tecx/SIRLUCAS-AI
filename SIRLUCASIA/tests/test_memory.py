from app.core.memory_manager import MemoryManager
memory = MemoryManager()

print("Guardando datos...")
memory.remember("nombre", "Juan")

print("Recuperando dato...")
print(memory.recall("nombre"))

print("Memoria completa:")
print(memory.list_memories())

print("Eliminando dato...")
memory.forget("nombre")

print("Memoria final:")
print(memory.list_memories())
