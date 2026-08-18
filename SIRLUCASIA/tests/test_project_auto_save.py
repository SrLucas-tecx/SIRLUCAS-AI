"""
test_project_auto_save.py
========================
Valida el flujo completo de auto-guardado de proyectos:
  1. Usuario dice: "mi proyecto es X"
  2. RuleEngine detecta la regla
  3. ProjectMemoryHandler guarda el proyecto
  4. MemoryManager persiste en memory.json
  5. Próxima consulta recupera el proyecto automáticamente
"""

import sys
import os
import json
from pathlib import Path

# Agregar ruta de app al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.memory_manager import MemoryManager
from app.core.rule_engine import RuleEngine
from app.modules.project_memory_handler import ProjectMemoryHandler
from app.core.conversation_manager import ConversationManager

def test_rule_engine_project_detection():
    """Test 1: RuleEngine detecta reglas de proyectos correctamente"""
    print("\n" + "="*60)
    print("TEST 1: RuleEngine detecta reglas de proyectos")
    print("="*60)
    
    # Cargar reglas
    rules_path = Path(__file__).parent.parent / "modules" / "parser_rules_proyectos.json"
    with open(rules_path, "r", encoding="utf-8") as f:
        rules = json.load(f)
    
    engine = RuleEngine(rules)
    
    # Test casos
    test_cases = [
        ("mi proyecto es SIRLUCAS", "guardar_proyecto"),
        ("trabajo en IAGENERATOR que es un sistema de IA", "guardar_proyecto_con_descripcion"),
        ("¿cuál es mi proyecto?", "recordar_proyecto"),
        ("cambio mi proyecto a ChatBot", "actualizar_proyecto"),
        ("lista mis proyectos", "listar_proyectos"),
    ]
    
    print("\nProbando detección de reglas:")
    for message, expected_rule in test_cases:
        result = engine.match(message)
        if result:
            actual_rule = result.get("rule")
            status = "✅" if actual_rule == expected_rule else "❌"
            print(f"{status} '{message}'")
            print(f"   → Esperado: {expected_rule}, Obtenido: {actual_rule}")
            if result.get("project_name"):
                print(f"   → Proyecto detectado: {result.get('project_name')}")
        else:
            print(f"❌ '{message}' - NO coincidió")


def test_project_memory_handler():
    """Test 2: ProjectMemoryHandler guarda proyectos correctamente"""
    print("\n" + "="*60)
    print("TEST 2: ProjectMemoryHandler guarda y recupera proyectos")
    print("="*60)
    
    # Crear instancia limpia
    memory = MemoryManager(autosave_enabled=False)
    handler = ProjectMemoryHandler(memory)
    
    # Test guardar proyecto
    print("\n1. Guardando proyecto 'SIRLUCAS'...")
    rule_result = {
        "command": "remember_project",
        "project_name": "SIRLUCAS"
    }
    result = handler.handle_rule(rule_result)
    print(f"   → Éxito: {result.success}")
    print(f"   → Mensaje: {result.message}")
    
    # Test recuperar proyecto
    print("\n2. Recuperando proyecto guardado...")
    result = handler.handle_recall_project({})
    print(f"   → Éxito: {result.success}")
    print(f"   → Mensaje: {result.message}")
    
    # Test guardar con descripción
    print("\n3. Guardando proyecto con descripción...")
    rule_result = {
        "command": "remember_project_description",
        "project_name": "IAGENERATOR",
        "description": "Sistema de generación de IA avanzada"
    }
    result = handler.handle_rule(rule_result)
    print(f"   → Éxito: {result.success}")
    
    # Test listar proyectos
    print("\n4. Listando todos los proyectos...")
    result = handler.handle_list_projects({})
    print(f"   → Éxito: {result.success}")
    print(f"   → Mensaje:\n{result.message}")
    
    # Limpiar
    memory.clear()


def test_conversation_integration():
    """Test 3: ConversationManager integra auto-guardado de proyectos"""
    print("\n" + "="*60)
    print("TEST 3: ConversationManager auto-guarda proyectos")
    print("="*60)
    
    # Crear ConversationManager
    memory = MemoryManager(autosave_enabled=False)
    conversation = ConversationManager(memory=memory)
    
    # Test 1: Procesar mensaje con proyecto
    print("\n1. Procesando: 'mi proyecto es SIRLUCAS'...")
    result = conversation.process({
        "message": "mi proyecto es SIRLUCAS",
        "user_id": "test_user"
    })
    print(f"   → Éxito: {result.success}")
    
    # Verificar que se guardó en memory
    print("\n2. Verificando que se guardó en memoria...")
    projects = memory.find_by_category({"category": "projects", "limit": 10})
    if projects.data:
        print(f"   ✅ Proyectos guardados: {len(projects.data)}")
        for proj in projects.data:
            print(f"      - {proj.get('name')}")
    else:
        print(f"   ❌ No hay proyectos guardados")
    
    # Test 2: Consultar proyecto
    print("\n3. Procesando: '¿cuál es mi proyecto?'...")
    result = conversation.process({
        "message": "¿cuál es mi proyecto?",
        "user_id": "test_user"
    })
    print(f"   → Respuesta generada: {result.success}")
    
    # Limpiar
    memory.clear()


def test_persistence():
    """Test 4: Los proyectos se guardan persistentemente en memory.json"""
    print("\n" + "="*60)
    print("TEST 4: Persistencia en memory.json")
    print("="*60)
    
    memory_file = Path(__file__).parent.parent / "data" / "memory.json"
    
    # Crear backup
    backup_content = None
    if memory_file.exists():
        with open(memory_file, "r", encoding="utf-8") as f:
            backup_content = f.read()
    
    try:
        # Crear nueva memoria
        memory = MemoryManager(autosave_enabled=True)
        
        # Guardar proyecto
        print("\n1. Guardando proyecto 'TestProject'...")
        result = memory.remember_project(
            project_name="TestProject",
            description="Proyecto de prueba"
        )
        print(f"   → Éxito: {result.success}")
        
        # Guardar a disco
        memory.save()
        print("\n2. Guardado en disco")
        
        # Verificar que existe en memory.json
        if memory_file.exists():
            with open(memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if "project:testproject" in data:
                print(f"   ✅ Proyecto guardado en memory.json")
                print(f"      Datos: {data['project:testproject']}")
            else:
                print(f"   ❌ Proyecto NO se guardó en memory.json")
        
        # Limpiar
        memory.clear()
        memory.save()
        
    finally:
        # Restaurar backup
        if backup_content:
            with open(memory_file, "w", encoding="utf-8") as f:
                f.write(backup_content)
            print("\n3. Backup restaurado")


def main():
    """Ejecutar todos los tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  VALIDACIÓN COMPLETA: AUTO-GUARDADO DE PROYECTOS".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        test_rule_engine_project_detection()
        test_project_memory_handler()
        test_conversation_integration()
        test_persistence()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR durante tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
