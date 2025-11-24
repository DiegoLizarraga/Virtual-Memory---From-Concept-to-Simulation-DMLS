"""
Kernel del Sistema Operativo Virtual
VOS (Virtual Operating System) - Lab 2

Este módulo implementa el Kernel que gestiona procesos y scheduling.
"""

from typing import Dict, List, Tuple, Callable, Optional
from vos.core.process import PCB, State
from vos.core.sched import Scheduler


class Kernel:
    """
    Kernel del Sistema Operativo Virtual.
    
    El Kernel es el núcleo del sistema operativo que gestiona:
    - Creación de procesos (spawn)
    - Scheduling de procesos (dispatch)
    - Ejecución de programas de procesos
    - Transiciones de estado de procesos
    - Tabla de procesos del sistema
    
    Conceptos implementados:
        - Process Table: Diccionario de todos los PCBs del sistema
        - Current Running Process: Proceso actualmente ejecutándose
        - Time Slice Execution: Ejecutar una porción del programa por vez
        - Context Switch: Cambiar entre procesos
    
    Atributos:
        procs: Tabla de procesos (pid → PCB)
        sched: Scheduler Round-Robin
        running: Proceso actualmente en ejecución (o None)
        next_pid: Siguiente PID disponible
    """
    
    def __init__(self):
        """Inicializa el kernel con estructuras vacías."""
        self.procs: Dict[int, PCB] = {}           # Tabla de procesos
        self.sched: Scheduler = Scheduler()        # Scheduler Round-Robin
        self.running: Optional[PCB] = None         # Proceso actualmente ejecutándose
        self.next_pid: int = 1                     # Contador de PIDs
        
        print("🖥️  Kernel inicializado")
        print(f"   - Scheduler: Round-Robin")
        print(f"   - Ready queue: vacía")
        print(f"   - Procesos: 0\n")
    
    def spawn(self, prog: Callable, name: str = "") -> int:
        """
        Crea un nuevo proceso.
        
        Pasos:
        1. Asigna un nuevo PID único
        2. Crea un PCB con VM propia
        3. Asocia el programa al proceso
        4. Agrega el proceso a la tabla de procesos
        5. Transiciona el proceso a READY y lo agrega al scheduler
        
        Args:
            prog: Función que implementa el programa del proceso
                  Firma: prog(kernel, pcb) -> None
            name: Nombre descriptivo del proceso (opcional)
        
        Returns:
            PID del proceso creado
        """
        # Asignar PID único
        pid = self.next_pid
        self.next_pid += 1
        
        # Crear PCB
        pcb = PCB(
            pid=pid,
            state=State.NEW,
            prog=prog,
            name=name if name else f"Process-{pid}"
        )
        
        # Agregar a tabla de procesos
        self.procs[pid] = pcb
        
        print(f"\n🆕 SPAWN: Creando proceso {pid} ({pcb.name})")
        print(f"   - Estado inicial: {State.NEW.value}")
        print(f"   - VM propia: ✓")
        
        # Transición NEW → READY
        pcb.state = State.READY
        self.sched.add(pcb)
        
        print(f"   - Transición: NEW → READY")
        print(f"   - Agregado al scheduler")
        
        return pid
    
    def dispatch(self) -> None:
        """
        Ejecuta un time slice del scheduler Round-Robin.
        
        Algoritmo:
        1. Si hay un proceso running que aún está RUNNING:
           - Requearlo (RUNNING → READY)
           - Agregarlo de vuelta al scheduler
        
        2. Pedir al scheduler el siguiente proceso:
           - Si None: CPU idle, terminar
           - Si hay proceso: ejecutarlo
        
        3. Transicionar el proceso a RUNNING
        
        4. Ejecutar UN PASO del programa del proceso:
           - Llamar a pcb.prog(kernel, pcb)
           - El programa puede cambiar su estado a TERMINATED o WAITING
        
        5. Actualizar estadísticas (cpu_time)
        
        Nota: El proceso puede cambiar su propio estado durante la ejecución.
              El Kernel solo reencola procesos que permanecen RUNNING.
        """
        print(f"\n{'='*70}")
        print(f"⏰ DISPATCH: Iniciando time slice")
        print(f"{'='*70}")
        
        # PASO 1: Reencolar proceso anterior si aún está RUNNING
        if self.running is not None and self.running.state == State.RUNNING:
            print(f"\n🔄 Proceso {self.running.pid} ({self.running.name}) aún RUNNING")
            print(f"   - Transición: RUNNING → READY")
            self.running.state = State.READY
            self.sched.add(self.running)
        
        # PASO 2: Obtener siguiente proceso del scheduler
        print(f"\n📋 Scheduler state: {self.sched}")
        pcb = self.sched.next()
        
        if pcb is None:
            print(f"\n💤 CPU IDLE: No hay procesos listos para ejecutar")
            self.running = None
            return
        
        # PASO 3: Marcar proceso como RUNNING
        self.running = pcb
        pcb.state = State.RUNNING
        print(f"\n▶️  Ejecutando proceso {pcb.pid} ({pcb.name})")
        print(f"   - Estado: READY → RUNNING")
        print(f"   - CPU time usado hasta ahora: {pcb.cpu_time} slices")
        
        # PASO 4: Ejecutar UN PASO del programa
        try:
            print(f"\n🔧 Ejecutando programa del proceso {pcb.pid}...")
            pcb.prog(self, pcb)
            
            # PASO 5: Actualizar estadísticas
            pcb.cpu_time += 1
            
            print(f"\n✅ Time slice completado para proceso {pcb.pid}")
            print(f"   - Estado después de ejecución: {pcb.state.value}")
            print(f"   - CPU time total: {pcb.cpu_time} slices")
            
        except Exception as e:
            print(f"\n❌ ERROR en proceso {pcb.pid}: {e}")
            pcb.state = State.TERMINATED
            print(f"   - Proceso terminado forzosamente")
    
    def ps(self) -> List[Tuple[int, str]]:
        """
        Retorna tabla de procesos estilo comando 'ps'.
        
        Muestra información básica de todos los procesos en el sistema,
        similar al comando 'ps' de Unix/Linux.
        
        Returns:
            Lista de tuplas (pid, estado_nombre)
            Ejemplo: [(1, 'RUNNING'), (2, 'READY'), (3, 'TERMINATED')]
        """
        return [(pid, pcb.state.value) for pid, pcb in sorted(self.procs.items())]
    
    def ps_detailed(self) -> List[Dict]:
        """
        Retorna información detallada de todos los procesos.
        
        Returns:
            Lista de diccionarios con información completa de cada proceso
        """
        result = []
        for pid, pcb in sorted(self.procs.items()):
            result.append({
                'pid': pid,
                'name': pcb.name,
                'state': pcb.state.value,
                'cpu_time': pcb.cpu_time,
                'priority': pcb.priority
            })
        return result
    
    def get_process(self, pid: int) -> Optional[PCB]:
        """
        Obtiene el PCB de un proceso por su PID.
        
        Args:
            pid: Process ID
            
        Returns:
            PCB del proceso, o None si no existe
        """
        return self.procs.get(pid)
    
    def print_process_table(self) -> None:
        """Imprime tabla de procesos formateada."""
        print(f"\n{'='*70}")
        print(f"TABLA DE PROCESOS")
        print(f"{'='*70}")
        print(f"{'PID':<5} {'NAME':<20} {'STATE':<12} {'CPU TIME':<10}")
        print(f"{'-'*70}")
        
        for pcb in sorted(self.procs.values(), key=lambda p: p.pid):
            print(f"{pcb.pid:<5} {pcb.name:<20} {pcb.state.value:<12} {pcb.cpu_time:<10}")
        
        print(f"{'-'*70}")
        print(f"Total procesos: {len(self.procs)}")
        print(f"En ready queue: {self.sched.size()}")
        print(f"Running: {self.running.pid if self.running else 'None'}")
        print(f"{'='*70}\n")
    
    def __repr__(self) -> str:
        """Representación legible del kernel."""
        return (
            f"Kernel(procs={len(self.procs)}, "
            f"ready={self.sched.size()}, "
            f"running={self.running.pid if self.running else None})"
        )