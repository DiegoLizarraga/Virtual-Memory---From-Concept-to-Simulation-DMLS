"""
VOS (Virtual Operating System) - Core Module
Lab 1: Virtual Memory
Lab 2: Processes and Scheduling

Este paquete contiene los componentes fundamentales del sistema operativo simulado.
"""

# Opcional: Puedes exportar las clases principales para facilitar imports

from vos.core.vm import VM, PageTable, PhysicalMemory, PTEntry, PAGE_SIZE, VIRTUAL_PAGES, PHYSICAL_FRAMES
from vos.core.process import PCB, State
from vos.core.sched import Scheduler
from vos.core.sys import Kernel

__all__ = [
    # VM Module (Lab 1)
    'VM',
    'PageTable', 
    'PhysicalMemory',
    'PTEntry',
    'PAGE_SIZE',
    'VIRTUAL_PAGES',
    'PHYSICAL_FRAMES',
    
    # Process Module (Lab 2)
    'PCB',
    'State',
    
    # Scheduler Module (Lab 2)
    'Scheduler',
    
    # System Module (Lab 2)
    'Kernel',
]

__version__ = '2.0.0'
__author__ = 'VOS Lab Team'