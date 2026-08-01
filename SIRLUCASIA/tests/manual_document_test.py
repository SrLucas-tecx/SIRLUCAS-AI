from app.service.document_manager import DocumentManager

doc = DocumentManager()

print("\n===== CREAR =====")
print(doc.create({
    "topic": "prueba"
}))

print("\n===== ESCRIBIR =====")
print(doc.write({
    "topic": "prueba",
    "content": "Hola desde SIRLUCAS AI"
}))

print("\n===== LEER =====")
print(doc.read({
    "topic": "prueba"
}))

print("\n===== RENOMBRAR =====")
print(doc.rename({
    "old_name": "prueba",
    "new_name": "prueba2"
}))

print("\n===== COPIAR =====")
print(doc.copy({
    "old_name": "prueba2",
    "new_name": "copia_prueba"
}))

print("\n===== ELIMINAR =====")
print(doc.delete({
    "topic": "prueba2"
}))

print("\n===== ELIMINAR COPIA =====")
print(doc.delete({
    "topic": "copia_prueba"
}))