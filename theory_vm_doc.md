# Memoria Virtual: Del Concepto a la Simulación
## Informe Teórico Completo

### Introducción

La memoria virtual es uno de los mecanismos fundamentales en los sistemas operativos modernos que permite la gestión eficiente de la memoria y el aislamiento entre procesos. Este documento proporciona una explicación exhaustiva de los conceptos teóricos necesarios para implementar un simulador de memoria virtual.

---

## 1. Memoria Virtual vs. Memoria Física

### Memoria Física (RAM)

La memoria física se refiere a la memoria principal o RAM instalada en la computadora, que sirve como el medio de almacenamiento primario para ejecutar programas y almacenar datos. El sistema operativo divide este espacio de memoria física en celdas de almacenamiento representadas con direcciones físicas.

**Características clave:**
- Espacio de direcciones contiguo y limitado
- Acceso directo por la CPU
- Capacidad fija determinada por el hardware instalado
- Direcciones físicas reales que corresponden a ubicaciones de RAM

### Memoria Virtual

La memoria virtual es un esquema de gestión de memoria que permite que la memoria física utilizada por un programa sea no contigua, ayudando a evitar el problema de fragmentación de memoria. 

**Ventajas principales:**
- **Abstracción**: Cada proceso opera con su propio espacio de direcciones virtuales aislado
- **Eficiencia**: Permite ejecutar programas más grandes que la RAM disponible
- **Protección**: Aísla procesos entre sí para mayor seguridad
- **Flexibilidad**: Simplifica la carga de programas al no requerir memoria contigua

Desde la perspectiva de cada proceso, tiene su propio espacio de memoria virtual aislado, apareciendo como un bloque contiguo, aunque la memoria física del proceso puede estar dispersa.

---

## 2. Paginación y Tablas de Páginas

### Concepto de Paginación

La paginación divide la memoria en bloques de tamaño fijo. La memoria virtual se divide en páginas, que tienen el mismo tamaño que los marcos (frames) en la memoria física.

**Terminología fundamental:**
- **Página (Page)**: Un bloque contiguo de longitud fija de memoria virtual, descrito por una única entrada en una tabla de páginas. Es la unidad más pequeña de datos para la gestión de memoria
- **Marco (Frame)**: Un bloque contiguo de memoria que corresponde a ubicaciones de almacenamiento reales en la RAM
- **Tamaño de página**: Típicamente 4 KB (4096 bytes), aunque los sistemas modernos también soportan páginas más grandes

### Tabla de Páginas (Page Table)

Una tabla de páginas es una estructura de datos utilizada por un sistema de memoria virtual para almacenar mapeos entre direcciones virtuales y direcciones físicas.

**Componentes de una entrada de tabla de páginas (PTE):**

1. **Número de Marco Físico (PFN/PPN)**: Indica dónde está almacenada la página en memoria física
2. **Bit de Validez/Presente**: Indica si la traducción particular es válida; cuando un proceso intenta acceder a memoria marcada como inválida, generará una trampa al SO
3. **Bit Sucio (Dirty Bit)**: Indica si la página contiene datos que deben ser escritos al almacenamiento estable antes de ser reemplazada
4. **Bit de Referencia**: Indica si la página ha sido accedida recientemente

**Funcionamiento:**
- Cada proceso tiene su propia tabla de páginas
- El SO indexa la tabla por el número de página virtual (VPN)
- Busca la entrada de la tabla de páginas (PTE) en ese índice
- Obtiene el número de marco físico (PFN) deseado

---

## 3. Traducción de Direcciones

### Proceso de Traducción

Una dirección virtual se divide en dos componentes: el número de página virtual (VPN) y el desplazamiento (offset) dentro de la página.

**Pasos del proceso:**

```
Dirección Virtual: [VPN | Offset]
                     ↓
              Tabla de Páginas
                     ↓
Dirección Física:  [PFN | Offset]
```

**Ejemplo práctico:**
- Dirección virtual de 32 bits con páginas de 4 KB (12 bits de offset)
- VPN: 20 bits superiores → identifican la página (2²⁰ = 1,048,576 páginas posibles)
- Offset: 12 bits inferiores → posición dentro de la página (2¹² = 4096 bytes)

### Memory Management Unit (MMU)

El mapeo de direcciones virtuales a físicas es realizado por la Memory Management Unit (MMU), que es un dispositivo de hardware, y este mapeo se conoce como la técnica de paginación.

**Translation Lookaside Buffer (TLB):**
Un cache de tipo muy rápido que almacena mapeos utilizados recientemente de la tabla de páginas del sistema operativo. Cuando no puede satisfacer una solicitud (TLB miss), el mapeo debe obtenerse de la tabla de páginas.

---

## 4. Manejo de Fallos de Página

### ¿Qué es un Fallo de Página?

Cuando un proceso intenta acceder a una página cuyo bit válido-inválido está establecido en inválido, ocurre un fallo de página, causando una trampa al sistema operativo.

**Causas de fallos de página:**
1. La página no está en memoria física (está en disco o nunca fue cargada)
2. Intento de escritura en una página de solo lectura
3. Acceso a una página con permisos inadecuados
4. Acceso a una dirección virtual inválida

### Manejo del Fallo de Página por el SO

El sistema operativo sigue estos pasos para manejar el fallo de página:
1. Verifica la tabla interna del proceso para determinar si la referencia de memoria es válida
2. Localiza un marco libre en la memoria física
3. Instruye al disco para leer la página requerida en el marco recién asignado
4. Una vez completado, actualiza la tabla interna del proceso y la tabla de páginas para reflejar la presencia de la página
5. El proceso luego reanuda la ejecución desde la instrucción que causó el fallo de página

---

## 5. Almacenamiento de Respaldo (Backing Store) y Bit Sucio

### Backing Store

El backing store es el almacenamiento secundario (típicamente disco duro o SSD) donde residen las páginas cuando no están en memoria física. Esta técnica históricamente se conoce como swapping, y cuando se combina con memoria virtual, se conoce como memoria virtual paginada.

**Propósito:**
- Permitir que el tamaño agregado de los espacios de direcciones exceda la memoria física
- Almacenar páginas que no están siendo utilizadas activamente
- Proporcionar persistencia para datos modificados

### Bit Sucio (Dirty Bit)

Cuando este esquema se usa, cada página o marco tiene un bit de modificación asociado en el hardware. Cuando cualquier palabra o byte en la página debe ser escrito, el bit de modificación para la página es establecido por el hardware, indicando que la página ha sido modificada.

**Funcionamiento:**
- **Bit = 0**: La página no ha sido modificada desde que fue cargada. No necesita ser escrita de vuelta al disco
- **Bit = 1**: La página ha sido modificada. Debe ser escrita al backing store antes de ser reemplazada

Reduce el tiempo de E/S a la mitad si la página no ha sido modificada, mejorando significativamente el rendimiento del sistema.

---

## 6. Reemplazo de Páginas FIFO

### Concepto General de Reemplazo de Páginas

El reemplazo de páginas completa la separación entre memoria lógica y física; se puede proporcionar memoria virtual grande sobre memoria física más pequeña.

Cuando todos los marcos están ocupados y se necesita cargar una nueva página, el SO debe seleccionar una página víctima para desalojar.

### Algoritmo FIFO (First-In, First-Out)

El algoritmo FIFO es el más simple. La idea es obvia por el nombre: el sistema operativo mantiene un registro de todas las páginas en memoria en una cola, con la llegada más reciente al final y la llegada más antigua al frente.

**Características:**
- **Implementación**: Se implementa manteniendo un registro de todas las páginas en una cola. La página más nueva está en la cabeza de la cola y la página más antigua está en la cola
- **Criterio de reemplazo**: Siempre se selecciona la página que ha estado en memoria por más tiempo
- **Overhead bajo**: Requiere poca contabilidad por parte del SO

**Ventajas:**
- Extremadamente simple de implementar
- Bajo costo computacional
- Predecible y determinista

**Desventajas:**
- Anomalía de Belady: es posible tener más fallos de página al aumentar el número de marcos de página mientras se usa el algoritmo de reemplazo FIFO
- No considera el patrón de uso real de las páginas
- Puede reemplazar páginas frecuentemente utilizadas

### Algoritmo Second-Chance (Mejora de FIFO)

Una forma modificada del algoritmo FIFO, conocida como algoritmo de segunda oportunidad, funciona mejor que FIFO con poco costo adicional. Examina el bit de referencia; si no está establecido, la página es intercambiada. De lo contrario, el bit de referencia se borra y la página se inserta al final de la cola.

---

## 7. Aislamiento de Procesos

### Importancia del Aislamiento

En sistemas operativos que no son de espacio de direcciones único, la información del ID del proceso es necesaria para que el sistema de gestión de memoria virtual sepa qué páginas asociar a qué proceso. Dos procesos pueden usar dos direcciones virtuales idénticas para diferentes propósitos.

**Beneficios del aislamiento:**
1. **Seguridad**: Un proceso no puede acceder a la memoria de otro proceso
2. **Estabilidad**: Un error en un proceso no corrompe la memoria de otros
3. **Simplicidad**: Cada proceso ve su propio espacio de direcciones limpio y contiguo

### Implementación Multi-Proceso

La tabla de páginas debe proporcionar mapeos de memoria virtual diferentes para los dos procesos. Esto puede hacerse asignando a los dos procesos identificadores de mapa de direcciones distintos, o usando IDs de proceso.

**Mecanismos:**
- Cada proceso tiene su propia tabla de páginas
- El registro CR3 (en arquitectura x86) apunta a la tabla de páginas del proceso actual
- El SO cambia este registro durante el cambio de contexto
- Las páginas compartidas pueden mapearse a ambos espacios de direcciones cuando sea necesario

---

## 8. Conexión con la Simulación de Software

### Del Hardware al Software

Nuestro simulador implementa los conceptos fundamentales de memoria virtual en software Python:

1. **Estructuras de Datos**:
   - `PTEntry`: Simula una entrada de tabla de páginas con bits de control
   - `PageTable`: Mapea páginas virtuales a marcos físicos
   - `PhysicalMemory`: Representa la RAM con marcos de tamaño fijo

2. **Operaciones Clave**:
   - **Traducción de direcciones**: De direcciones virtuales a físicas
   - **Manejo de fallos de página**: Cargar páginas desde backing store
   - **Reemplazo FIFO**: Desalojar páginas cuando la memoria está llena
   - **Gestión del bit sucio**: Decidir si escribir de vuelta al disco

3. **Simplificaciones**:
   - Un solo proceso (no múltiples tablas de páginas)
   - Sin TLB (traducción directa cada vez)
   - Backing store simulado (sin E/S real de disco)
   - Sin protección de memoria ni permisos

### Objetivos de Aprendizaje

Esta simulación permite comprender:
- Cómo el hardware MMU traduce direcciones
- Por qué los fallos de página son costosos
- Cómo el reemplazo de páginas afecta el rendimiento
- La importancia del bit sucio para optimizar E/S

---

## Referencias y Fuentes Autorizadas

1. **Silberschatz, A., Galvin, P. B., & Gagne, G.** - "Operating System Concepts" - Concepto estándar de la industria sobre sistemas operativos
2. **Tanenbaum, A. S. & Bos, H.** - "Modern Operating Systems" - Tratado completo sobre SO modernos
3. **Arpaci-Dusseau, R. H. & Arpaci-Dusseau, A. C.** - "Operating Systems: Three Easy Pieces" - Recurso educativo abierto
4. **Wikipedia**: Artículos sobre Memory Paging, Page Tables, Page Replacement Algorithms
5. **GeeksforGeeks**: Tutoriales técnicos sobre algoritmos de reemplazo de páginas
6. **OSDev Wiki**: Documentación técnica para desarrollo de sistemas operativos

---

## Conclusión

La memoria virtual es un componente esencial de los sistemas operativos modernos que proporciona abstracción, eficiencia y protección. A través de mecanismos como paginación, tablas de páginas, manejo de fallos de página y algoritmos de reemplazo, los sistemas operativos pueden:

- Ejecutar programas más grandes que la memoria física disponible
- Aislar procesos entre sí para mayor seguridad
- Optimizar el uso de recursos mediante paginación bajo demanda
- Proporcionar a cada proceso la ilusión de un espacio de memoria grande y contiguo

La implementación de un simulador de memoria virtual en Python permite comprender profundamente estos conceptos y apreciar la complejidad del software de sistemas.