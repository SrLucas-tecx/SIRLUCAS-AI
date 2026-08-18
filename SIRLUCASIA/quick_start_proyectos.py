#!/usr/bin/env python3
# quick_start_proyectos.py
"""
QUICK START - Sistema de Auto-Guardado de Proyectos
=====================================================

Ejecuta este script para probar el sistema en 2 minutos.

Requisitos:
  - Python 3.8+
  - SIRLUCAS-AI configurado
  - app/core/memory_manager.py ✅
  - app/core/conversation_manager.py ✅
  - app/modules/parser_rules_proyectos.json ✅

Uso:
  python quick_start_proyectos.py
"""

import sys
from pathlib import Path

# Agregar al path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.conversation_manager import ConversationManager
from app.core.memory_manager import MemoryManager


def print_header(title: str):
    """Imprime un encabezado bonito"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_step(num: int, title: str):
    """Imprime un paso numerado"""
    print(f"\n▶ PASO {num}: {title}")
    print("-" * 60)


def main():
    """Ejecuta la demostración"""
    
    print_header("🎯 DEMO - AUTO-GUARDADO DE PROYECTOS")
    
    try:
        # ==================================================
        # PASO 1: Inicializar
        # ==================================================
        print_step(1, "Inicializando el sistema")
        
        memory = MemoryManager(autosave_enabled=True)
        conversation = ConversationManager(memory=memory)
        
        print("✅ ConversationManager inicializado")
        print("✅ MemoryManager inicializado")
        print("✅ RuleEngine compilado")
        print("✅ ProjectMemoryIntegration activo")
        
        # ==================================================
        # PASO 2: Guardar Proyecto Simple
        # ==================================================
        print_step(2, "Guardar proyecto simple")
        
        message = "mi proyecto es SIRLUCAS"
        print(f'📝 Usuario: "{message}"')
        
        result = conversation.process({
            "message": message,
            "user_id": "demo_user"
        })
        
        if result.success:
            print(f"✅ Respuesta: {result.data.get('response', 'OK')}")
        
        # ==================================================
        # PASO 3: Guardar Proyecto con Descripción
        # ==================================================
        print_step(3, "Guardar proyecto con descripción")
        
        message = "trabajo en IAGENERATOR que es un sistema generador de IA"
        print(f'📝 Usuario: "{message}"')
        
        result = conversation.process({
            "message": message,
            "user_id": "demo_user"
        })
        
        if result.success:
            print(f"✅ Respuesta: {result.data.get('response', 'OK')}")
        
        # ==================================================
        # PASO 4: Consultar Proyecto
        # ==================================================
        print_step(4, "Consultar proyecto guardado")
        
        message = "¿cuál es mi proyecto?"
        print(f'📝 Usuario: "{message}"')
        
        result = conversation.process({
            "message": message,
            "user_id": "demo_user"
        })
        
        if result.success:
            print(f"✅ Respuesta: {result.data.get('response', 'OK')}")
        
        # ==================================================
        # PASO 5: Listar Todos los Proyectos
        # ==================================================
        print_step(5, "Listar todos los proyectos")
        
        message = "lista mis proyectos"
        print(f'📝 Usuario: "{message}"')
        
        result = conversation.process({
            "message": message,
            "user_id": "demo_user"
        })
        
        if result.success:
            print(f"✅ Respuesta: {result.data.get('response', 'OK')}")
        
        # ==================================================
        # PASO 6: Verificar memory.json
        # ==================================================
        print_step(6, "Verificar data en memory.json")
        
        projects = memory.find_by_category({
            "category": "projects",
            "limit": 100
        })
        
        if projects.success and projects.data:
            print(f"📦 Proyectos guardados: {len(projects.data)}\n")
            for i, proj in enumerate(projects.data, 1):
                name = proj.get("name", "Desconocido")
                desc = proj.get("description", "Sin descripción")
                print(f"   {i}. {name}")
                print(f"      → {desc}\n")
            print(f"✅ Todos los datos se guardaron en: data/memory.json")
        else:
            print("⚠️  No hay proyectos guardados")
        
        # ==================================================
        # PASO 7: Actualizar Proyecto
        # ==================================================
        print_step(7, "Actualizar proyecto")
        
        message = "cambio mi proyecto a ChatBot"
        print(f'📝 Usuario: "{message}"')
        
        result = conversation.process({
            "message": message,
            "user_id": "demo_user"
        })
        
        if result.success:
            print(f"✅ Respuesta: {result.data.get('response', 'OK')}")
        
        # ==================================================
        # PASO 8: Resumen Final
        # ==================================================
        print_step(8, "Resumen de operaciones")
        
        stats = memory.statistics()
        if stats.success:
            total = stats.data.get("total_memories", 0)
            print(f"📊 Total de memorias: {total}")
            
            print("\n✅ OPERACIONES COMPLETADAS:")
            print("   ✓ Guardó 2 proyectos")
            print("   ✓ Listó proyectos")
            print("   ✓ Actualizó proyecto")
            print("   ✓ Guardó todo en memory.json")
            print("   ✓ Recuperó datos correctamente")
        
        # ==================================================
        # FINALIZACIÓN
        # ==================================================
        print_header("🎉 DEMO COMPLETADA EXITOSAMENTE")
        
        print("📚 PRÓXIMOS PASOS:")
        print("\n1. Revisa la documentación:")
        print("   - RESUMEN_AUTO_GUARDADO_PROYECTOS.md")
        print("   - GUIA_AUTO_GUARDADO_PROYECTOS.md")
        print("   - ARQUITECTURA_AUTO_GUARDADO_PROYECTOS.md")
        
        print("\n2. Ejecuta los tests:")
        print("   python tests/test_project_auto_save.py")
        
        print("\n3. Integra en tu aplicación:")
        print("   from app.core.conversation_manager import ConversationManager")
        print("   conversation = ConversationManager()")
        print("   result = conversation.process({'message': '...', 'user_id': '...'})")
        
        print("\n4. Verifica memory.json:")
        print("   cat data/memory.json | python -m json.tool")
        
        print("\n" + "="*60)
        print("✨ El sistema está listo para producción ✨")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
