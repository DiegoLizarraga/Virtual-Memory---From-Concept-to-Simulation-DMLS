# Procesos y Round-Robin Scheduling: Del Concepto a la Simulación Python
## Investigación Teórica Completa - Lab 2

---

## 1. Program vs Process vs Thread

### Program (Programa)

Un **programa** es una entidad pasiva: un archivo ejecutable almacenado en disco que contiene instrucciones de máquina. Es simplemente código y datos estáticos.

**Características:**
- Existe como archivo en disco (ej: `/bin/ls`, `notepad.exe`)
- No consume recursos de sistema cuando no está ejecutándose
- Múltiples procesos pueden ejecutar el mismo programa simultáneamente
- Es una receta, no la comida

**Analogía:** Un programa es como una receta de cocina escrita en un libro.

### Process (Proceso)

Un **proceso** es un programa en ejecución: es la instancia activa de un programa con su propio estado, recursos asignados y espacio de direcciones.

**Características:**
- Entidad activa que consume recursos (CPU, memoria, I/O)
- Tiene su propio espacio de direcciones virtual aislado
- Posee identificador único (PID - Process ID)
- Mantiene estado: registros de CPU, contador de programa, stack, heap
- Es independiente de otros procesos
- La unidad de asignación de recursos del SO

**Analogía:** Un proceso es como cocinar activamente la receta: tienes ingredientes (memoria), estás usando utensilios (recursos), y estás en cierto paso (contador de programa).

### Thread (Hilo)

Un **thread** es una unidad de ejecución dentro de un proceso. Un proceso puede tener múltiples threads que comparten el mismo espacio de direcciones.

**Características:**
- Unidad más liviana que un proceso (lightweight process)
- Comparten memoria del proceso (heap, datos, código)
- Cada thread tiene su propio stack y registros
- Cambio de contexto más rápido que entre procesos
- Comunicación más fácil (memoria compartida) pero requiere sincronización

**Analogía:** Threads son como múltiples cocineros trabajando en la misma receta, compartiendo ingredientes pero cada uno con sus propias herramientas.

### Comparación:

| Aspecto | Program | Process | Thread |
|---------|---------|---------|--------|
| Naturaleza | Pasivo (código) | Activo (ejecutándose) | Activo (sub-ejecución) |
| Memoria | Archivo en disco | Espacio propio | Comparte con proceso |
| Recursos | Ninguno | Propios (PID, VM, files) | Comparte recursos del proceso |
| Aislamiento | N/A | Completo | Parcial |
| Overhead creación | N/A | Alto | Bajo |
| Comunicación | N/A | IPC (costoso) | Memoria compartida (rápido) |

---

## 2. Process Control Block (PCB)

### Definición

El **Process Control Block (PCB)**, también conocido como **Task Control Block (TCB)**, es la representación del sistema operativo de un proceso. Es una estructura de datos que contiene toda la información necesaria para gestionar un proceso.

### Propósito del PCB

El PCB es fundamental porque:
1. Permite al SO mantener múltiples procesos en memoria simultáneamente
2. Facilita la multiprogramación y el multitasking
3. Preserva el estado del proceso durante context switches
4. Provee aislamiento y protección entre procesos

### Campos Típicos del PCB

#### 1. **Process Identification (Identificación)**
- **PID (Process ID)**: Identificador único del proceso
- **PPID (Parent Process ID)**: PID del proceso padre
- **User ID / Group ID**: Propietario del proceso

#### 2. **Process State (Estado)**
- Estado actual: NEW, READY, RUNNING, WAITING, TERMINATED
- Información de scheduling (prioridad, quantum restante)

#### 3. **CPU Context (Contexto de CPU)**
- **Program Counter (PC)**: Dirección de la siguiente instrucción
- **Registros de CPU**: Valores de todos los registros generales
- **Stack Pointer (SP)**: Apunta al tope del stack
- **Status Registers**: Flags de condición (carry, zero, etc.)

Este contexto debe guardarse durante un **context switch** y restaurarse cuando el proceso vuelve a ejecutar.

#### 4. **Memory Management (Gestión de Memoria)**
- **Base and Limit Registers**: Para protección de memoria simple
- **Page Table Pointer**: Apunta a la tabla de páginas del proceso
- **Segment Table Pointer**: En sistemas con segmentación
- **Text/Data/BSS/Heap/Stack pointers**: Límites de secciones

#### 5. **I/O Status (Estado de I/O)**
- Lista de archivos abiertos (File Descriptors)
- Lista de dispositivos asignados
- Información de I/O pendiente

#### 6. **Accounting Information (Contabilidad)**
- Tiempo total de CPU usado
- Tiempo de inicio del proceso
- Límites de tiempo y memoria

#### 7. **Pointers (Punteros)**
- Puntero al siguiente PCB en la ready queue
- Puntero al proceso padre
- Punteros a procesos hijos

### Ubicación del PCB

Los PCBs típicamente residen en:
- **Kernel memory**: Protegida del espacio de usuario
- **Process table**: Arreglo o lista enlazada de PCBs
- **Por proceso**: Un PCB por cada proceso en el sistema

### Operaciones con PCB

El sistema operativo manipula PCBs durante:
1. **Process creation**: Inicializar nuevo PCB
2. **Context switch**: Guardar/restaurar contexto de CPU
3. **Scheduling**: Seleccionar proceso usando información del PCB
4. **Termination**: Liberar recursos y remover PCB

---

## 3. Process States y Transiciones de Estado

### Estados de un Proceso

Un proceso pasa por varios estados durante su ciclo de vida. El **modelo de 5 estados** es el más común:

#### 1. **NEW (Nuevo)**
- Proceso está siendo creado
- PCB está siendo inicializado
- Recursos aún no asignados completamente
- No listo para ejecutar

#### 2. **READY (Listo)**
- Proceso está listo para ejecutar
- Esperando ser asignado a CPU
- Tiene todos los recursos excepto CPU
- Reside en la **ready queue**

#### 3. **RUNNING (Ejecutando)**
- Proceso actualmente ejecutándose en CPU
- Solo un proceso por CPU core puede estar RUNNING
- Ejecuta instrucciones activamente

#### 4. **WAITING/BLOCKED (Esperando)**
- Proceso no puede continuar hasta que ocurra un evento
- Típicamente esperando I/O o señal
- Aunque CPU esté disponible, no puede ejecutar
- Reside en una **wait queue** específica del evento

#### 5. **TERMINATED/EXIT (Terminado)**
- Proceso ha finalizado su ejecución
- Recursos están siendo liberados
- PCB será removido (después de que padre lea exit status)

### Diagrama de Transiciones de Estado

```
                    +-------+
                    |  NEW  |
                    +-------+
                        |
                        | admit (SO asigna recursos)
                        v
    +-------------+ +-------+ dispatch (scheduler) +---------+
    |   WAITING   | | READY |<---------------------|         |
    | (BLOCKED)   | +-------+                      |         |
    +-------------+     ^                          | RUNNING |
          |             |                          |         |
          |             | interrupt/timeout        |         |
          |             | (quantum expired)        +---------+
          |             |                              |
          |             +------------------------------+
          |                                            |
          | event occurs (I/O complete)                | exit
          v                                            v
    +-------------+                               +-----------+
    | event wait  |                               |TERMINATED |
    | (I/O request)                               +-----------+
    +-------------+
```

### Transiciones Detalladas

1. **NEW → READY (Admission)**
   - SO termina de crear el proceso
   - Recursos asignados (memoria, PCB)
   - Proceso insertado en ready queue

2. **READY → RUNNING (Dispatch)**
   - Scheduler selecciona el proceso
   - Context switch realizado
   - CPU asignada al proceso

3. **RUNNING → READY (Interrupt/Timeout)**
   - Time quantum expira (en scheduling preemptive)
   - Proceso de mayor prioridad llega
   - Proceso voluntariamente cede CPU
   - Proceso va al final de ready queue

4. **RUNNING → WAITING (Event Wait)**
   - Proceso solicita I/O
   - Proceso espera recurso no disponible
   - Proceso espera señal o semáforo
   - Mueve a wait queue específica

5. **WAITING → READY (Event Occurs)**
   - I/O completa
   - Recurso disponible
   - Señal recibida
   - Proceso va a ready queue

6. **RUNNING → TERMINATED (Exit)**
   - Proceso completa su ejecución (return o exit)
   - Proceso es terminado forzosamente (killed)
   - Error fatal ocurre
   - Recursos liberados, PCB eventualmente removido

### Estados Adicionales en Sistemas Reales

Sistemas operativos modernos pueden tener estados adicionales:

- **SUSPENDED READY**: Proceso swapped out del disco pero listo para ejecutar
- **SUSPENDED WAITING**: Proceso swapped out esperando evento
- **ZOMBIE**: Proceso terminado pero PCB aún existe (esperando parent's wait())

---

## 4. CPU Scheduling: Conceptos Básicos

### ¿Qué es CPU Scheduling?

**CPU Scheduling** es el método por el cual el sistema operativo decide qué proceso de la ready queue obtiene la CPU. Es el mecanismo fundamental para multitasking.

### Objetivos del Scheduling

Los schedulers buscan optimizar múltiples métricas conflictivas:

#### 1. **CPU Utilization (Utilización de CPU)**
- Mantener la CPU tan ocupada como sea posible
- Métrica: porcentaje de tiempo que CPU está ejecutando procesos
- Objetivo: 40-90% en sistemas reales

#### 2. **Throughput (Rendimiento)**
- Número de procesos completados por unidad de tiempo
- Métrica: procesos/segundo
- Objetivo: Maximizar

#### 3. **Turnaround Time (Tiempo de Retorno)**
- Tiempo total desde envío hasta completación
- Incluye: tiempo en ready, ejecutando, esperando I/O
- Métrica: tiempo_completación - tiempo_llegada
- Objetivo: Minimizar (promedio)

#### 4. **Waiting Time (Tiempo de Espera)**
- Tiempo total que proceso pasa en ready queue
- NO incluye tiempo de ejecución o I/O
- Métrica: sum(tiempos en ready queue)
- Objetivo: Minimizar (promedio)

#### 5. **Response Time (Tiempo de Respuesta)**
- Tiempo desde envío hasta primera respuesta (no completación)
- Crucial para sistemas interactivos
- Métrica: tiempo_primera_ejecución - tiempo_llegada
- Objetivo: Minimizar

#### 6. **Fairness (Justicia)**
- Cada proceso debe recibir "su parte justa" de CPU
- Evitar **starvation**: proceso espera indefinidamente
- Balance entre justicia y rendimiento

### Trade-offs en Scheduling

Es imposible optimizar todas las métricas simultáneamente:
- **Throughput vs Response Time**: Maximizar throughput favorece procesos largos; minimizar response time favorece procesos cortos
- **Fairness vs Efficiency**: Dar a todos tiempo igual puede ser ineficiente
- **CPU Utilization vs Latency**: Alta utilización puede aumentar latencia

### Tipos de Scheduling

#### Preemptive (Con Desalojo)
- SO puede interrumpir proceso en ejecución
- Requiere interrupciones de timer
- Más complejo pero más responsive
- Ejemplos: Round-Robin, Priority Scheduling con preemption

#### Non-Preemptive (Sin Desalojo)
- Proceso ejecuta hasta que voluntariamente cede CPU o termina
- Más simple de implementar
- Puede causar problemas con procesos largos
- Ejemplos: FCFS, SJF sin preemption

---

## 5. Round-Robin (RR) Scheduling

### Concepto

**Round-Robin (RR)** es un algoritmo de scheduling preemptive diseñado específicamente para time-sharing systems. Es uno de los algoritmos más simples y justos.

### Componentes Clave

#### 1. **Ready Queue (Cola de Listos)**
- Cola FIFO (First-In-First-Out) de procesos READY
- Implementada típicamente como cola circular
- Cada proceso espera su turno

#### 2. **Time Quantum/Time Slice**
- Período fijo de tiempo asignado a cada proceso
- También llamado **scheduling quantum**
- Típicamente 10-100 ms en sistemas reales
- Crucial para el comportamiento del scheduler

#### 3. **Context Switch**
- Cambio de un proceso a otro
- Implica:
  1. Guardar contexto del proceso saliente (en su PCB)
  2. Cargar contexto del proceso entrante (de su PCB)
  3. Actualizar estructuras del SO
- Tiene overhead (tiempo perdido)

### Algoritmo Round-Robin

```
ALGORITMO: Round-Robin Scheduling

Inicialización:
  ready_queue ← cola vacía
  quantum ← tiempo fijo (ej: 10ms)

En cada timer interrupt (cada quantum):
  IF proceso actual no ha terminado THEN
    guardar contexto en PCB
    mover proceso al final de ready_queue
  END IF
  
  proceso ← sacar primero de ready_queue
  
  IF proceso ≠ NULL THEN
    cargar contexto del proceso desde PCB
    marcar proceso como RUNNING
    configurar timer para quantum
    ejecutar proceso
  ELSE
    CPU idle
  END IF
```

### Características de Round-Robin

#### Ventajas:
1. **Simplicidad**: Fácil de implementar y entender
2. **Fairness**: Cada proceso recibe tiempo igual de CPU
3. **No starvation**: Todos los procesos eventualmente ejecutan
4. **Buen response time**: Procesos no esperan mucho para primera ejecución
5. **Predecible**: Tiempo de espera es proporcional a cantidad de procesos

#### Desventajas:
1. **Overhead de context switch**: Switches frecuentes si quantum pequeño
2. **No optimal turnaround time**: Puede ser peor que otros algoritmos para ciertos workloads
3. **Todos igual prioridad**: No diferencia procesos importantes
4. **Performance variable**: Depende críticamente de la elección del quantum

### Elección del Time Quantum

El quantum debe balancear:

#### Quantum Pequeño (ej: 1-5ms):
- **Ventaja**: Excelente response time, más "responsive"
- **Desventaja**: Alto overhead de context switches
- Si quantum → 0, overhead → 100%

#### Quantum Grande (ej: 100ms-1s):
- **Ventaja**: Bajo overhead de context switches
- **Desventaja**: Se comporta como FCFS, peor response time

#### Regla Práctica:
- **Quantum óptimo**: 80% de CPU bursts deben ser más cortos que el quantum
- En sistemas reales: 10-100ms
- En nuestra simulación: 1 "step" por quantum (abstracto)

### Ejemplo de Ejecución

```
Procesos: P1 (duración 24), P2 (3), P3 (3)
Quantum: 4

Tiempo: 0  4  7  10 14 18 22 26 30
        |  |  |  |  |  |  |  |  |
CPU:    P1 P2 P3 P1 P1 P1 P1 P1 P1
        
Ready Queue evolución:
t=0:  [P1, P2, P3]
t=4:  [P2, P3, P1]  (P1 usó su quantum)
t=7:  [P3, P1]      (P2 terminó)
t=10: [P1]          (P3 terminó)
...

Waiting times:
P1: (30-24) = 6 (tiempo en ready)
P2: (7-3) = 4
P3: (10-3) = 7
Average: (6+4+7)/3 = 5.67
```

---

## 6. Memoria Virtual por Proceso

### ¿Por Qué Cada Proceso Necesita Su Propia VM?

#### 1. **Aislamiento (Isolation)**
- Proceso A no puede acceder memoria de Proceso B
- Previene errores de un proceso afectar otros
- Seguridad: proceso malicioso no puede leer/modificar otros

#### 2. **Abstracción (Abstraction)**
- Cada proceso ve su propio espacio de direcciones "limpio"
- Siempre comienza en dirección 0
- No necesita saber dónde está físicamente en RAM
- Simplifica programación

#### 3. **Protección (Protection)**
- SO puede marcar páginas como read-only, execute-only, etc.
- Previene código modificar sus propias instrucciones accidentalmente
- Implementa principio de least privilege

#### 4. **Flexibilidad (Flexibility)**
- Procesos pueden tener tamaños diferentes
- Memoria no necesita ser contigua físicamente
- Permite overcommitment (procesos usan más memoria que RAM total)

### Implementación: Page Table por Proceso

Cada proceso tiene su propia **page table** que mapea sus páginas virtuales a marcos físicos:

```
Proceso A:
  Page Table A:
    Page 0 → Frame 3
    Page 1 → Frame 7
    Page 2 → Frame 1

Proceso B:
  Page Table B:
    Page 0 → Frame 2  (diferente frame que A!)
    Page 1 → Frame 5
    Page 2 → Frame 9
```

### Context Switch y Memoria Virtual

Durante un context switch, el SO debe:
1. Guardar puntero a page table del proceso saliente
2. Cargar puntero a page table del proceso entrante
3. Flush TLB (Translation Lookaside Buffer)

En arquitectura x86, el registro **CR3** contiene la dirección física de la page table del proceso actual.

### Compartir Memoria Entre Procesos

Aunque cada proceso tiene su VM propia, pueden compartir memoria cuando sea necesario:

#### Shared Memory:
- Múltiples page tables mapean a mismo frame físico
- Usado para: bibliotecas compartidas, IPC

#### Copy-on-Write (COW):
- Al hacer fork(), padre e hijo comparten páginas (marcadas read-only)
- Si uno intenta escribir, se crea copia privada
- Optimización: evita copiar memoria innecesariamente

---

## 7. Cómo el SO Usa PCB + Scheduler + VM

### Integración de Componentes

#### Creación de Proceso:

```
spawn(programa):
  1. Asignar nuevo PID
  2. Crear PCB:
     - Inicializar pid, state=NEW
     - Crear nueva page table (VM propia)
     - Apuntar program counter al inicio del programa
     - Inicializar registros
  3. Asignar recursos (archivos, memoria inicial)
  4. Insertar PCB en process table
  5. Cambiar state a READY
  6. Agregar a ready queue del scheduler
```

#### Ejecución (Dispatch):

```
dispatch():
  1. Scheduler selecciona proceso de ready queue
  2. Context switch:
     a. Guardar contexto de proceso anterior en su PCB
     b. Cargar contexto de nuevo proceso desde su PCB
     c. Cambiar page table (cargar CR3 con page table del proceso)
     d. Flush TLB
  3. Cambiar state del proceso a RUNNING
  4. Configurar timer interrupt para quantum
  5. Transferir control a proceso (jump a PC)
```

#### Durante Ejecución:

```
Proceso ejecutando:
  - Accede memoria → MMU usa page table del proceso para traducir
  - Page fault? → SO maneja:
    * Guarda contexto en PCB
    * Cambia state a WAITING
    * Inicia carga de página desde disco
    * Selecciona otro proceso para ejecutar
    * Cuando página lista, proceso vuelve a READY
```

#### Timer Interrupt (Quantum Expira):

```
timer_interrupt():
  1. Guardar contexto de proceso actual en su PCB
  2. Cambiar state de RUNNING a READY
  3. Agregar proceso al final de ready queue
  4. Llamar dispatch() para seleccionar siguiente proceso
```

### Flujo Completo de Ejemplo

```
Estado Inicial:
  Ready Queue: [P1, P2, P3]
  Running: ninguno

Ciclo 1 (dispatch):
  - Scheduler selecciona P1
  - P1.state = RUNNING
  - Cargar page table de P1
  - Ejecutar P1 por quantum
  - Timer interrupt:
    * P1.state = READY
    * Ready Queue: [P2, P3, P1]

Ciclo 2 (dispatch):
  - Scheduler selecciona P2
  - P2.state = RUNNING
  - Cargar page table de P2
  - P2 accede memoria → MMU traduce usando page table de P2
  - P2 solicita I/O → P2.state = WAITING
  - Ready Queue: [P3, P1]
  - Wait Queue: [P2]

Ciclo 3 (dispatch):
  - Scheduler selecciona P3
  - P3.state = RUNNING
  - Cargar page table de P3
  - P3 ejecuta y termina
  - P3.state = TERMINATED
  - Ready Queue: [P1]

Ciclo 4:
  - I/O de P2 completa
  - P2.state = READY
  - Ready Queue: [P1, P2]
  - Continúa...
```

---

## 8. Mapeo a Simulación Python

### Estructuras de Datos Python

```python
# Enum de estados
class State(Enum):
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"

# Process Control Block
@dataclass
class PCB:
    pid: int                    # Process ID único
    state: State = State.NEW    # Estado actual
    vm: VM = field(default_factory=VM)  # VM propia
    prog: Callable = None       # Programa a ejecutar
    cpu_time: int = 0           # Tiempo de CPU usado
    
    # En sistema real: registros de CPU, PC, stack pointer, etc.

# Scheduler Round-Robin
class Scheduler:
    def __init__(self):
        self.ready_queue = deque()  # Cola FIFO
    
    def add(self, pcb: PCB):
        if pcb.state == State.READY:
            self.ready_queue.append(pcb)
    
    def next(self) -> Optional[PCB]:
        return self.ready_queue.popleft() if self.ready_queue else None

# Kernel
class Kernel:
    def __init__(self):
        self.procs = {}             # process table: pid → PCB
        self.sched = Scheduler()
        self.running = None
        self.next_pid = 1
    
    def spawn(self, prog, name=""):
        # Crear proceso con VM propia
        pcb = PCB(pid=self.next_pid, prog=prog, name=name)
        self.next_pid += 1
        self.procs[pcb.pid] = pcb
        pcb.state = State.READY
        self.sched.add(pcb)
        return pcb.pid
    
    def dispatch(self):
        # Reencolar proceso anterior si aún RUNNING
        if self.running and self.running.state == State.RUNNING:
            self.running.state = State.READY
            self.sched.add(self.running)
        
        # Obtener siguiente proceso
        pcb = self.sched.next()
        if not pcb:
            self.running = None
            return  # CPU idle
        
        # Context switch (simulado)
        self.running = pcb
        pcb.state = State.RUNNING
        
        # Ejecutar un "time slice" del programa
        pcb.prog(self, pcb)  # Programa puede cambiar pcb.state
        pcb.cpu_time += 1
```

### Simulación de Programas

Cada programa es una función que ejecuta "un paso":

```python
def touch_pages_prog(kernel, pcb):
    """Programa que escribe en su VM."""
    
    # Inicializar estado si no existe
    if not hasattr(pcb, '_counter'):
        pcb._counter = 0
    
    # Verificar si terminamos
    if pcb._counter >= 5:
        pcb.state = State.TERMINATED
        return
    
    # Hacer trabajo: escribir en VM propia
    vaddr = pcb._counter * PAGE_SIZE
    pcb.vm.write_byte(vaddr, pcb.pid)
    
    # Avanzar
    pcb._counter += 1
```

### Ejecución del Sistema

```python
# Crear kernel
kernel = Kernel()

# Crear procesos
pid1 = kernel.spawn(touch_pages_prog, "Process-A")
pid2 = kernel.spawn(touch_pages_prog, "Process-B")

# Ejecutar time slices
for step in range(20):
    print(f"\n=== Step {step} ===")
    kernel.dispatch()
    print(f"ps: {kernel.ps()}")

# Resultado esperado:
# Los procesos alternan ejecución (Round-Robin)
# Cada uno escribe en su propia VM
# Terminan cuando completan su trabajo
```

### Diferencias con Sistema Real

Nuestra simulación simplifica:
1. **Time slice**: Es "un paso" abstracto, no tiempo real
2. **Context switch**: No guardamos/cargamos registros reales
3. **Page table switch**: No cambiamos CR3, cada PCB ya tiene su VM objeto
4. **Interrupts**: No usamos interrupciones hardware, dispatch() es manual
5. **I/O**: No simulamos dispositivos reales, WAITING es opcional
6. **Concurrencia**: Ejecución es secuencial, no paralela

Pero los **conceptos** son idénticos:
- PCB contiene todo el estado
- Scheduler usa Round-Robin
- Cada proceso tiene VM propia
- Context switch entre procesos
- Estados y transiciones de estado

---

## Referencias

1. **Silberschatz, A., Galvin, P. B., & Gagne, G.** (2018). *Operating System Concepts* (10th ed.). Wiley.
   - Capítulo 3: Processes
   - Capítulo 5: CPU Scheduling

2. **Tanenbaum, A. S., & Bos, H.** (2014). *Modern Operating Systems* (4th ed.). Pearson.
   - Capítulo 2: Processes and Threads
   - Capítulo 6: Scheduling

3. **Arpaci-Dusseau, R. H., & Arpaci-Dusseau, A. C.** (2018). *Operating Systems: Three Easy Pieces*.
   - Capítulo 4: The Abstraction: The Process
   - Capítulo 7: Scheduling: Introduction
   - Capítulo 8: Scheduling: MLFQ
   - Disponible online: https://pages.cs.wisc.edu/~remzi/OSTEP/

4. **Stallings, W.** (2017). *Operating Systems: Internals and Design Principles* (9th ed.). Pearson.

5. **Love, R.** (2010). *Linux Kernel Development* (3rd ed.). Addison-Wesley.
   - Capítulo 3: Process Management
   - Capítulo 4: Process Scheduling

---

## Conclusión

Este documento ha cubierto los conceptos fundamentales de procesos y scheduling necesarios para implementar un simulador realista:

- **Procesos** son programas en ejecución con estado y recursos propios
- **PCB** es la representación del SO de un proceso, conteniendo todo su contexto
- **Estados de proceso** y sus transiciones modelan el ciclo de vida
- **CPU Scheduling** decide qué proceso ejecuta, optimizando múltiples métricas
- **Round-Robin** es un algoritmo simple, justo y preemptive basado en quantums
- **Memoria virtual por proceso** provee aislamiento, abstracción y protección
- La **integración** de PCB, Scheduler y VM permite ejecución segura de múltiples procesos

La simulación Python captura la esencia de estos conceptos, permitiendo experimentar con scheduling, context switches y aislamiento de memoria sin la complejidad de un sistema operativo real.