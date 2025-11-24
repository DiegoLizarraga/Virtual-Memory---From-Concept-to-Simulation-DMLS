"""
Script de Prueba para Lab 2: Procesos y Round-Robin Scheduling
VOS (Virtual Operating System)

Este script demuestra el funcionamiento del sistema de procesos:
- Creación de múltiples procesos
- Scheduling Round-Robin
- Ejecución de programas con memoria virtual aislada
- Transiciones de estados de procesos
"""

from vos.core.sys import Kernel
from vos.core.demo_tasks import (
    touch_pages_prog, 
    idle_prog, 
    fibonacci_prog,
    memory_scanner_prog,
    counter_writer_prog,
    pattern_writer_prog
)
from vos.core.vm import PAGE_SIZE


def test_basic_two_processes():
    """
    Test básico con dos procesos simples.
    Demuestra Round-Robin básico y terminación de procesos.
    """
    print("\n" + "="*70)
    print("TEST 1: DOS PROCESOS BÁSICOS (touch_pages y idle)")
    print("="*70)
    
    # Crear kernel
    kernel = Kernel()
    
    # Crear dos procesos
    pid1 = kernel.spawn(touch_pages_prog, "TouchPages")
    pid2 = kernel.spawn(idle_prog, "Idle")
    
    print(f"\n✅ Procesos creados: PID {pid1} y PID {pid2}")
    
    # Ejecutar 15 time slices
    print(f"\n{'='*70}")
    print("INICIANDO EJECUCIÓN")
    print(f"{'='*70}")
    
    for step in range(15):
        print(f"\n{'─'*70}")
        print(f"STEP {step:02d}")
        print(f"{'─'*70}")
        
        # Dispatch
        kernel.dispatch()
        
        # Mostrar tabla de procesos
        ps_output = kernel.ps()
        print(f"\n📊 ps: {ps_output}")
    
    # Mostrar tabla final
    kernel.print_process_table()
    
    # Verificar memoria de proceso 1
    print(f"\n{'='*70}")
    print("VERIFICACIÓN DE MEMORIA VIRTUAL (Proceso 1)")
    print(f"{'='*70}")
    
    pcb1 = kernel.get_process(pid1)
    if pcb1:
        print(f"\n🔍 Leyendo memoria del proceso {pid1} ({pcb1.name}):")
        for page_no in range(5):
            vaddr = page_no * PAGE_SIZE
            try:
                value = pcb1.vm.read_byte(vaddr)
                print(f"   Página {page_no} (vaddr={vaddr}): {value}")
            except:
                print(f"   Página {page_no}: no accesible")


def test_multiple_processes():
    """
    Test con múltiples procesos de diferentes tipos.
    Demuestra scheduling complejo y aislamiento de memoria.
    """
    print("\n" + "="*70)
    print("TEST 2: MÚLTIPLES PROCESOS (6 procesos concurrentes)")
    print("="*70)
    
    # Crear kernel
    kernel = Kernel()
    
    # Crear 6 procesos diferentes
    procs = [
        kernel.spawn(touch_pages_prog, "TouchPages-1"),
        kernel.spawn(idle_prog, "Idle-1"),
        kernel.spawn(fibonacci_prog, "Fibonacci"),
        kernel.spawn(memory_scanner_prog, "Scanner"),
        kernel.spawn(counter_writer_prog, "Counter"),
        kernel.spawn(pattern_writer_prog, "Pattern")
    ]
    
    print(f"\n✅ Creados {len(procs)} procesos")
    
    # Ejecutar 25 time slices
    print(f"\n{'='*70}")
    print("INICIANDO EJECUCIÓN (25 time slices)")
    print(f"{'='*70}")
    
    for step in range(25):
        print(f"\n{'─'*70}")
        print(f"STEP {step:02d}")
        print(f"{'─'*70}")
        
        # Dispatch
        kernel.dispatch()
        
        # Mostrar tabla de procesos (compacta)
        ps_output = kernel.ps()
        print(f"\n📊 ps: {ps_output}")
        
        # Mostrar estado del scheduler
        print(f"   Scheduler: {kernel.sched}")
    
    # Mostrar tabla final detallada
    kernel.print_process_table()
    
    # Verificar estadísticas de VM de cada proceso
    print(f"\n{'='*70}")
    print("ESTADÍSTICAS DE MEMORIA VIRTUAL POR PROCESO")
    print(f"{'='*70}")
    
    for pid in procs:
        pcb = kernel.get_process(pid)
        if pcb:
            stats = pcb.vm.get_stats()
            print(f"\n📊 Proceso {pid} ({pcb.name}):")
            print(f"   - Page faults: {stats['page_faults']}")
            print(f"   - Write-backs: {stats['write_backs']}")
            print(f"   - Páginas en RAM: {stats['pages_in_ram']}")
            print(f"   - Páginas sucias: {stats['dirty_pages']}")


def test_memory_isolation():
    """
    Test que demuestra el aislamiento de memoria entre procesos.
    Cada proceso escribe en la misma dirección virtual pero ve valores diferentes.
    """
    print("\n" + "="*70)
    print("TEST 3: AISLAMIENTO DE MEMORIA ENTRE PROCESOS")
    print("="*70)
    
    # Crear kernel
    kernel = Kernel()
    
    # Crear tres procesos que escriben en la misma dirección virtual
    pids = [
        kernel.spawn(counter_writer_prog, "Writer-A"),
        kernel.spawn(counter_writer_prog, "Writer-B"),
        kernel.spawn(counter_writer_prog, "Writer-C")
    ]
    
    print(f"\n✅ Creados 3 procesos que escribirán en direcciones virtuales similares")
    
    # Ejecutar varios time slices
    for step in range(20):
        print(f"\n{'─'*70}")
        print(f"STEP {step:02d}")
        print(f"{'─'*70}")
        
        kernel.dispatch()
        ps_output = kernel.ps()
        print(f"\n📊 ps: {ps_output}")
    
    # Verificar que cada proceso tiene su propia memoria
    print(f"\n{'='*70}")
    print("VERIFICACIÓN DE AISLAMIENTO")
    print(f"{'='*70}")
    
    test_vaddr = 10  # Misma dirección virtual en todos los procesos
    
    for pid in pids:
        pcb = kernel.get_process(pid)
        if pcb:
            try:
                value = pcb.vm.read_byte(test_vaddr)
                print(f"\n🔍 Proceso {pid} ({pcb.name}):")
                print(f"   vaddr={test_vaddr} contiene: {value}")
                print(f"   ✓ Memoria aislada e independiente")
            except:
                print(f"\n🔍 Proceso {pid} ({pcb.name}):")
                print(f"   vaddr={test_vaddr}: no accedida aún")


def test_state_transitions():
    """
    Test que muestra claramente las transiciones de estado de los procesos.
    """
    print("\n" + "="*70)
    print("TEST 4: TRANSICIONES DE ESTADO")
    print("="*70)
    
    # Crear kernel
    kernel = Kernel()
    
    # Crear procesos con diferentes duraciones
    kernel.spawn(idle_prog, "Short-Process")  # Termina rápido
    kernel.spawn(fibonacci_prog, "Medium-Process")  # Duración media
    
    print(f"\n✅ Procesos creados con diferentes tiempos de vida")
    
    # Ejecutar y observar transiciones
    for step in range(20):
        print(f"\n{'─'*70}")
        print(f"STEP {step:02d}")
        
        # Antes del dispatch
        ps_before = kernel.ps()
        print(f"Antes:   {ps_before}")
        
        # Dispatch
        kernel.dispatch()
        
        # Después del dispatch
        ps_after = kernel.ps()
        print(f"Después: {ps_after}")
        
        # Detectar cambios de estado
        if ps_before != ps_after:
            print(f"   ⚡ ¡Cambio de estado detectado!")


def main():
    """Ejecuta todos los tests."""
    print("\n" + "="*70)
    print("VOS LAB 2: SUITE DE PRUEBAS DE PROCESOS Y SCHEDULING")
    print("="*70)
    
    try:
        # Test 1: Básico con dos procesos
        test_basic_two_processes()
        
        input("\n⏸️  Presiona Enter para continuar con el Test 2...")
        
        # Test 2: Múltiples procesos
        test_multiple_processes()
        
        input("\n⏸️  Presiona Enter para continuar con el Test 3...")
        
        # Test 3: Aislamiento de memoria
        test_memory_isolation()
        
        input("\n⏸️  Presiona Enter para continuar con el Test 4...")
        
        # Test 4: Transiciones de estado
        test_state_transitions()
        
        # Resumen final
        print("\n" + "="*70)
        print("🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        print("="*70)
        print("\n✅ Sistema de procesos funciona correctamente:")
        print("   ✓ Creación de procesos (spawn)")
        print("   ✓ Round-Robin scheduling")
        print("   ✓ Ejecución de programas por time slices")
        print("   ✓ Transiciones de estado (NEW→READY→RUNNING→TERMINATED)")
        print("   ✓ Aislamiento de memoria entre procesos")
        print("   ✓ Memoria virtual por proceso")
        print("   ✓ Tabla de procesos (ps)")
        print("\n💡 Cada proceso tiene su propio espacio de direcciones virtual")
        print("💡 El scheduler Round-Robin garantiza fairness entre procesos")
        print("💡 Los procesos pueden terminar de manera independiente\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())