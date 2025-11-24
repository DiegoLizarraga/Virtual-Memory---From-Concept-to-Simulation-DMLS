# Prompts LLM y Respuestas - Lab 2: Procesos y Scheduling

## PROMPT 1: PCB y Estados de Proceso

### Prompt Inicial:
```
Necesito crear un módulo process.py con:
- Un enum State con estados NEW, READY, RUNNING, WAITING, TERMINATED
- Una dataclass PCB con campos pid, state, vm, prog
```

### Prompt Refinado (Final):
```
Diseña un módulo process.py para un sistema operativo simulado con las siguientes especificaciones:

1. Enum de Estados (State):
   - NEW: Proceso recién creado
   - READY: Listo para ejecutar, esperando CPU
   - RUNNING: Actualmente ejecutándose
   - WAITING: Bloqueado esperando I/O
   - TERMINATED: Proceso finalizado

2. Dataclass PCB (Process Control Block):
   Campos obligatorios:
   - pid: int - Identificador único del proceso
   - state: State - Estado actual (default State.NEW)
   - vm: VM - Objeto de memoria virtual del Lab 1
     * Usar field(default_factory=VM) para que cada proceso tenga su propia VM
   - prog: Callable[[Kernel, PCB], None] - Programa a ejecutar
     * Firma: recibe kernel y pcb, no retorna nada
     * Implementa "un paso" de ejecución (time slice)
   
   Campos opcionales:
   - name: str - Nombre descriptivo del proceso
   - cpu_time: int - Tiempo total de CPU usado (en time slices)
   - priority: int - Prioridad del proceso

3. Requisitos adicionales:
   - Importar VM desde vos.core.vm
   - Incluir docstrings explicando cada campo
   - Método __repr__ para debugging
   - __post_init__ para inicializar name si está vacío

Explica el propósito de cada campo y cómo se relaciona con el scheduling Round-Robin.
```

### Cambios y Justificación:
- **Agregué especificación de firma de `prog`**: El prompt inicial no especificaba cómo debía ser la función prog. Es crucial definir que recibe (kernel, pcb) para que el programa pueda interactuar con el sistema y modificar su propio estado.
- **Agregué field(default_factory=VM)**: El prompt inicial no especificaba cómo crear instancias únicas de VM por proceso. Esto es esencial para el aislamiento de memoria.
- **Agregué campos opcionales**: name, cpu_time y priority son útiles para debugging y estadísticas.
- **Agregué métodos especiales**: __repr__ y __post_init__ mejoran la usabilidad.

### Respuesta Usada:
Ver archivo `vos/core/process.py` con la implementación completa.

---

## PROMPT 2: Scheduler Round-Robin

### Prompt Inicial:
```
Crea una clase Scheduler que gestione una cola de procesos READY y los seleccione en orden FIFO.
```

### Prompt Refinado (Final):
```
Implementa una clase Scheduler para scheduling Round-Robin con las siguientes especificaciones:

Estructura:
- Clase: Scheduler
- Archivo: vos/core/sched.py

Atributos:
- ready_queue: deque[PCB] - Cola FIFO de procesos listos
  * Usar collections.deque para eficiencia O(1) en ambos extremos

Métodos requeridos:

1. __init__(self)
   - Inicializa ready_queue vacía

2. add(self, pcb: PCB) -> None
   - Agrega un PCB a la cola de listos
   - Validación: pcb.state debe ser State.READY
   - Si no es READY, lanzar ValueError con mensaje explicativo
   - Agregar al final de la cola (append)
   - Imprimir mensaje de debug

3. next(self) -> Optional[PCB]
   - Retorna el siguiente proceso a ejecutar
   - Política: FIFO (tomar del frente de la cola)
   - Si la cola está vacía, retornar None
   - Remover el proceso de la cola (popleft)
   - Imprimir mensaje indicando qué proceso fue seleccionado

4. is_empty(self) -> bool
   - Retorna True si no hay procesos en la cola

5. size(self) -> int
   - Retorna cantidad de procesos en la cola

6. get_ready_pids(self) -> List[int]
   - Retorna lista de PIDs en la cola (para debugging)

7. __repr__(self) -> str
   - Representación legible del estado del scheduler

Conceptos a documentar:
- Ready Queue: qué es y por qué usar deque
- Round-Robin: cómo esta implementación soporta RR
- Fairness: cómo se garantiza que cada proceso reciba CPU

Incluye:
- Type hints completos
- Docstrings detallados
- Manejo de errores apropiado
- Mensajes de logging para debugging
```

### Cambios y Justificación:
- **Especifiqué usar deque**: El prompt inicial no especificaba la estructura de datos. deque es crucial para eficiencia O(1) en ambos extremos.
- **Agregué validación en add()**: Es importante validar que solo procesos READY entren a la cola.
- **Agregué métodos auxiliares**: is_empty(), size(), get_ready_pids() son útiles para el Kernel y para debugging.
- **Agregué logging**: Los prints ayudan a entender el flujo de scheduling.
- **Especifiqué retornar Optional[PCB]**: El prompt inicial no clarificaba qué hacer cuando la cola está vacía.

### Respuesta Usada:
Ver archivo `vos/core/sched.py` con la implementación completa.

---

## PROMPT 3: Kernel - Gestión de Procesos

### Prompt Inicial:
```
Implementa una clase Kernel que pueda crear procesos y ejecutarlos con dispatch().
```

### Prompt Refinado (Final):
```
Implementa una clase Kernel que gestione procesos y scheduling con las siguientes especificaciones:

Estructura:
- Clase: Kernel
- Archivo: vos/core/sys.py

Atributos:
- procs: Dict[int, PCB] - Tabla de procesos (pid → PCB)
- sched: Scheduler - Instancia del scheduler Round-Robin
- running: Optional[PCB] - Proceso actualmente ejecutándose
- next_pid: int - Contador para asignar PIDs únicos

Métodos requeridos:

1. __init__(self)
   - Inicializar todas las estructuras vacías
   - Imprimir mensaje de inicialización del kernel

2. spawn(self, prog: Callable, name: str = "") -> int
   - Crear un nuevo proceso
   
   Algoritmo:
   a) Asignar nuevo PID único (usar y incrementar self.next_pid)
   b) Crear PCB con:
      - pid: el PID asignado
      - state: State.NEW
      - vm: nueva instancia (default_factory)
      - prog: el programa recibido
      - name: el nombre recibido o "Process-{pid}"
   c) Agregar PCB a self.procs[pid]
   d) Transicionar a READY: pcb.state = State.READY
   e) Agregar al scheduler: self.sched.add(pcb)
   f) Imprimir logs del proceso de creación
   g) Retornar el PID
   
   Returns: PID del proceso creado

3. dispatch(self) -> None
   - Ejecutar un time slice del scheduler Round-Robin
   
   Algoritmo detallado:
   a) Si self.running existe Y self.running.state == State.RUNNING:
      - El proceso anterior no terminó ni se bloqueó
      - Debe ser reencolado para dar chance a otros procesos
      - Transición: self.running.state = State.READY
      - Reencolar: self.sched.add(self.running)
      - Imprimir log de reencolado
   
   b) Obtener siguiente proceso:
      - pcb = self.sched.next()
      - Si pcb es None:
        * No hay procesos listos
        * Imprimir "CPU IDLE"
        * self.running = None
        * return (terminar dispatch)
   
   c) Preparar proceso para ejecutar:
      - self.running = pcb
      - pcb.state = State.RUNNING
      - Imprimir información del proceso (pid, name, cpu_time actual)
   
   d) Ejecutar UN PASO del programa:
      - Dentro de try-except para capturar errores
      - Llamar: pcb.prog(self, pcb)
      - El programa puede cambiar pcb.state a TERMINATED o WAITING
      - Incrementar: pcb.cpu_time += 1
      - Imprimir estado después de ejecución
   
   e) Manejo de errores:
      - Si hay excepción, marcar proceso como TERMINATED
      - Imprimir error
   
   Nota importante: El Kernel NO decide cuándo un proceso termina.
   El programa mismo (pcb.prog) cambia su estado a TERMINATED cuando termina.

4. ps(self) -> List[Tuple[int, str]]
   - Retorna tabla de procesos estilo Unix 'ps'
   - Formato: [(pid, estado_nombre), ...]
   - Ordenado por PID

5. ps_detailed(self) -> List[Dict]
   - Retorna información detallada de todos los procesos
   - Incluir: pid, name, state, cpu_time, priority

6. get_process(self, pid: int) -> Optional[PCB]
   - Obtiene PCB por PID
   - Retorna None si no existe

7. print_process_table(self) -> None
   - Imprime tabla formateada de procesos
   - Mostrar: PID, NAME, STATE, CPU_TIME
   - Incluir estadísticas: total procesos, en ready, running

8. __repr__(self) -> str
   - Representación legible del kernel

Conceptos a documentar:
- Time Slice: qué significa ejecutar "un paso"
- Context Switch: cómo dispatch() cambia entre procesos
- Process Table: para qué sirve self.procs
- State Transitions: cómo los procesos cambian de estado

Incluye:
- Type hints completos
- Logging extensivo para entender el flujo
- Manejo robusto de errores
- Docstrings detallados explicando cada paso del algoritmo
```

### Cambios y Justificación:
- **Detallé el algoritmo de dispatch()**: El prompt inicial no especificaba cómo manejar el proceso anterior running. Es crucial reencolarlo si aún está RUNNING.
- **Especifiqué manejo de CPU IDLE**: Cuando no hay procesos, el Kernel debe manejar esto elegantemente.
- **Agregué manejo de errores**: Los programas pueden fallar, el Kernel debe capturar excepciones.
- **Agregué métodos auxiliares**: ps_detailed(), get_process(), print_process_table() son útiles para debugging.
- **Clarif iqué quién controla terminación**: El programa (prog) decide cuándo terminar cambiando su propio estado, no el Kernel.
- **Agregué logging extensivo**: Es crucial ver el flujo de ejecución para entender el scheduling.

### Respuesta Usada:
Ver archivo `vos/core/sys.py` con la implementación completa.

---

## PROMPT 4: Programas de Demo

### Prompt Inicial:
```
Crea programas de ejemplo que puedan ejecutarse como procesos y demuestren el uso de memoria virtual.
```

### Prompt Refinado (Final):
```
Implementa programas de demostración para procesos con las siguientes especificaciones:

Estructura:
- Archivo: vos/core/demo_tasks.py
- Cada programa es una función con firma: prog(kernel, pcb) -> None

Requisitos generales para todos los programas:
1. Usar memoria virtual del proceso: pcb.vm.read_byte(), pcb.vm.write_byte()
2. Mantener estado entre time slices usando atributos del PCB (ej: pcb._counter)
3. Cambiar pcb.state a State.TERMINATED cuando terminen
4. Imprimir logs descriptivos de lo que hacen
5. Demostrar diferentes patrones de uso de memoria

Programas requeridos:

1. touch_pages_prog(kernel, pcb)
   - Escribe el PID del proceso en varias páginas de su VM
   - Demuestra: page faults, escritura a VM, aislamiento
   - En cada time slice:
     * Escribir pcb.pid en vaddr = page_no * PAGE_SIZE
     * Leer de vuelta para verificar
     * Incrementar contador interno (pcb._touch_counter)
     * Terminar después de tocar NUM_PAGES páginas (ej: 5)

2. idle_prog(kernel, pcb)
   - Proceso simple que solo cuenta time slices
   - Demuestra: proceso mínimo sin uso de memoria
   - En cada time slice:
     * Incrementar contador (pcb._idle_counter)
     * Imprimir progreso
     * Terminar después de MAX_SLICES (ej: 8)

3. fibonacci_prog(kernel, pcb)
   - Calcula secuencia de Fibonacci y almacena en VM
   - Demuestra: cómputo real + almacenamiento en memoria
   - Estado: pcb._fib_state = {count, prev, curr}
   - En cada time slice:
     * Calcular siguiente número de Fibonacci
     * Almacenar (mod 256) en memoria: vaddr = count * 4
     * Actualizar estado
     * Terminar después de MAX_NUMBERS (ej: 10)

4. memory_scanner_prog(kernel, pcb)
   - Lee secuencialmente de su memoria virtual
   - Demuestra: lecturas, page faults en lecturas
   - En cada time slice:
     * Leer de vaddr = page_no * PAGE_SIZE + 10
     * Imprimir valor leído
     * Terminar después de NUM_READS (ej: 6)

5. counter_writer_prog(kernel, pcb)
   - Escribe contador incremental en memoria
   - Demuestra: escrituras repetidas, dirty pages
   - En cada time slice:
     * Escribir valor en memoria
     * Incrementar contador
     * Terminar después de MAX_WRITES (ej: 7)

6. pattern_writer_prog(kernel, pcb)
   - Escribe un patrón en múltiples ubicaciones
   - Demuestra: uso intensivo de memoria, múltiples escrituras por slice
   - En cada time slice:
     * Escribir patrón en varios offsets de una página
     * Usar bucle for interno para múltiples escrituras
     * Terminar después de NUM_PAGES (ej: 4)

Patrón de implementación para todos:

```python
def programa_prog(kernel, pcb):
    """Docstring explicando qué hace el programa."""
    
    # Constantes
    MAX_ITERATIONS = 10
    
    # Inicializar estado si no existe
    if not hasattr(pcb, '_program_state'):
        pcb._program_state = valor_inicial
        print(f"   🔧 [{pcb.name}] Inicializando...")
    
    # Verificar si terminamos
    if pcb._program_state >= MAX_ITERATIONS:
        print(f"   ✅ [{pcb.name}] Completado")
        pcb.state = State.TERMINATED
        return
    
    # Hacer trabajo del time slice
    # ... usar pcb.vm.read_byte() / pcb.vm.write_byte() ...
    
    # Incrementar estado
    pcb._program_state += 1
    
    # Terminar si completamos
    if pcb._program_state >= MAX_ITERATIONS:
        print(f"   🏁 [{pcb.name}] Terminando")
        pcb.state = State.TERMINATED
```

Requisitos de cada programa:
- Docstring explicando propósito y comportamiento
- Logs con prefijo [nombre_proceso] para identificar salida
- Inicialización lazy de estado (usar hasattr)
- Terminación explícita (pcb.state = State.TERMINATED)
- Valores numéricos apropiados (mod 256 para bytes)
- Uso realista de direcciones virtuales (esparcidas en páginas)

Importaciones necesarias:
- from vos.core.process import State
- from vos.core.vm import PAGE_SIZE
```

### Cambios y Justificación:
- **Especifiqué 6 programas diversos**: El prompt inicial no especificaba cuántos ni qué tipos. Variedad demuestra diferentes aspectos del sistema.
- **Definí patrón de implementación**: Todos los programas deben seguir un patrón consistente para manejo de estado y terminación.
- **Agregué requisito de logs con prefijo**: Facilita identificar qué proceso produce cada salida.
- **Especifiqué uso de atributos del PCB para estado**: Esto es crucial porque los programas no tienen memoria persistente entre llamadas.
- **Agregué verificación de terminación al inicio**: Evita trabajo innecesario si ya terminamos.
- **Especifiqué valores realistas**: mod 256 para bytes, direcciones esparcidas, etc.
- **Agregué bucles internos en pattern_writer**: Demuestra que un time slice puede hacer múltiple trabajo.

### Respuesta Usada:
Ver archivo `vos/core/demo_tasks.py` con la implementación completa de los 6 programas.

---

## Resumen de Mejoras en los Prompts

### Cambios Generales Aplicados:
1. **Especificación de tipos completa**: Agregué type hints detallados
2. **Algoritmos paso a paso**: Descompuse operaciones complejas
3. **Manejo de errores**: Agregué validaciones y excepciones
4. **Logging extensivo**: Facilita debugging y comprensión
5. **Casos edge**: Especifiqué qué hacer cuando queues vacías, errores, etc.
6. **Patrones consistentes**: Definí estructuras repetibles
7. **Documentación**: Docstrings explicando propósito y funcionamiento

### Lecciones Aprendidas:
- **Prompts vagos producen código incompleto**: Es mejor ser excesivamente específico
- **Los algoritmos deben descomponerse**: Paso a paso es más fácil de verificar
- **El contexto importa**: Referencias a otros módulos deben ser explícitas
- **La validación es crucial**: Siempre especificar qué hacer con inputs inválidos
- **El debugging es parte del diseño**: Logs y métodos auxiliares deben planearse desde el inicio