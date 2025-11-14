"""
Script de prueba para el simulador de memoria virtual VOS.

Este script demuestra el funcionamiento del simulador mediante:
- Pruebas básicas de lectura/escritura
- Generación de page faults
- Activación del algoritmo de reemplazo FIFO
- Verificación de write-backs de páginas sucias
"""

from vos.core.vm import VM, PAGE_SIZE

def test_basic_read_write():
    """Prueba básica de lectura y escritura."""
    print("=" * 70)
    print("TEST 1: Lectura y Escritura Básica")
    print("=" * 70)
    
    vm = VM()
    addr = 3 * PAGE_SIZE + 10  # Página 3, offset 10
    
    print(f"\n📝 Escribiendo 99 a dirección virtual {addr}")
    vm.write_byte(addr, 99)
    
    print(f"\n📖 Leyendo de dirección virtual {addr}")
    value = vm.read_byte(addr)
    
    print(f"\n✅ Valor leído: {value}")
    assert value == 99, f"Error: esperaba 99, obtuvo {value}"
    print("✅ TEST 1 PASADO: Lectura/escritura funciona correctamente\n")
    
    return vm


def test_page_faults():
    """Prueba generación de múltiples page faults."""
    print("=" * 70)
    print("TEST 2: Generación de Page Faults")
    print("=" * 70)
    
    vm = VM()
    
    # Escribir a 5 páginas diferentes
    pages_to_test = [0, 2, 5, 7, 9]
    
    for page_no in pages_to_test:
        addr = page_no * PAGE_SIZE
        value = page_no * 10
        print(f"\n--- Accediendo página {page_no} ---")
        vm.write_byte(addr, value)
    
    print(f"\n📊 Estadísticas después de accesos:")
    stats = vm.get_stats()
    print(f"   - Page faults: {stats['page_faults']}")
    print(f"   - Páginas en RAM: {stats['pages_in_ram']}")
    print(f"   - Páginas sucias: {stats['dirty_pages']}")
    
    assert stats['page_faults'] == 5, "Debería haber 5 page faults"
    print("\n✅ TEST 2 PASADO: Page faults generados correctamente\n")
    
    return vm


def test_fifo_replacement():
    """Prueba el algoritmo de reemplazo FIFO."""
    print("=" * 70)
    print("TEST 3: Reemplazo FIFO")
    print("=" * 70)
    
    vm = VM()
    
    # Llenar todos los marcos físicos (8 marcos)
    print("\n🔄 Fase 1: Llenando RAM (8 marcos)...")
    for i in range(8):
        addr = i * PAGE_SIZE
        vm.write_byte(addr, i * 10)
        print(f"   Página {i} cargada")
    
    print(f"\n📊 RAM ahora llena: {vm.get_stats()['pages_in_ram']} páginas")
    
    # Acceder a una página nueva - debe causar reemplazo
    print("\n🔄 Fase 2: Accediendo página 8 (debe causar reemplazo FIFO)...")
    addr = 8 * PAGE_SIZE
    vm.write_byte(addr, 80)
    
    print(f"\n📊 Estadísticas después de reemplazo:")
    stats = vm.get_stats()
    print(f"   - Page faults: {stats['page_faults']}")
    print(f"   - Write-backs: {stats['write_backs']}")
    print(f"   - Páginas en RAM: {stats['pages_in_ram']}")
    print(f"   - Cola FIFO: {stats['fifo_queue']}")
    
    assert stats['page_faults'] == 9, "Debería haber 9 page faults"
    assert stats['write_backs'] >= 1, "Debería haber al menos 1 write-back"
    print("\n✅ TEST 3 PASADO: Reemplazo FIFO funciona correctamente\n")
    
    return vm


def test_dirty_bit():
    """Prueba el manejo del bit sucio."""
    print("=" * 70)
    print("TEST 4: Manejo de Dirty Bit")
    print("=" * 70)
    
    vm = VM()
    
    # Escribir a una página
    print("\n✍️  Escribiendo a página 0...")
    vm.write_byte(0, 42)
    
    # Leer de la misma página (no cambia dirty bit)
    print("📖 Leyendo de página 0...")
    value = vm.read_byte(0)
    
    # Verificar que la página está sucia
    entry = vm.page_table.get_entry(0)
    print(f"\n📊 Estado de página 0:")
    print(f"   - Present: {entry.present}")
    print(f"   - Dirty: {entry.dirty}")
    print(f"   - Frame: {entry.frame}")
    
    assert entry.dirty, "Página debería estar marcada como sucia"
    print("\n✅ TEST 4 PASADO: Dirty bit manejado correctamente\n")
    
    return vm


def test_zero_page():
    """Prueba la operación zero_page."""
    print("=" * 70)
    print("TEST 5: Zero Page")
    print("=" * 70)
    
    vm = VM()
    
    # Escribir algunos valores a página 0
    print("\n✍️  Escribiendo valores a página 0...")
    for i in range(10):
        vm.write_byte(i, i + 100)
    
    # Llenar página con ceros
    print("🧹 Llenando página 0 con ceros...")
    vm.zero_page(0)
    
    # Verificar que todos los bytes son 0
    print("📖 Verificando que página está llena de ceros...")
    all_zeros = True
    for i in range(10):
        value = vm.read_byte(i)
        if value != 0:
            all_zeros = False
            break
    
    assert all_zeros, "Todos los bytes deberían ser 0"
    print("\n✅ TEST 5 PASADO: Zero page funciona correctamente\n")
    
    return vm


def test_comprehensive():
    """Prueba comprensiva que ejercita todo el sistema."""
    print("=" * 70)
    print("TEST 6: Prueba Comprensiva")
    print("=" * 70)
    
    vm = VM()
    
    # Escribir a múltiples páginas con patrón conocido
    print("\n🔄 Escribiendo patrón de datos...")
    test_data = {}
    for page_no in range(12):  # Más de 8 páginas (causará reemplazos)
        addr = page_no * PAGE_SIZE + 5
        value = (page_no * 7 + 13) % 256
        test_data[addr] = value
        vm.write_byte(addr, value)
    
    # Leer de vuelta y verificar
    print("\n📖 Verificando datos...")
    errors = 0
    for addr, expected_value in test_data.items():
        actual_value = vm.read_byte(addr)
        if actual_value != expected_value:
            print(f"   ❌ Error en {addr}: esperaba {expected_value}, obtuvo {actual_value}")
            errors += 1
    
    print(f"\n📊 Estadísticas finales:")
    stats = vm.get_stats()
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    assert errors == 0, f"Se encontraron {errors} errores en los datos"
    print("\n✅ TEST 6 PASADO: Sistema completo funciona correctamente\n")
    
    return vm


def main():
    """Ejecuta todos los tests."""
    print("\n" + "=" * 70)
    print("INICIANDO SUITE DE PRUEBAS VOS")
    print("=" * 70 + "\n")
    
    try:
        # Ejecutar todos los tests
        test_basic_read_write()
        test_page_faults()
        test_fifo_replacement()
        test_dirty_bit()
        test_zero_page()
        test_comprehensive()
        
        print("=" * 70)
        print("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("=" * 70)
        print("\n✅ El simulador de memoria virtual funciona correctamente!")
        print("✅ Todos los componentes están operando como se espera:")
        print("   ✓ Traducción de direcciones")
        print("   ✓ Manejo de page faults")
        print("   ✓ Reemplazo FIFO")
        print("   ✓ Write-back de páginas sucias")
        print("   ✓ Gestión de dirty bits")
        print("   ✓ Operaciones de memoria\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
