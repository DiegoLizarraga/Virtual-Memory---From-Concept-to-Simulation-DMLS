"""
Demo Programs (Tasks) para Procesos
VOS (Virtual Operating System) - Lab 2

Este módulo contiene programas de ejemplo que pueden ejecutarse como procesos.
Cada programa está diseñado para demostrar diferentes aspectos del sistema.
"""

from vos.core.process import State
from vos.core.vm import PAGE_SIZE


def touch_pages_prog(kernel, pcb):
    """
    Programa que escribe el PID del proceso en su propia memoria virtual.
    
    Este programa demuestra:
    - Uso de memoria virtual por proceso
    - Aislamiento de espacios de direcciones
    - Page faults al acceder memoria nueva
    
    Comportamiento:
    - En cada time slice, escribe su PID en una página diferente
    - Escribe en offset 0 de cada página
    - Después de tocar NUM_PAGES páginas, termina
    
    Args:
        kernel: Instancia del Kernel (no usado aquí)
        pcb: Process Control Block del proceso
    """
    NUM_PAGES = 5  # Número total de páginas a tocar
    
    # Inicializar contador si no existe
    if not hasattr(pcb, '_touch_counter'):
        pcb._touch_counter = 0
        print(f"   🔧 [{pcb.name}] Inicializando contador de páginas")
    
    # Verificar si ya terminamos
    if pcb._touch_counter >= NUM_PAGES:
        print(f"   ✅ [{pcb.name}] Completado: tocadas {NUM_PAGES} páginas")
        pcb.state = State.TERMINATED
        return
    
    # Calcular dirección virtual: página i, offset 0
    page_no = pcb._touch_counter
    vaddr = page_no * PAGE_SIZE + 0
    
    # Escribir PID en memoria virtual propia
    print(f"   📝 [{pcb.name}] Escribiendo PID {pcb.pid} en vaddr={vaddr} (página {page_no})")
    pcb.vm.write_byte(vaddr, pcb.pid)
    
    # Leer de vuelta para verificar
    value = pcb.vm.read_byte(vaddr)
    print(f"   ✓ [{pcb.name}] Verificado: leído valor {value}")
    
    # Incrementar contador
    pcb._touch_counter += 1
    
    # Si terminamos, marcar como TERMINATED
    if pcb._touch_counter >= NUM_PAGES:
        print(f"   🏁 [{pcb.name}] Terminando después de tocar {NUM_PAGES} páginas")
        pcb.state = State.TERMINATED


def idle_prog(kernel, pcb):
    """
    Programa simple que solo cuenta time slices.
    
    Este programa demuestra:
    - Proceso mínimo sin acceso a memoria
    - Terminación después de N time slices
    
    Comportamiento:
    - Incrementa contador en cada time slice
    - Después de MAX_SLICES, termina
    
    Args:
        kernel: Instancia del Kernel (no usado aquí)
        pcb: Process Control Block del proceso
    """
    MAX_SLICES = 8  # Número de time slices antes de terminar
    
    # Inicializar contador si no existe
    if not hasattr(pcb, '_idle_counter'):
        pcb._idle_counter = 0
        print(f"   🔧 [{pcb.name}] Proceso idle iniciado")
    
    # Incrementar contador
    pcb._idle_counter += 1
    print(f"   ⏳ [{pcb.name}] Slice {pcb._idle_counter}/{MAX_SLICES}")
    
    # Terminar después de MAX_SLICES
    if pcb._idle_counter >= MAX_SLICES:
        print(f"   🏁 [{pcb.name}] Terminando después de {MAX_SLICES} slices")
        pcb.state = State.TERMINATED


def fibonacci_prog(kernel, pcb):
    """
    Programa que calcula números de Fibonacci y los almacena en memoria virtual.
    
    Este programa demuestra:
    - Cómputo real en un proceso
    - Almacenamiento de resultados en VM
    - Uso de múltiples páginas de memoria
    
    Comportamiento:
    - En cada time slice, calcula el siguiente número de Fibonacci
    - Almacena el resultado (módulo 256) en memoria virtual
    - Después de calcular N números, termina
    
    Args:
        kernel: Instancia del Kernel (no usado aquí)
        pcb: Process Control Block del proceso
    """
    MAX_NUMBERS = 10  # Cantidad de números de Fibonacci a calcular
    
    # Inicializar estado si no existe
    if not hasattr(pcb, '_fib_state'):
        pcb._fib_state = {
            'count': 0,
            'prev': 0,
            'curr': 1
        }
        print(f"   🔧 [{pcb.name}] Iniciando secuencia de Fibonacci")
    
    state = pcb._fib_state
    
    # Verificar si terminamos
    if state['count'] >= MAX_NUMBERS:
        print(f"   ✅ [{pcb.name}] Completado: calculados {MAX_NUMBERS} números")
        pcb.state = State.TERMINATED
        return
    
    # Calcular siguiente número de Fibonacci
    fib_value = state['curr']
    next_fib = state['prev'] + state['curr']
    
    # Actualizar estado
    state['prev'] = state['curr']
    state['curr'] = next_fib
    
    # Almacenar en memoria virtual (módulo 256 para que quepa en un byte)
    vaddr = state['count'] * 4  # Esparcir en memoria
    byte_value = fib_value % 256
    
    print(f"   🔢 [{pcb.name}] Fib[{state['count']}] = {fib_value} (guardando {byte_value} en vaddr={vaddr})")
    pcb.vm.write_byte(vaddr, byte_value)
    
    # Incrementar contador
    state['count'] += 1
    
    # Terminar si completamos
    if state['count'] >= MAX_NUMBERS:
        print(f"   🏁 [{pcb.name}] Terminando después de {MAX_NUMBERS} números")
        pcb.state = State.TERMINATED


def memory_scanner_prog(kernel, pcb):
    """
    Programa que escanea y verifica su propia memoria virtual.
    
    Este programa demuestra:
    - Lectura de memoria virtual
    - Detección de page faults
    - Patrón de acceso secuencial a memoria
    
    Comportamiento:
    - En cada time slice, lee de una dirección diferente
    - Imprime el valor leído
    - Después de escanear N direcciones, termina
    
    Args:
        kernel: Instancia del Kernel (no usado aquí)
        pcb: Process Control Block del proceso
    """
    NUM_READS = 6  # Número de lecturas a realizar
    
    # Inicializar contador si no existe
    if not hasattr(pcb, '_scan_counter'):
        pcb._scan_counter = 0
        print(f"   🔧 [{pcb.name}] Iniciando escaneo de memoria")
    
    # Verificar si terminamos
    if pcb._scan_counter >= NUM_READS:
        print(f"   ✅ [{pcb.name}] Completado: escaneadas {NUM_READS} direcciones")
        pcb.state = State.TERMINATED
        return
    
    # Calcular dirección a leer (páginas diferentes)
    page_no = pcb._scan_counter
    vaddr = page_no * PAGE_SIZE + 10
    
    # Leer de memoria virtual
    print(f"   🔍 [{pcb.name}] Leyendo vaddr={vaddr} (página {page_no})")
    value = pcb.vm.read_byte(vaddr)
    print(f"   ✓ [{pcb.name}] Valor leído: {value}")
    
    # Incrementar contador
    pcb._scan_counter += 1
    
    # Terminar si completamos
    if pcb._scan_counter >= NUM_READS:
        print(f"   🏁 [{pcb.name}] Terminando después de {NUM_READS} lecturas")
        pcb.state = State.TERMINATED


def counter_writer_prog(kernel, pcb):
    """
    Programa que escribe un contador incremental en memoria.
    
    Este programa demuestra:
    - Escrituras repetidas a memoria
    - Modificación de páginas (dirty bit)
    - Uso simple de VM
    
    Comportamiento:
    - En cada time slice, escribe el valor del contador en memoria
    - Incrementa el contador
    - Después de N escrituras, termina
    
    Args:
        kernel: Instancia del Kernel (no usado aquí)
        pcb: Process Control Block del proceso
    """
    MAX_WRITES = 7  # Número de escrituras a realizar
    
    # Inicializar contador si no existe
    if not hasattr(pcb, '_counter'):
        pcb._counter = 0
        print(f"   🔧 [{pcb.name}] Iniciando contador desde 0")
    
    # Verificar si terminamos
    if pcb._counter >= MAX_WRITES:
        print(f"   ✅ [{pcb.name}] Completado: {MAX_WRITES} escrituras")
        pcb.state = State.TERMINATED
        return
    
    # Escribir contador en memoria (diferentes páginas)
    page_no = pcb._counter % 4  # Rotar entre 4 páginas
    vaddr = page_no * PAGE_SIZE + (pcb._counter * 2)
    value = (pcb._counter * 10) % 256
    
    print(f"   ✍️  [{pcb.name}] Escribiendo {value} en vaddr={vaddr}")
    pcb.vm.write_byte(vaddr, value)
    
    # Incrementar contador
    pcb._counter += 1
    
    # Terminar si completamos
    if pcb._counter >= MAX_WRITES:
        print(f"   🏁 [{pcb.name}] Terminando después de {MAX_WRITES} escrituras")
        pcb.state = State.TERMINATED


def pattern_writer_prog(kernel, pcb):
    """
    Programa que escribe un patrón específico en múltiples páginas.
    
    Este programa demuestra:
    - Escritura de patrones en memoria
    - Uso de múltiples páginas
    - Dirty pages y page faults
    
    Comportamiento:
    - Escribe el patrón (PID * 10 + offset) en varias ubicaciones
    - Usa un bucle for interno para escribir múltiples bytes por slice
    - Termina después de escribir en N páginas
    
    Args:
        kernel: Instancia del Kernel (no usado aquí)
        pcb: Process Control Block del proceso
    """
    NUM_PAGES = 4  # Número de páginas a escribir
    
    # Inicializar contador si no existe
    if not hasattr(pcb, '_pattern_page'):
        pcb._pattern_page = 0
        print(f"   🔧 [{pcb.name}] Iniciando escritura de patrón")
    
    # Verificar si terminamos
    if pcb._pattern_page >= NUM_PAGES:
        print(f"   ✅ [{pcb.name}] Completado: patrón escrito en {NUM_PAGES} páginas")
        pcb.state = State.TERMINATED
        return
    
    # Escribir patrón en la página actual
    page_no = pcb._pattern_page
    base_addr = page_no * PAGE_SIZE
    
    print(f"   🎨 [{pcb.name}] Escribiendo patrón en página {page_no}")
    
    # Escribir algunos bytes con patrón
    for offset in range(0, 15, 3):  # Escribir cada 3 bytes
        vaddr = base_addr + offset
        value = (pcb.pid * 10 + offset) % 256
        pcb.vm.write_byte(vaddr, value)
        print(f"      ✓ vaddr={vaddr}: {value}")
    
    # Avanzar a siguiente página
    pcb._pattern_page += 1
    
    # Terminar si completamos
    if pcb._pattern_page >= NUM_PAGES:
        print(f"   🏁 [{pcb.name}] Terminando después de escribir {NUM_PAGES} páginas")
        pcb.state = State.TERMINATED