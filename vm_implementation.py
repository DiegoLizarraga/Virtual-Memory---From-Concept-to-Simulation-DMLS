"""
Simulador de Memoria Virtual con Paginación
VOS (Virtual Operating System) - Lab 1

Este módulo implementa un simulador completo de memoria virtual que incluye:
- Paginación con tabla de páginas
- Manejo de page faults
- Reemplazo de páginas FIFO
- Backing store simulado
- Gestión de dirty bits
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

# ============================================================================
# CONSTANTES DEL SISTEMA
# ============================================================================

PAGE_SIZE = 256          # Bytes por página/marco
VIRTUAL_PAGES = 16       # Número total de páginas virtuales
PHYSICAL_FRAMES = 8      # Número de marcos físicos en RAM


# ============================================================================
# ESTRUCTURAS DE DATOS
# ============================================================================

@dataclass
class PTEntry:
    """
    Entrada de Tabla de Páginas (Page Table Entry).
    
    Representa el mapeo de una página virtual a un marco físico,
    junto con bits de control que indican el estado de la página.
    
    Atributos:
        frame: Número de marco físico donde reside la página (None si no está en RAM)
        present: Bit de validez - True si la página está actualmente en memoria física
        dirty: Bit sucio - True si la página fue modificada (necesita write-back)
    """
    frame: Optional[int] = None
    present: bool = False
    dirty: bool = False


class PageTable:
    """
    Tabla de Páginas del proceso.
    
    Mapea números de página virtual (0 a VIRTUAL_PAGES-1) a entradas PTEntry.
    Esta estructura es fundamental para la traducción de direcciones virtuales
    a físicas en un sistema de memoria virtual con paginación.
    
    Propósito:
        - Permite traducción de direcciones virtuales a físicas
        - Mantiene estado de cada página (presente, sucia)
        - Habilita paginación bajo demanda (lazy loading)
    """
    
    def __init__(self):
        """Inicializa tabla vacía para todas las páginas virtuales."""
        self._entries: Dict[int, PTEntry] = {}
        # Crear entradas para todas las páginas virtuales
        for page_no in range(VIRTUAL_PAGES):
            self._entries[page_no] = PTEntry()
    
    def get_entry(self, page_no: int) -> PTEntry:
        """
        Obtiene entrada de tabla de páginas para una página virtual.
        
        Args:
            page_no: Número de página virtual
            
        Returns:
            Entrada PTEntry correspondiente
            
        Raises:
            ValueError: Si page_no está fuera de rango
        """
        if page_no not in self._entries:
            raise ValueError(f"Página {page_no} fuera de rango [0, {VIRTUAL_PAGES-1}]")
        return self._entries[page_no]
    
    def set_entry(self, page_no: int, entry: PTEntry) -> None:
        """
        Actualiza entrada de tabla de páginas.
        
        Args:
            page_no: Número de página virtual
            entry: Nueva entrada PTEntry
            
        Raises:
            ValueError: Si page_no está fuera de rango
        """
        if page_no not in self._entries:
            raise ValueError(f"Página {page_no} fuera de rango [0, {VIRTUAL_PAGES-1}]")
        self._entries[page_no] = entry


class PhysicalMemory:
    """
    Memoria Física (RAM simulada).
    
    Gestiona marcos de memoria física donde se cargan las páginas.
    Mantiene tanto los datos como la lista de marcos disponibles.
    
    Propósito:
        - Simula la RAM física limitada del sistema
        - Gestiona asignación/liberación de marcos
        - Almacena los datos reales de las páginas
    
    Atributos:
        frames: Mapeo de número de marco a bytearray con PAGE_SIZE bytes
        free_frames: Lista de números de marco disponibles para asignar
    """
    
    def __init__(self):
        """Inicializa PHYSICAL_FRAMES marcos, todos inicialmente libres."""
        # Cada marco es un bytearray de PAGE_SIZE bytes (inicialmente ceros)
        self.frames: Dict[int, bytearray] = {
            frame_no: bytearray(PAGE_SIZE)
            for frame_no in range(PHYSICAL_FRAMES)
        }
        # Todos los marcos empiezan disponibles
        self.free_frames: List[int] = list(range(PHYSICAL_FRAMES))
    
    def allocate_frame(self) -> Optional[int]:
        """
        Asigna un marco libre de la memoria física.
        
        Returns:
            Número de marco asignado, o None si no hay marcos libres
        """
        if not self.free_frames:
            return None  # Sin marcos disponibles - necesita reemplazo
        return self.free_frames.pop(0)  # FIFO: toma el primero
    
    def free_frame(self, frame_no: int) -> None:
        """
        Libera un marco para reutilización.
        
        Args:
            frame_no: Número de marco a liberar
            
        Raises:
            ValueError: Si frame_no es inválido o ya está libre
        """
        if frame_no not in self.frames:
            raise ValueError(f"Marco {frame_no} inválido [0, {PHYSICAL_FRAMES-1}]")
        if frame_no in self.free_frames:
            raise ValueError(f"Marco {frame_no} ya está libre")
        
        # Limpiar datos del marco (opcional pero buena práctica)
        self.frames[frame_no] = bytearray(PAGE_SIZE)
        # Marcar como disponible
        self.free_frames.append(frame_no)


# ============================================================================
# CLASE PRINCIPAL: SIMULADOR DE MEMORIA VIRTUAL
# ============================================================================

class VM:
    """
    Simulador de Memoria Virtual con Paginación.
    
    Implementa un sistema completo de memoria virtual con:
    - Traducción de direcciones virtuales a físicas
    - Manejo automático de page faults
    - Reemplazo de páginas usando algoritmo FIFO
    - Backing store para páginas no residentes
    - Gestión de dirty bits para optimizar write-backs
    
    El simulador proporciona una interfaz simple de lectura/escritura de bytes
    mientras maneja internamente toda la complejidad de la gestión de memoria.
    """
    
    def __init__(self):
        """
        Inicializa el simulador de memoria virtual.
        
        Crea todas las estructuras de datos necesarias:
        - Tabla de páginas para mapeo virtual→físico
        - Memoria física con marcos de tamaño fijo
        - Backing store para páginas en disco
        - Estructuras para algoritmo de reemplazo FIFO
        """
        # Tabla de páginas del proceso
        self.page_table = PageTable()
        
        # Memoria física (RAM simulada)
        self.physical_memory = PhysicalMemory()
        
        # Backing store - simula almacenamiento secundario (disco)
        # Almacena páginas que no están actualmente en RAM
        self.backing_store: Dict[int, bytearray] = {}
        
        # Cola FIFO - rastrea orden de llegada de páginas a RAM
        # La página al frente es la más antigua (candidata para reemplazo)
        self.fifo_queue: List[int] = []
        
        # Mapeo inverso: frame → page
        # Permite saber qué página está en cada marco
        self.frame_to_page: Dict[int, int] = {}
        
        # Estadísticas
        self.page_faults = 0
        self.write_backs = 0
    
    def _ensure_in_ram(self, page_no: int) -> None:
        """
        Asegura que una página esté cargada en RAM, manejando page faults si es necesario.
        
        Este método implementa el núcleo del sistema de memoria virtual:
        - Detecta si una página está presente en RAM
        - Maneja page faults cargando páginas desde backing store
        - Implementa reemplazo FIFO cuando RAM está llena
        - Realiza write-back de páginas sucias al disco
        
        Args:
            page_no: Número de página virtual a cargar (0 a VIRTUAL_PAGES-1)
            
        Raises:
            ValueError: Si page_no está fuera de rango
        """
        # Validación
        if not (0 <= page_no < VIRTUAL_PAGES):
            raise ValueError(f"Página {page_no} fuera de rango [0, {VIRTUAL_PAGES-1}]")
        
        # Obtener entrada de tabla de páginas
        entry = self.page_table.get_entry(page_no)
        
        # CASO 1: Página ya está en RAM (HIT)
        if entry.present:
            return  # Nada que hacer
        
        # CASO 2: PAGE FAULT - página no está en RAM
        print(f"⚠️  PAGE FAULT: página {page_no} no está en RAM")
        self.page_faults += 1
        
        # Intentar obtener un marco libre
        frame_no = self.physical_memory.allocate_frame()
        
        # Si no hay marcos libres, necesitamos reemplazar una página
        if frame_no is None:
            print("💾 RAM llena - ejecutando reemplazo FIFO")
            
            # FIFO: seleccionar víctima (la página más antigua en RAM)
            if not self.fifo_queue:
                raise RuntimeError("No hay páginas para desalojar")
            
            victim_page = self.fifo_queue.pop(0)  # Remover del frente (más antigua)
            print(f"   Víctima seleccionada: página {victim_page}")
            
            # Obtener información de la víctima
            victim_entry = self.page_table.get_entry(victim_page)
            victim_frame = victim_entry.frame
            
            # Si la víctima está sucia, escribirla de vuelta al backing store
            if victim_entry.dirty:
                print(f"   ✍️  Página {victim_page} está sucia - escribiendo a disco")
                # Copiar datos del marco al backing store
                self.backing_store[victim_page] = bytearray(
                    self.physical_memory.frames[victim_frame]
                )
                self.write_backs += 1
            else:
                print(f"   ✓ Página {victim_page} limpia - sin write-back necesario")
            
            # Actualizar entrada de la víctima (ya no está en RAM)
            victim_entry.present = False
            victim_entry.frame = None
            victim_entry.dirty = False
            
            # Remover mapeo inverso
            del self.frame_to_page[victim_frame]
            
            # Liberar el marco
            self.physical_memory.free_frame(victim_frame)
            
            # Ahora podemos asignar el marco recién liberado
            frame_no = self.physical_memory.allocate_frame()
            if frame_no is None:
                raise RuntimeError("Error al reasignar marco después de desalojo")
        
        # Cargar página del backing store (o inicializar con ceros si es nueva)
        if page_no in self.backing_store:
            print(f"   📖 Cargando página {page_no} desde backing store al marco {frame_no}")
            # Copiar datos del backing store al marco
            self.physical_memory.frames[frame_no] = bytearray(
                self.backing_store[page_no]
            )
        else:
            print(f"   🆕 Inicializando nueva página {page_no} con ceros en marco {frame_no}")
            # Página nueva - ya inicializada con ceros por PhysicalMemory
            pass
        
        # Actualizar entrada de tabla de páginas
        entry.frame = frame_no
        entry.present = True
        entry.dirty = False  # Recién cargada, no modificada aún
        
        # Actualizar estructuras de seguimiento
        self.fifo_queue.append(page_no)  # Agregar al final (más reciente)
        self.frame_to_page[frame_no] = page_no
        
        print(f"   ✅ Página {page_no} ahora en marco {frame_no}")
    
    def read_byte(self, vaddr: int) -> int:
        """
        Lee un byte de una dirección virtual.
        
        Traduce la dirección virtual a física, maneja page faults si es necesario,
        y retorna el valor del byte.
        
        Args:
            vaddr: Dirección virtual (0 a VIRTUAL_PAGES*PAGE_SIZE-1)
            
        Returns:
            Valor del byte (0-255)
            
        Raises:
            ValueError: Si vaddr está fuera de rango
        """
        # Validar dirección virtual
        max_vaddr = VIRTUAL_PAGES * PAGE_SIZE
        if not (0 <= vaddr < max_vaddr):
            raise ValueError(f"Dirección virtual {vaddr} fuera de rango [0, {max_vaddr-1}]")
        
        # PASO 1: Traducción de dirección virtual a (página, offset)
        page_no = vaddr // PAGE_SIZE    # Número de página virtual
        offset = vaddr % PAGE_SIZE       # Offset dentro de la página
        
        print(f"\n🔍 READ: vaddr={vaddr} → página={page_no}, offset={offset}")
        
        # PASO 2: Asegurar que la página esté en RAM (puede causar page fault)
        self._ensure_in_ram(page_no)
        
        # PASO 3: Obtener el marco físico donde está la página
        entry = self.page_table.get_entry(page_no)
        frame_no = entry.frame
        
        # PASO 4: Leer el byte de la memoria física
        byte_value = self.physical_memory.frames[frame_no][offset]
        
        print(f"   ✓ Leído valor {byte_value} del marco {frame_no}[{offset}]")
        return byte_value
    
    def write_byte(self, vaddr: int, value: int) -> None:
        """
        Escribe un byte a una dirección virtual.
        
        Traduce la dirección virtual a física, maneja page faults si es necesario,
        marca la página como sucia (dirty), y escribe el valor.
        
        Args:
            vaddr: Dirección virtual (0 a VIRTUAL_PAGES*PAGE_SIZE-1)
            value: Valor a escribir (0-255)
            
        Raises:
            ValueError: Si vaddr o value están fuera de rango
        """
        # Validar dirección virtual
        max_vaddr = VIRTUAL_PAGES * PAGE_SIZE
        if not (0 <= vaddr < max_vaddr):
            raise ValueError(f"Dirección virtual {vaddr} fuera de rango [0, {max_vaddr-1}]")
        
        # Validar valor de byte
        if not (0 <= value <= 255):
            raise ValueError(f"Valor {value} fuera de rango [0, 255]")
        
        # PASO 1: Traducción de dirección
        page_no = vaddr // PAGE_SIZE
        offset = vaddr % PAGE_SIZE
        
        print(f"\n✍️  WRITE: vaddr={vaddr} → página={page_no}, offset={offset}, value={value}")
        
        # PASO 2: Asegurar página en RAM
        self._ensure_in_ram(page_no)
        
        # PASO 3: Obtener marco físico
        entry = self.page_table.get_entry(page_no)
        frame_no = entry.frame
        
        # PASO 4: Marcar página como SUCIA antes de escribir
        # Esto es CRÍTICO - indica que la página fue modificada
        entry.dirty = True
        
        # PASO 5: Escribir el byte a memoria física
        self.physical_memory.frames[frame_no][offset] = value
        
        print(f"   ✓ Escrito valor {value} al marco {frame_no}[{offset}] (página marcada sucia)")
    
    def zero_page(self, page_no: int) -> None:
        """
        Llena una página completa con ceros.
        
        Útil para inicializar memoria, limpiar datos sensibles, o implementar
        copy-on-write.
        
        Args:
            page_no: Número de página virtual a llenar con ceros
            
        Raises:
            ValueError: Si page_no está fuera de rango
        """
        # Validar número de página
        if not (0 <= page_no < VIRTUAL_PAGES):
            raise ValueError(f"Página {page_no} fuera de rango [0, {VIRTUAL_PAGES-1}]")
        
        print(f"\n🧹 ZERO_PAGE: Llenando página {page_no} con ceros")
        
        # Asegurar página en RAM
        self._ensure_in_ram(page_no)
        
        # Obtener marco físico
        entry = self.page_table.get_entry(page_no)
        frame_no = entry.frame
        
        # Marcar como sucia (estamos modificando la página)
        entry.dirty = True
        
        # Llenar con ceros - reemplazar bytearray completo
        self.physical_memory.frames[frame_no] = bytearray(PAGE_SIZE)
        
        print(f"   ✓ Página {page_no} (marco {frame_no}) llena con ceros")
    
    def get_stats(self) -> Dict[str, any]:
        """
        Obtiene estadísticas del simulador.
        
        Returns:
            Diccionario con estadísticas de rendimiento y estado
        """
        dirty_pages = sum(
            1 for page_no in range(VIRTUAL_PAGES)
            if self.page_table.get_entry(page_no).dirty
        )
        
        pages_in_ram = sum(
            1 for page_no in range(VIRTUAL_PAGES)
            if self.page_table.get_entry(page_no).present
        )
        
        return {
            'page_faults': self.page_faults,
            'write_backs': self.write_backs,
            'pages_in_ram': pages_in_ram,
            'dirty_pages': dirty_pages,
            'free_frames': len(self.physical_memory.free_frames),
            'fifo_queue': list(self.fifo_queue)
        }
    
    def __repr__(self) -> str:
        """Representación legible del estado de la VM."""
        stats = self.get_stats()
        return (
            f"VM(faults={stats['page_faults']}, "
            f"writebacks={stats['write_backs']}, "
            f"ram={stats['pages_in_ram']}/{VIRTUAL_PAGES}, "
            f"dirty={stats['dirty_pages']})"
        )
