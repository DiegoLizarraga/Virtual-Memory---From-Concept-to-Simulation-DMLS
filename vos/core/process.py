"""
Process Control Block (PCB) y Estados de Proceso
VOS (Virtual Operating System) - Lab 2

Este módulo define las estructuras fundamentales para la gestión de procesos:
- Enum de estados de proceso
- Clase PCB (Process Control Block)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional
from vos.core.vm import VM


class State(Enum):
    """
    Estados de un proceso en el sistema operativo.
    
    Transiciones típicas:
    NEW → READY → RUNNING → READY (time slice expired)
                          → WAITING (I/O request)
                          → TERMINATED (exit)
    WAITING → READY (I/O complete)
    """
    NEW = "NEW"                    # Proceso recién creado, no listo para ejecutar
    READY = "READY"                # Proceso listo para ejecutar, esperando CPU
    RUNNING = "RUNNING"            # Proceso actualmente ejecutándose
    WAITING = "WAITING"            # Proceso bloqueado esperando I/O u otro evento
    TERMINATED = "TERMINATED"      # Proceso finalizado


@dataclass
class PCB:
    """
    Process Control Block (Bloque de Control de Proceso).
    
    El PCB es la representación del sistema operativo de un proceso.
    Contiene toda la información necesaria para gestionar y ejecutar un proceso.
    
    Campos obligatorios:
        pid: Identificador único del proceso (Process ID)
        state: Estado actual del proceso (NEW, READY, RUNNING, WAITING, TERMINATED)
        vm: Objeto de memoria virtual propio del proceso (espacio de direcciones aislado)
        prog: Programa a ejecutar - función que implementa un "time slice"
    
    Campos opcionales:
        name: Nombre descriptivo del proceso
        cpu_time: Tiempo total de CPU usado por el proceso (en time slices)
        priority: Prioridad del proceso (no usado en Round-Robin básico)
        
    Propósito de cada campo:
        - pid: Identificación única, usado para debugging y gestión
        - state: Controla las transiciones del proceso en el scheduler
        - vm: Aislamiento de memoria - cada proceso tiene su propio espacio de direcciones
        - prog: El código real que el proceso ejecuta
        - cpu_time: Estadísticas y debugging
        - name: Facilita debugging y logging
    """
    pid: int
    state: State = State.NEW
    vm: VM = field(default_factory=VM)
    prog: Optional[Callable] = None
    name: str = ""
    cpu_time: int = 0
    priority: int = 0
    
    def __post_init__(self):
        """Inicialización adicional después de crear el PCB."""
        if not self.name:
            self.name = f"Process-{self.pid}"
    
    def __repr__(self) -> str:
        """Representación legible del PCB."""
        return (
            f"PCB(pid={self.pid}, name='{self.name}', "
            f"state={self.state.value}, cpu_time={self.cpu_time})"
        )