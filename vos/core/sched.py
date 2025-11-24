"""
Round-Robin Scheduler
VOS (Virtual Operating System) - Lab 2

Este módulo implementa un scheduler Round-Robin simple que gestiona
la cola de procesos listos para ejecutar.
"""

from typing import Optional, List
from collections import deque
from vos.core.process import PCB, State


class Scheduler:
    """
    Scheduler Round-Robin.
    
    Gestiona una cola FIFO de procesos en estado READY.
    El scheduler selecciona procesos de manera justa usando Round-Robin:
    cada proceso recibe un time slice igual, luego va al final de la cola.
    
    Conceptos clave:
        - Ready Queue: Cola de procesos listos para ejecutar
        - Fair Scheduling: Cada proceso recibe la misma oportunidad de CPU
        - Time Quantum: Duración de cada time slice (manejado por el Kernel)
        - FIFO Order: Los procesos se ejecutan en el orden que llegaron a READY
    
    Atributos:
        ready_queue: Cola de PCBs en estado READY
    """
    
    def __init__(self):
        """Inicializa el scheduler con una cola vacía."""
        self.ready_queue: deque[PCB] = deque()
    
    def add(self, pcb: PCB) -> None:
        """
        Agrega un proceso a la cola de listos.
        
        El proceso debe estar en estado READY antes de ser agregado.
        Esto es típicamente llamado por el Kernel cuando:
        - Un proceso nuevo es creado (NEW → READY)
        - Un proceso running expira su time slice (RUNNING → READY)
        - Un proceso bloqueado completa I/O (WAITING → READY)
        
        Args:
            pcb: Process Control Block a agregar
            
        Raises:
            ValueError: Si el proceso no está en estado READY
        """
        if pcb.state != State.READY:
            raise ValueError(
                f"Solo se pueden agregar procesos READY al scheduler. "
                f"Estado actual: {pcb.state.value}"
            )
        
        # Agregar al final de la cola (FIFO)
        self.ready_queue.append(pcb)
        print(f"   📋 Scheduler: Proceso {pcb.pid} ({pcb.name}) agregado a ready queue")
    
    def next(self) -> Optional[PCB]:
        """
        Obtiene el siguiente proceso a ejecutar.
        
        Implementa la política Round-Robin: toma el primer proceso de la cola.
        Si la cola está vacía, retorna None (CPU idle).
        
        El proceso retornado es removido de la cola. El Kernel debe
        re-agregarlo si el proceso no termina su ejecución.
        
        Returns:
            PCB del siguiente proceso a ejecutar, o None si no hay procesos
        """
        if not self.ready_queue:
            return None
        
        # Tomar el primer proceso de la cola (FIFO)
        pcb = self.ready_queue.popleft()
        print(f"   🎯 Scheduler: Seleccionado proceso {pcb.pid} ({pcb.name}) para ejecutar")
        return pcb
    
    def is_empty(self) -> bool:
        """
        Verifica si la cola de listos está vacía.
        
        Returns:
            True si no hay procesos listos, False en caso contrario
        """
        return len(self.ready_queue) == 0
    
    def size(self) -> int:
        """
        Retorna el número de procesos en la cola de listos.
        
        Returns:
            Cantidad de procesos READY esperando ejecutar
        """
        return len(self.ready_queue)
    
    def get_ready_pids(self) -> List[int]:
        """
        Obtiene lista de PIDs de procesos en la cola de listos.
        
        Útil para debugging y visualización del estado del scheduler.
        
        Returns:
            Lista de PIDs en orden FIFO
        """
        return [pcb.pid for pcb in self.ready_queue]
    
    def __repr__(self) -> str:
        """Representación legible del scheduler."""
        pids = self.get_ready_pids()
        return f"Scheduler(ready={len(pids)}, queue={pids})"