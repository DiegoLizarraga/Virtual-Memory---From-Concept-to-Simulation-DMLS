# Prompts LLM y Respuestas GPT
## Laboratorio de Memoria Virtual

---

## PROMPT 1: Estructuras de Datos

### Prompt Inicial:
```
Necesito diseñar las estructuras de datos fundamentales para un simulador de memoria 
virtual en Python. Específicamente necesito:

1. PTEntry: Una clase que represente una entrada de tabla de páginas con los campos:
   - frame: número de marco físico
   - present: bit que indica si la página está en RAM
   - dirty: bit que indica si la página fue modificada

2. PageTable: Una clase para la tabla de páginas que mapee números de página 
   virtual a objetos PTEntry

3. PhysicalMemory: Una clase que represente la RAM con:
   - Un mapeo de frame → bytearray para almacenar datos
   - Una lista de marcos libres disponibles

Constantes a usar:
- PAGE_SIZE = 256
- VIRTUAL_PAGES = 16
- PHYSICAL_FRAMES = 8

Por favor, proporciona:
- Implementación usando dataclasses de Python
- Explicación detallada de por qué existe cada clase
- Justificación de cada campo/elemento en las clases
```

### Prompt Refinado (Final):
```
Crea estructuras de datos para simulador de memoria virtual en Python usando dataclasses.

Requisitos específicos:
1. PTEntry (dataclass):
   - frame: Optional[int] - número de marco físico (None si no está en RAM)
   - present: bool = False - indica si página está cargada en memoria
   - dirty: bool = False - indica si página fue modificada desde que se cargó

2. PageTable (clase normal):
   - Diccionario interno: int → PTEntry
   - Método get_entry(page_no) que devuelve PTEntry o None
   - Método set_entry(page_no, entry) para actualizar entrada

3. PhysicalMemory (clase):
   - frames: Dict[int, bytearray] - mapeo frame_no → datos
   - free_frames: List[int] - marcos disponibles (inicialmente [0,1,2,...,7])
   - Método allocate_frame() → int - retorna número de marco libre
   - Método free_frame(frame_no) - marca marco como libre

Constantes:
PAGE_SIZE = 256
VIRTUAL_PAGES = 16  
PHYSICAL_FRAMES = 8

Incluye:
- Type hints completos
- Inicialización apropiada
- Docstrings explicando el propósito de cada clase
- Comentarios sobre por qué cada campo es necesario
```

### Respuesta GPT:

```python
from dataclasses import dataclass
from typing import Dict, List, Optional

# Constantes del sistema
PAGE_SIZE = 256        # Bytes por página/marco
VIRTUAL_PAGES = 16     # Número de páginas virtuales
PHYSICAL_FRAMES = 8    # Número de marcos físicos en RAM

@dataclass
class PTEntry:
    """
    Entrada de Tabla de Páginas (Page Table Entry).
    
    Representa el mapeo de una página virtual a un marco físico,
    junto con bits de control que indican el estado de la página.
    
    Campos:
    - frame: Número de marco físico donde reside la página (None si no está en RAM)
    - present: Bit de validez - True si la página está actualmente en memoria física
    - dirty: Bit sucio - True si la página fue modificada (necesita write-back)
    """
    frame: Optional[int] = None
    present: bool = False
    dirty: bool = False


class PageTable:
    """
    Tabla de Páginas del proceso.
    
    Mapea números de página virtual (0 a VIRTUAL_PAGES-1) a entradas PTEntry.
    Cada proceso tiene su propia tabla de páginas que el SO usa para 
    traducir direcciones virtuales a físicas.
    
    Por qué existe:
    - Permite traducción de direcciones virtuales a físicas
    - Mantiene estado de cada página (presente, sucia)
    - Habilita paginación bajo demanda (lazy loading)
    """
    
    def __init__(self):
        """Inicializa tabla vacía para VIRTUAL_PAGES páginas."""
        self._entries: Dict[int, PTEntry] = {}
        # Crear entradas para todas las páginas virtuales
        for page_no in range(VIRTUAL_PAGES):
            self._entries[page_no] = PTEntry()
    
    def get_entry(self, page_no: int) -> PTEntry:
        """Obtiene entrada de tabla de páginas para una página virtual."""
        if page_no not in self._entries:
            raise ValueError(f"Página {page_no} fuera de rango")
        return self._entries[page_no]
    
    def set_entry(self, page_no: int, entry: PTEntry) -> None:
        """Actualiza entrada de tabla de páginas."""
        if page_no not in self._entries:
            raise ValueError(f"Página {page_no} fuera de rango")
        self._entries[page_no] = entry


class PhysicalMemory:
    """
    Memoria Física (RAM simulada).
    
    Gestiona marcos de memoria física donde se cargan las páginas.
    Mantiene tanto los datos como la lista de marcos disponibles.
    
    Por qué existe:
    - Simula la RAM física limitada del sistema
    - Gestiona asignación/liberación de marcos
    - Almacena los datos reales de las páginas
    
    Campos:
    - frames: Mapeo de número de marco a bytearray con PAGE_SIZE bytes
    - free_frames: Lista de números de marco disponibles para asignar
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
        Asigna un marco libre.
        
        Returns:
            Número de marco asignado, o None si no hay marcos libres
        """
        if not self.free_frames:
            return None  # Sin marcos disponibles
        return self.free_frames.pop(0)  # FIFO: toma el primero
    
    def free_frame(self, frame_no: int) -> None:
        """
        Libera un marco para reutilización.
        
        Args:
            frame_no: Número de marco a liberar
        """
        if frame_no not in self.frames:
            raise ValueError(f"Marco {frame_no} inválido")
        if frame_no in self.free_frames:
            raise ValueError(f"Marco {frame_no} ya está libre")
        
        # Limpiar datos del marco
        self.frames[frame_no] = bytearray(PAGE_SIZE)
        # Marcar como disponible
        self.free_frames.append(frame_no)
```

**Explicación de diseño:**

1. **PTEntry**: Modela una entrada de tabla de páginas hardware. Cada campo corresponde a un bit de control real en sistemas x86:
   - `frame`: El PFN (Physical Frame Number) - esencial para traducción
   - `present`: Bit de validez - distingue entre páginas en RAM vs en disco
   - `dirty`: Bit de modificación - optimiza write-back (solo escribir si cambió)

2. **PageTable**: Abstracción del mapeo virtual→físico. Es un diccionario porque:
   - Acceso O(1) por número de página
   - Cada proceso necesita su propia tabla
   - Permite páginas dispersas (no todas las páginas deben estar asignadas)

3. **PhysicalMemory**: Simula la RAM limitada. Usa dos estructuras porque:
   - `frames`: Almacena datos reales (bytearray mutable para lecturas/escrituras)
   - `free_frames`: Administra asignación - crucial cuando RAM se llena
   - Separación permite buscar marcos disponibles en O(1)

---

## PROMPT 2: Page Fault + Reemplazo FIFO

### Prompt Inicial:
```
Necesito implementar el manejo de fallos de página con reemplazo FIFO para el 
simulador de memoria virtual.

Específicamente, necesito un método _ensure_in_ram(page_no) que:
- Verifique si una página está en RAM
- Si no está, la cargue (page fault)
- Si no hay marcos libres, desaloje una página usando FIFO
- Si la página desalojada está sucia, la escriba de vuelta al backing store

También necesito:
- Una cola FIFO para rastrear el orden de llegada de páginas
- Mapeo inverso: frame → page para saber qué página está en cada marco
- Lógica para escribir páginas sucias al disco

Proporciona la lógica paso a paso con explicaciones detalladas.
```

### Prompt Refinado (Final):
```
Implementa método _ensure_in_ram(page_no: int) para clase VM con manejo 
completo de page faults y reemplazo FIFO.

Contexto:
- La clase VM tiene: page_table (PageTable), physical_memory (PhysicalMemory)
- Necesita: backing_store (Dict[int, bytearray]) para páginas en disco
- Necesita: fifo_queue (List[int]) para orden de páginas en RAM
- Necesita: frame_to_page (Dict[int, int]) para mapeo inverso

Algoritmo paso a paso:

1. Verificar si page_no ya está en RAM:
   - Obtener entry = page_table.get_entry(page_no)
   - Si entry.present es True: return (ya está cargada)

2. PAGE FAULT - necesitamos cargar la página:
   a) Intentar asignar marco libre:
      - frame_no = physical_memory.allocate_frame()
   
   b) Si frame_no es None (sin marcos libres):
      - REEMPLAZO FIFO:
        * victim_page = fifo_queue.pop(0)  # La más antigua
        * victim_entry = page_table.get_entry(victim_page)
        * victim_frame = victim_entry.frame
        
        * Si victim_entry.dirty es True:
          - WRITE-BACK: backing_store[victim_page] = copy(frames[victim_frame])
        
        * Actualizar victim_entry: present=False, frame=None, dirty=False
        * Liberar: physical_memory.free_frame(victim_frame)
        * Reasignar: frame_no = physical_memory.allocate_frame()
   
   c) Cargar página del backing store:
      - Si page_no in backing_store:
          frames[frame_no] = copy(backing_store[page_no])
      - Sino:
          frames[frame_no] = bytearray(PAGE_SIZE)  # Página nueva (ceros)
   
   d) Actualizar estructuras:
      - entry.frame = frame_no
      - entry.present = True
      - entry.dirty = False  # Recién cargada, no modificada
      - fifo_queue.append(page_no)  # Agregar al final
      - frame_to_page[frame_no] = page_no

Incluye:
- Manejo de errores (page_no inválido)
- Comentarios explicando cada paso
- Print statements para debugging
```

### Respuesta GPT:

```python
def _ensure_in_ram(self, page_no: int) -> None:
    """
    Asegura que una página esté cargada en RAM, manejando page faults si es necesario.
    
    Este método implementa:
    - Detección de page faults
    - Carga de páginas desde backing store
    - Reemplazo FIFO cuando RAM está llena
    - Write-back de páginas sucias
    
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
```

**Explicación del algoritmo:**

1. **Verificación inicial**: Primero revisamos si la página ya está presente. Esto evita trabajo innecesario.

2. **Page Fault**: Cuando `present=False`, significa que la página está en disco o nunca fue inicializada. Esto es un fallo de página.

3. **Asignación de marco**: Intentamos obtener un marco libre. Si `allocate_frame()` retorna `None`, significa que RAM está completamente ocupada.

4. **Reemplazo FIFO**: 
   - `fifo_queue` mantiene orden de llegada (más antiguo al frente)
   - `pop(0)` obtiene la página más antigua (víctima)
   - Esto es O(n) pero simple - en producción se usaría deque

5. **Write-back condicional**: Solo escribimos la víctima al disco si `dirty=True`. Esto ahorra tiempo de E/S cuando la página no fue modificada.

6. **Mapeo inverso**: `frame_to_page` permite saber rápidamente qué página vive en cada marco. Útil para depuración y estadísticas.

7. **Actualización de estructuras**: Al final, actualizamos todos los metadatos para reflejar que la página ahora está en RAM.

---

## PROMPT 3: Read, Write, Zero Page

### Prompt Inicial:
```
Necesito implementar las operaciones de memoria fundamentales:

1. read_byte(vaddr) - leer un byte de una dirección virtual
2. write_byte(vaddr, value) - escribir un byte a una dirección virtual  
3. zero_page(page_no) - llenar una página con ceros

Cada método debe:
- Traducir dirección virtual a física
- Llamar a _ensure_in_ram() para manejar page faults
- Actualizar el bit dirty cuando corresponda

Proporciona explicación de cómo funciona la traducción de direcciones.
```

### Prompt Refinado (Final):
```
Implementa tres métodos de acceso a memoria para clase VM con traducción 
de direcciones y manejo de dirty bit.

MÉTODO 1: read_byte(vaddr: int) → int

1. Traducción de dirección:
   - page_no = vaddr // PAGE_SIZE       # División entera
   - offset = vaddr % PAGE_SIZE         # Módulo (resto)
   
2. Asegurar página en RAM:
   - self._ensure_in_ram(page_no)       # Maneja page fault si necesario
   
3. Obtener marco físico:
   - entry = page_table.get_entry(page_no)
   - frame_no = entry.frame
   
4. Leer dato:
   - byte_value = physical_memory.frames[frame_no][offset]
   - return byte_value

MÉTODO 2: write_byte(vaddr: int, value: int) → None

Similar a read_byte, pero:
1. Traducir vaddr → (page_no, offset)
2. _ensure_in_ram(page_no)
3. Obtener frame_no
4. **IMPORTANTE**: Marcar página como sucia ANTES de escribir:
   - entry.dirty = True
5. Escribir dato:
   - physical_memory.frames[frame_no][offset] = value

MÉTODO 3: zero_page(page_no: int) → None

Llenar una página completa con ceros:
1. Validar page_no
2. _ensure_in_ram(page_no)  # Cargar si es necesario
3. Obtener frame_no
4. Marcar dirty: entry.dirty = True
5. Llenar con ceros:
   - for i in range(PAGE_SIZE):
       physical_memory.frames[frame_no][i] = 0
   O más eficiente:
   - physical_memory.frames[frame_no] = bytearray(PAGE_SIZE)

Incluye:
- Type hints completos
- Validación de rangos (vaddr válida, value 0-255)
- Docstrings completos
- Comentarios explicando traducción de direcciones
```

### Respuesta GPT:

```python
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
    
    print(f"🔍 READ: vaddr={vaddr} → página={page_no}, offset={offset}")
    
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
    
    print(f"✍️  WRITE: vaddr={vaddr} → página={page_no}, offset={offset}, value={value}")
    
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
    
    print(f"🧹 ZERO_PAGE: Llenando página {page_no} con ceros")
    
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
```

**Explicación de la traducción de direcciones:**

Una dirección virtual es un número entero que el proceso usa para referenciar memoria. Internamente, se compone de dos partes:

```
Dirección Virtual: [    VPN    |    Offset    ]
                    (bits altos) (bits bajos)

Ejemplo con PAGE_SIZE = 256 (2^8):
- vaddr = 770
- VPN = 770 // 256 = 3        # Página 3
- Offset = 770 % 256 = 2       # Byte 2 dentro de la página

La página 3 podría estar en el marco físico 5:
Dirección Física: marco 5, offset 2
Ubicación real en RAM: frames[5][2]
```

**Por qué marcar dirty en escrituras:**

Cuando escribimos a una página, debemos marcar `dirty=True` porque:
1. La copia en RAM ahora difiere del backing store
2. Si la página es desalojada, debe escribirse de vuelta al disco
3. Si no marcamos dirty, los cambios se perderán
4. Es una optimización: páginas limpias no necesitan write-back

---

## PROMPT 4: Ensamble Final

### Prompt Inicial:
```
Necesito integrar todas las clases y métodos anteriores en un archivo vm.py completo.

Debe incluir:
- Las tres estructuras de datos (PTEntry, PageTable, PhysicalMemory)
- La clase VM principal con todos los métodos
- Método __init__ que inicialice todas las estructuras
- Los tres prompts anteriores integrados y funcionando juntos

El archivo debe ser limpio, bien documentado y listo para usar.
```

### Prompt Refinado (Final):
```
Crea un archivo vm.py completo y funcional integrando todos los componentes 
del simulador de memoria virtual.

Estructura completa de la clase VM:

```python
class VM:
    def __init__(self):
        # Inicializar tabla de páginas
        self.page_table = PageTable()
        
        # Inicializar memoria física
        self.physical_memory = PhysicalMemory()
        
        # Backing store - almacena páginas que no están en RAM
        self.backing_store: Dict[int, bytearray] = {}
        
        # Cola FIFO - rastrea orden de páginas en RAM
        self.fifo_queue: List[int] = []
        
        # Mapeo inverso frame → page
        self.frame_to_page: Dict[int, int] = {}
```

Métodos a incluir (ya implementados en prompts anteriores):
1. _ensure_in_ram(page_no) - del Prompt 2
2. read_byte(vaddr) - del Prompt 3
3. write_byte(vaddr, value) - del Prompt 3
4. zero_page(page_no) - del Prompt 3

Métodos adicionales útiles:
5. get_stats() - retorna estadísticas (page faults, dirty pages, etc.)
6. __repr__() - representación legible del estado de la VM

Requisitos:
- Todas las importaciones necesarias al inicio
- Constantes definidas correctamente
- Documentación completa de la clase VM
- Código probado y sin errores
- Comentarios explicando partes complejas
```

### Respuesta GPT:

Ver el siguiente artefacto (vm.py) para la implementación completa.

**Notas de integración:**

1. **Orden de definiciones**: Las clases deben definirse en orden (PTEntry, PageTable, PhysicalMemory, luego VM) para evitar errores de referencia.

2. **Inicialización coherente**: `__init__` de VM debe inicializar todas las estructuras en el orden correcto.

3. **Gestión de estado**: `fifo_queue` y `frame_to_page` deben mantenerse sincronizados con `page_table`.

4. **Manejo de errores**: Todos los métodos incluyen validación de entrada apropiada.

5. **Debugging**: Los print statements facilitan seguir el flujo de ejecución durante el desarrollo.

Esta integración asegura que:
- Los page faults se manejan correctamente
- El reemplazo FIFO funciona como se espera
- Las páginas sucias se escriben de vuelta al disco
- La traducción de direcciones es precisa