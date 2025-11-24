# Lab 2: Reflexiones Argumentativas
## Respuestas a Preguntas Críticas sobre Procesos y Scheduling

---

## 1. Program vs Process

### ¿Cuál es la diferencia entre un programa y un proceso?

Un **programa** es una entidad completamente pasiva: un archivo ejecutable almacenado en disco que contiene código máquina y datos estáticos. Es simplemente una secuencia de instrucciones esperando ser ejecutadas, similar a una receta escrita en un libro de cocina.

Un **proceso**, por el contrario, es una entidad activa: es un programa en ejecución con estado dinámico, recursos asignados y contexto de ejecución. El proceso incluye:

1. **El código del programa** (text section)
2. **Estado de ejecución actual**:
   - Valor del Program Counter (próxima instrucción)
   - Valores de todos los registros de CPU
   - Contenido del stack
3. **Recursos asignados**:
   - Memoria (heap, stack, datos)
   - Archivos abiertos
   - Dispositivos de I/O
4. **Identificación y metadatos**:
   - Process ID (PID)
   - Estado (READY, RUNNING, etc.)
   - Prioridad de scheduling
   - Tiempo de CPU usado

**Analogía práctica**: 
- **Programa** = Receta en un libro
- **Proceso** = Cocinar activamente esa receta, con ingredientes específicos, progreso actual y utensilios en uso

**Implicación importante**: Múltiples procesos pueden ejecutar el mismo programa simultáneamente. Por ejemplo, puedes tener 5 instancias del navegador abiertas (5 procesos) ejecutando el mismo programa (archivo ejecutable del navegador). Cada proceso tiene su propio estado, memoria y recursos independientes.

### ¿Cómo el PCB convierte un programa estático en un proceso en ejecución?

El **Process Control Block (PCB)** es el mecanismo crítico que realiza esta transformación. El PCB actúa como el "contenedor" que rodea al programa con todo el contexto necesario para convertirlo de código pasivo a entidad ejecutable.

**Transformación paso a paso**:

1. **Cuando el SO crea un proceso**:
   - Carga el programa desde disco a memoria
   - Crea un PCB nuevo con un PID único
   - Inicializa el Program Counter apuntando a la primera instrucción del programa
   - Asigna memoria virtual (crea page table)
   - Inicializa registros de CPU a valores por defecto
   - Establece estado inicial (NEW)

2. **El PCB "envuelve" el programa con**:
   - **Identidad**: PID para que el SO pueda referenciarlo
   - **Localización**: Puntero a la page table (dónde está el código/datos en memoria)
   - **Estado de ejecución**: PC, registros (dónde está en su ejecución)
   - **Control**: Estado actual (READY, RUNNING) para el scheduler
   - **Recursos**: Qué archivos tiene abiertos, cuánta memoria usa

3. **Durante la ejecución**:
   - El PCB se actualiza constantemente:
     - PC avanza con cada instrucción
     - Registros cambian con operaciones
     - Estado cambia con transiciones
   - En context switches, todo el contexto se guarda en el PCB
   - Cuando el proceso vuelve a ejecutar, se restaura desde el PCB

**Ejemplo concreto en nuestra simulación**:

```python
# ANTES: Solo un programa (función Python)
def mi_programa(kernel, pcb):
    # código...
    pass

# DESPUÉS: El spawn() lo convierte en proceso
pid = kernel.spawn(mi_programa, "MiProceso")

# Internamente, spawn() creó:
pcb = PCB(
    pid=1,                          # Identidad única
    state=State.NEW,                # Estado inicial
    vm=VM(),                        # Espacio de direcciones propio
    prog=mi_programa,               # El código a ejecutar
    cpu_time=0                      # Contabilidad
)
# Y lo insertó en la process table y ready queue
```

Sin el PCB, el SO no tendría forma de:
- Identificar el proceso
- Saber dónde está su memoria
- Recordar dónde pausó su ejecución
- Cambiar entre múltiples procesos
- Gestionar sus recursos

El PCB es literalmente lo que diferencia "código en disco" de "programa ejecutándose".

---

## 2. PCB Design

### ¿Por qué es útil que el PCB contenga al menos: pid, state, vm y prog?

Cada uno de estos campos es **esencial** para una función específica del sistema operativo. No son opcionales ni redundantes:

#### **1. PID (Process ID) - Identidad**

**Propósito**: Identificador único que permite al SO referenciar y manipular el proceso.

**Por qué es necesario**:
- El SO mantiene múltiples procesos simultáneamente en la process table
- Operaciones como kill, wait, signals necesitan especificar qué proceso
- Debugging y logging requieren identificar procesos
- Relaciones padre-hijo entre procesos usan PIDs (PPID)

**Sin PID**:
- No habría forma de distinguir procesos
- Imposible referenciar un proceso específico
- El comando `ps` no podría listar procesos
- `kill -9 <pid>` no funcionaría

**En nuestra simulación**:
```python
# kernel.ps() retorna [(pid, estado), ...]
# Si no hubiera PID, ¿cómo identificaríamos cada proceso?
```

#### **2. State - Control de Scheduling**

**Propósito**: Indica el estado actual del proceso en su ciclo de vida.

**Por qué es necesario**:
- El **scheduler solo puede seleccionar procesos READY**
- Procesos WAITING no deben ejecutar aunque CPU esté libre
- Procesos TERMINATED deben limpiarse
- Las transiciones de estado son la base del multitasking

**Sin state**:
- El scheduler no sabría qué procesos puede ejecutar
- Procesos esperando I/O consumirían CPU innecesariamente
- No habría forma de saber si un proceso terminó
- Context switches serían imposibles de gestionar correctamente

**En nuestra simulación**:
```python
def dispatch(self):
    # Reencolar solo si aún RUNNING (no terminó)
    if self.running and self.running.state == State.RUNNING:
        self.running.state = State.READY
        self.sched.add(self.running)
    
    # Scheduler solo tiene procesos READY
    pcb = self.sched.next()
    
    # Sin state, ¿cómo sabríamos qué hacer con cada proceso?
```

#### **3. VM (Virtual Memory) - Aislamiento**

**Propósito**: Espacio de direcciones virtual propio del proceso.

**Por qué es necesario**:
- **Aislamiento**: Proceso A no puede acceder memoria de Proceso B
- **Seguridad**: Previene que procesos lean/modifiquen datos de otros
- **Abstracción**: Cada proceso ve un espacio de direcciones limpio desde 0
- **Protección**: Errores en un proceso no corrompen otros

**Sin vm propio**:
- Todos los procesos compartirían la misma memoria
- Escrituras de un proceso sobrescribirían datos de otros
- No habría protección ni seguridad
- Un bug en un proceso crashearía todo el sistema

**En nuestra simulación**:
```python
# Cada PCB tiene su VM propia:
pcb = PCB(
    pid=1,
    vm=VM()  # Nueva instancia única
)

# Si dos procesos escriben en vaddr=100:
proceso1.vm.write_byte(100, 42)
proceso2.vm.write_byte(100, 99)

# Cada uno ve su propio valor, no interfieren
```

#### **4. Prog - El Código a Ejecutar**

**Propósito**: Referencia al programa (código) que el proceso debe ejecutar.

**Por qué es necesario**:
- El PCB debe saber **qué código ejecutar** cuando recibe CPU
- Durante dispatch(), el kernel llama `pcb.prog(kernel, pcb)`
- Sin referencia al programa, el proceso sería solo metadatos sin comportamiento

**Sin prog**:
- El proceso sería una "cáscara vacía" sin código
- dispatch() no sabría qué instrucciones ejecutar
- El proceso no podría hacer ningún trabajo útil

**En nuestra simulación**:
```python
def dispatch(self):
    pcb = self.sched.next()
    pcb.state = State.RUNNING
    
    # ¡Aquí es donde ejecutamos el programa del proceso!
    pcb.prog(self, pcb)  # Sin prog, esto fallaría
    
    pcb.cpu_time += 1
```

### ¿Qué problemas aparecerían si faltara alguno de estos campos?

Veamos el impacto concreto de omitir cada campo:

#### **Escenario 1: Sin PID**

```python
# Problema: No puedes referenciar procesos específicamente
kernel.kill(???)  # ¿Cómo especificas cuál matar?

# La process table sería un arreglo sin índice:
procs = [pcb1, pcb2, pcb3]  # ¿Cómo encuentras el correcto?

# Imposible implementar parent-child relationships
# Imposible logging: "Process ??? did something"
```

**Consecuencia**: Sistema no funcional, no hay forma de gestionar procesos individualmente.

#### **Escenario 2: Sin State**

```python
# Problema: Scheduler selecciona procesos incorrectos
def next(self):
    return self.ready_queue.popleft()  # Pero... ¿está realmente listo?

# Un proceso esperando I/O ejecutaría innecesariamente:
pcb.prog(kernel, pcb)  # ¡Pero el proceso está bloqueado esperando disco!

# No sabrías si un proceso terminó:
while True:  # Loop infinito, procesos terminados nunca se limpian
    dispatch()
```

**Consecuencia**: Scheduling incorrecto, desperdicicio de CPU, memory leaks (procesos muertos no se limpian).

#### **Escenario 3: Sin VM Propia (VM Compartida)**

```python
# PROBLEMA CRÍTICO: Todos los procesos comparten memoria

# Proceso 1:
def prog1(kernel, pcb):
    shared_vm.write_byte(100, 42)  # Guarda dato importante
    # ... más código ...
    valor = shared_vm.read_byte(100)  # Espera 42

# Proceso 2 (ejecuta antes de que prog1 lea):
def prog2(kernel, pcb):
    shared_vm.write_byte(100, 99)  # ¡Sobrescribe el 42!

# prog1 lee 99 en vez de 42 → comportamiento incorrecto
```

**Consecuencias reales**:
1. **Race conditions**: Resultados dependen del orden de ejecución
2. **Data corruption**: Procesos destruyen datos de otros
3. **No debugging**: Imposible aislar bugs
4. **Security nightmare**: Proceso malicioso lee contraseñas de otros
5. **Crashes**: Un proceso corrompe stack de otro → segfault

**Ejemplo histórico**: Sistemas antiguos sin protección de memoria (MS-DOS) sufrían crashes constantes porque cualquier programa podía corromper memoria del SO o de otros programas.

#### **Escenario 4: Sin Prog**

```python
# Problema: PCB sin comportamiento
pcb = PCB(pid=1, state=State.READY, vm=VM(), prog=None)

# En dispatch():
pcb.prog(self, pcb)  # AttributeError: NoneType no es callable

# O peor, todos los PCBs apuntan al mismo prog:
prog_shared = mi_programa
pcb1.prog = prog_shared
pcb2.prog = prog_shared  # ¡Misma función!

# No hay forma de tener procesos con comportamientos diferentes
```

**Consecuencia**: Procesos inútiles sin código, o todos los procesos hacen lo mismo (no útil).

### Resumen: Interdependencia de los Campos

Los cuatro campos forman un sistema interdependiente:

```
PID → Identifica el proceso (naming)
State → Controla cuándo puede ejecutar (control)
VM → Define qué memoria ve (abstraction + isolation)
Prog → Define qué hace cuando ejecuta (behavior)
```

Omitir cualquiera rompe una función fundamental del sistema operativo:
- Sin PID: No hay gestión
- Sin State: No hay scheduling correcto
- Sin VM: No hay aislamiento
- Sin Prog: No hay comportamiento

---

## 3. Per-Process Virtual Memory

### ¿Por qué cada proceso debe tener su PROPIO objeto VM (espacio de direcciones)?

La memoria virtual per-process es uno de los conceptos más fundamentales en sistemas operativos modernos. No es una optimización ni una característica "nice to have" - es **esencial** para un sistema operativo seguro y funcional.

#### **Razones Fundamentales**:

**1. Aislamiento (Isolation)**

Cada proceso opera en su propio "sandbox" de memoria completamente aislado de otros procesos.

```
Proceso A:                    Proceso B:
+-----------------+          +-----------------+
| Page Table A    |          | Page Table B    |
| vpage 0 → frame 3|          | vpage 0 → frame 7|
| vpage 1 → frame 1|          | vpage 1 → frame 2|
+-----------------+          +-----------------+
```

Ambos pueden usar la misma dirección virtual (ej: vaddr=100) pero mapean a diferentes marcos físicos:
- Proceso A lee vaddr=100 → frame 3
- Proceso B lee vaddr=100 → frame 7
- **No interfieren entre sí**

**2. Seguridad (Security)**

Sin VM per-process, cualquier proceso podría:
- Leer contraseñas de otros procesos
- Modificar código de otros programas
- Robar datos sensibles (tokens, llaves criptográficas)
- Inyectar código malicioso en otros procesos

Con VM per-process:
- Proceso malicioso está confinado a su propio espacio
- No puede "saltar" a memoria de otros procesos
- El SO media todos los accesos a memoria

**3. Estabilidad (Stability)**

Un bug en un proceso no afecta a otros:
- Buffer overflow en Proceso A solo corrompe su propia memoria
- NULL pointer dereference crashea solo ese proceso
- El SO puede terminar el proceso problemático sin afectar otros

**4. Simplicidad de Programación (Abstraction)**

Cada proceso ve un espacio de direcciones "limpio":
- Direcciones siempre empiezan en 0
- Espacio de direcciones parece contiguo
- No necesita saber dónde está físicamente en RAM
- No necesita coordinar con otros procesos por direcciones

### Escenario Concreto: Memoria Compartida Causando Problemas

Imaginemos un sistema SIN VM per-process, donde todos los procesos comparten el mismo espacio de memoria virtual:

```python
# Sistema INCORRECTO con VM compartida:
class Kernel:
    def __init__(self):
        self.shared_vm = VM()  # ¡UNA SOLA VM PARA TODOS!
    
    def spawn(self, prog):
        pcb = PCB(
            pid=self.next_pid,
            vm=self.shared_vm  # ¡TODOS COMPARTEN!
        )
        # ...
```

#### **Problema 1: Data Corruption**

```python
# Proceso 1: Programa de cálculo científico
def scientific_prog(kernel, pcb):
    if not hasattr(pcb, '_initialized'):
        # Guardar datos importantes en memoria
        for i in range(100):
            pcb.vm.write_byte(i, i)  # Datos críticos
        pcb._initialized = True
    
    # Leer datos para cálculo
    value = pcb.vm.read_byte(50)
    # Espera value=50, pero...

# Proceso 2: Programa de imagen
def image_prog(kernel, pcb):
    # Escribe imagen en memoria
    for i in range(200):
        pcb.vm.write_byte(i, 255)  # ¡Sobrescribe datos de Proceso 1!

# RESULTADO: scientific_prog lee 255 en vez de 50 → cálculo incorrecto
```

**Comportamiento Observado**:
```
Step 0: Proceso 1 escribe [0,1,2,...,99] en memoria
Step 1: Proceso 2 ejecuta
Step 2: Proceso 2 escribe [255,255,...] → ¡Destruye datos de Proceso 1!
Step 3: Proceso 1 lee → encuentra 255 en vez de 50 → FALLA
```

#### **Problema 2: Security Breach**

```python
# Proceso 1: Programa legítimo con contraseña
def banking_app(kernel, pcb):
    password = "supersecret123"
    # Guarda contraseña en memoria (por ejemplo, en vaddr=1000)
    for i, char in enumerate(password):
        pcb.vm.write_byte(1000 + i, ord(char))
    
    # ... usa contraseña para autenticación ...

# Proceso 2: Programa malicioso
def malware(kernel, pcb):
    # ¡Puede leer la contraseña de Proceso 1!
    stolen_password = ""
    for i in range(20):
        byte_val = pcb.vm.read_byte(1000 + i)
        if byte_val == 0:
            break
        stolen_password += chr(byte_val)
    
    print(f"🚨 Contraseña robada: {stolen_password}")
    # ¡SEGURIDAD COMPROMETIDA!
```

**Consecuencia**: Cualquier proceso puede leer datos sensibles de otros procesos.

#### **Problema 3: Stack Collision**

```python
# Proceso 1: Usa stack en vaddr 4000-5000
def process1(kernel, pcb):
    # Push datos al stack
    pcb.vm.write_byte(4500, 100)
    # ...

# Proceso 2: También intenta usar stack en vaddr 4000-5000
def process2(kernel, pcb):
    # ¡Colisión! Sobrescribe stack de Proceso 1
    pcb.vm.write_byte(4500, 200)

# RESULTADO: Stack corrupto → crashes impredecibles
```

#### **Problema 4: Debugging Imposible**

```python
# Bug report: "El programa calcula mal a veces"
# Con VM compartida:
# - El bug solo aparece cuando ciertos procesos corren juntos
# - Depende del orden de scheduling (race condition)
# - Imposible reproducir consistentemente
# - No sabes qué proceso causó la corrupción

# Con VM per-process:
# - Bug es reproducible (solo depende del proceso mismo)
# - Fácil aislar el problema
# - Testing es determinista
```

### Demostración en Nuestra Simulación

Veamos cómo VM per-process **previene** estos problemas:

```python
# Sistema CORRECTO con VM per-process:
def spawn(self, prog):
    pcb = PCB(
        pid=self.next_pid,
        vm=VM()  # ¡NUEVA INSTANCIA PARA CADA PROCESO!
    )

# Ahora los procesos están aislados:
pid1 = kernel.spawn(process1)
pid2 = kernel.spawn(process2)

pcb1 = kernel.get_process(pid1)
pcb2 = kernel.get_process(pid2)

# Cada uno escribe en "su" vaddr=100:
pcb1.vm.write_byte(100, 42)
pcb2.vm.write_byte(100, 99)

# Cada uno lee su propio valor:
assert pcb1.vm.read_byte(100) == 42  # ✓ Correcto
assert pcb2.vm.read_byte(100) == 99  # ✓ Correcto

# ¡No hay interferencia!
```

### ¿Cómo lo Logra VM Per-Process?

Cada proceso tiene su propia **page table**:

```
Proceso 1:
  Page Table 1:
    vpage 0 → frame 3
    vpage 1 → frame 1
  Cuando Proceso 1 accede vaddr=100:
    → page 0, offset 100
    → frame 3, offset 100
    → Dirección física: frame3[100]

Proceso 2:
  Page Table 2:
    vpage 0 → frame 7
    vpage 1 → frame 2
  Cuando Proceso 2 accede vaddr=100:
    → page 0, offset 100
    → frame 7, offset 100
    → Dirección física: frame7[100]  ← ¡Diferente!
```

Durante context switch:
1. Guardar puntero a page table del proceso saliente
2. Cargar puntero a page table del proceso entrante
3. Ahora todas las traducciones usan la nueva page table
4. El proceso ve solo "su" memoria

### Comparación: Con y Sin VM Per-Process

| Aspecto | VM Compartida | VM Per-Process |
|---------|---------------|----------------|
| **Aislamiento** | ❌ Ninguno | ✅ Total |
| **Seguridad** | ❌ Cualquiera lee todo | ✅ Confinado a su espacio |
| **Estabilidad** | ❌ Un bug crashea todo | ✅ Bug aislado al proceso |
| **Debugging** | ❌ Race conditions | ✅ Comportamiento determinista |
| **Complejidad programación** | ❌ Coordinar direcciones | ✅ Espacio limpio desde 0 |
| **Protección SO** | ❌ Procesos pueden corromper OS | ✅ SO protegido |

---

## Conclusión General

Los tres aspectos analizados (Program vs Process, Diseño del PCB, VM per-process) están profundamente interconectados:

1. **PCB transforma programa en proceso** agregando estado, identidad y recursos
2. **Los campos del PCB son indispensables** - cada uno cumple una función crítica
3. **VM per-process es fundamental** para aislamiento, seguridad y estabilidad

Omitir cualquiera de estos conceptos resultaría en un sistema operativo no funcional, inseguro o inestable. Son los pilares sobre los que se construyen los sistemas operativos modernos.

En nuestra simulación, aunque simplificada, estos conceptos se preservan fielmente, permitiéndonos experimentar con las ideas fundamentales de gestión de procesos y memoria virtual.