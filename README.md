# Sistema de Reservas de Hostel

Trabajo Final de **Programación 2** · Instituto Superior Del Milagro

> Este README es la **documentación viva** del proyecto: acá se registra qué se hizo, qué falta y por qué se tomaron las decisiones. Se actualiza a medida que avanza el trabajo.

| Dato | Detalle |
|---|---|
| Materia | Programación 2 |
| Integrantes | _Erazo Baltazar y Costilla Bruno_ |
| Proceso modelado | Gestionar Reserva |
| Entrega límite | 09/11/2026, 23:59 hs |
| Exposición | Desde el 11/11/2026 |
| Tecnologías, herramientas y conceptos utilizados | Python 3.12.0, MySQL 8.0.46, Aiven, PyQt, Logging, Pathlib, Pandas, Matplotlib, Variables de entorno, Dependencias, DBeaver, Connection Pooling, Inyección de Conexión en Cascada, Baja Logica|
| Formato de backups y reportes | JSON |

---

## Índice

1. [Narrativa descriptiva](#1-narrativa-descriptiva)
2. [Descripción del proceso](#2-descripción-del-proceso)
3. [Actores](#3-actores)
4. [Modelado de datos](#4-modelado-de-datos)
   - [4.1 Diagrama Entidad-Relación (DER)](#41-diagrama-entidad-relación-der)
   - [4.2 Derivación de tablas normalizadas](#42-derivación-de-tablas-normalizadas)
   - [4.3 Diagrama de Flujo de Datos (DFD)](#43-diagrama-de-flujo-de-datos-dfd)
   - [4.4 Diagrama de Clases (DCD)](#44-diagrama-de-clases-dcd)
5. [Flujos y Arquitectura del Sistema](#5-flujos-y-arquitectura-del-sistema)
   - [5.1 Flujo de comunicación del programa (Arquitectura)](#51-flujo-de-comunicación-del-programa-arquitectura)
   - [5.2 Flujos de datos (Capa DAO)](#52-flujos-de-datos-capa-dao)
   - [5.3 Flujos de lógica (Capa de Servicios) y procesos](#53-flujos-de-lógica-capa-de-servicios-y-procesos)
6. [Reglas del negocio](#6-reglas-del-negocio)
7. [Estructura del proyecto](#7-estructura-del-proyecto)
8. [Instalación y ejecución](#8-instalación-y-ejecución)
9. [Bitácora de avances](#9-bitácora-de-avances)
10. [Decisiones de diseño](#10-decisiones-de-diseño)
11. [Lista de pendientes](#11-lista-de-pendientes)

---

## 1. Narrativa descriptiva

## Vista de Gestión de Reservas en Hostales

### ¿Por qué nació la vista?

En la recepción de un hostal, el manejo manual o desorganizado de las reservas colapsa la atención y genera errores críticos en el mostrador. Los principales problemas que motivaron el desarrollo de esta vista específica para el recepcionista son:

- *El riesgo inminente de sobre reserva:* Al no contar con una validación automatizada en pantalla, es fácil asignar una misma habitación a dos huéspedes distintos para las mismas fechas.
- *Demoras en la atención cara a cara:* Buscar una reserva hojeando cuadernos o planillas lentas hace esperar al viajero recién llegado.
- *Errores al modificar o calcular estancias:* Ajustar fechas de última hora o calcular los costos de forma manual bajo presión genera confusiones y cuentas incorrectas.
- *Pérdida de control del inventario de habitaciones:* No saber con certeza inmediata qué espacios están libres, ocupados o bloqueados por cancelaciones.

## 2. Descripción del proceso

El sistema modela **un único proceso** de un hostel: la **gestión de la reserva de uno o muchos huéspedes**.

Permite registrar a un huésped o más huéspedes, consultar qué habitaciones están disponibles para unas fechas y una cantidad de personas, crear la reserva, modificarla y cancelarla. Además, genera estadísticas sobre las reservas para ayudar a la gestión del hostel (ocupación e ingresos).

**Objetivos**

- Evitar reservas duplicadas o superpuestas para una misma habitación.
- Calcular automáticamente el precio de la estadía según el tipo de habitación.
- Mantener un registro ordenado de huéspedes y reservas.
- Ofrecer un panel (dashboard) con indicadores para la toma de decisiones.

## 3. Actores

| Actor | Rol |
|---|---|
| **Recepcionista / administrador** | Usa el sistema: busca disponibilidad, carga huéspedes y reservas, cancela y consulta reportes. |
| **Cliente** | Persona que solicita la reserva. Aporta sus datos, pero no usa el sistema directamente. |

---

## 4. Modelado de datos

### 4.1 Diagrama Entidad-Relación (DER)

<p align="center">
  <img src="docs/img/WhatsApp Image 2026-11-02 at 22.00.09.jpeg" alt="Arquitectura del Sistema" width="100%" style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
</p>

**Borrador de entidades**:

| Entidad | Atributos principales |
|---|---|
| `CLIENTES` | id_cilente, nombre, apellido, dni, telefono, correo |
| `HUESPEDES` | id_huesped, nombre, apellido, dni, telefono |
| `HABITACIONES` | id_habitacion, numero, capacidad, precio_noche, estado |
| `RESERVAS` | id_reserva, fecha_reserva, fecha_ingreso, fecha_salida, estado, monto_total, id_cliente |
| `RESERVAS_X_HUESPEDES` | id_res_x_hue, id_reserva, id_huesped |
| `RESERVAS_X_HABITACIONES` | id_res_x_hab, id_reservas, id_habitacion |

### 4.2 Derivación de tablas normalizadas

Tablas resultantes de pasar el DER a 3FN, con datos de ejemplo para ver cómo quedan cargadas. **PK** indica clave primaria y **FK** clave foránea. Los datos son ficticios.

#### 1. CLIENTES

| id_cliente | nombre | apellido | dni | telefono | correo | activo |
|---|---|---|---|---|---|---|
| PK | | | | | | |
| 1 | Martín | Gómez | 30123456 | 387-4112233 | martin.gomez@example.com | True |
| 2 | Sofía | Álvarez | 28456789 | 387-4556677 | sofia.alvarez@example.com | True |

#### 2. HUESPEDES

| id_huesped | nombre | apellido | dni | telefono | activo |
|---|---|---|---|---|---|
| PK | | | | | |
| 1 | Lucía | Pérez | 40111222 | 387-4001122 | True |
| 2 | Tomás | Ruiz | 41222333 | 387-4002233 | True |
| 3 | Camila | Díaz | 42333444 | 387-4003344 | True |
| 4 | Julián | Torres | 39444555 | 387-4004455 | True |
| 5 | Valentina | Cruz | 38555666 | 387-4005566 | True |
| 6 | Mateo | Silva | 37666777 | 387-4006677 | True |

#### 3. HABITACIONES

| id_habitacion | numero | capacidad | precio_noche | estado | activo |
|---|---|---|---|---|---|
| PK | | | | | |
| 1 | 101 | 4 | 18000.00 | DISPONIBLE | True |
| 2 | 102 | 2 | 25000.00 | OCUPADA | True |
| 3 | 201 | 6 | 40000.00 | DISPONIBLE | True |
| 4 | 202 | 2 | 22000.00 | DISPONIBLE | True |

#### 4. RESERVAS

| id_reserva | fecha_reserva | fecha_ingreso | fecha_salida | estado | monto_total | id_cliente | activo |
|---|---|---|---|---|---|---|---|
| PK | | | | | | FK → CLIENTES | |
| 1 | 2026-10-30 | 2026-11-10 | 2026-11-13 | RESERVADA | 54000.00 | 1 | True |
| 2 | 2026-11-01 | 2026-11-15 | 2026-11-17 | RESERVADA | 86000.00 | 2 | True |
| 3 | 2026-11-02 | 2026-11-25 | 2026-11-27 | CANCELADA | 80000.00 | 1 | False |

#### 5. RESERVAS_X_HUESPEDES

| id_res_x_hue | id_reserva | id_huesped |
|---|---|---|
| PK | FK → RESERVAS | FK → HUESPEDES |
| 1 | 1 | 1 |
| 2 | 1 | 2 |
| 3 | 1 | 3 |
| 4 | 2 | 4 |
| 5 | 2 | 5 |
| 6 | 2 | 6 |
| 7 | 3 | 1 |

#### 6. RESERVAS_X_HABITACIONES

| id_res_x_hab | id_reserva | id_habitacion |
|---|---|---|
| PK | FK → RESERVAS | FK → HABITACIONES |
| 1 | 1 | 1 |
| 2 | 2 | 1 |
| 3 | 2 | 2 |
| 4 | 3 | 3 |

### 4.3 Diagrama de Flujo de Datos (DFD)

_(Pendiente: DFD nivel 0 y nivel 1. Guardar como `docs/dfd_nivel0.png` y `docs/dfd_nivel1.png`.)_

**Elementos a considerar**
- Entidades externas: recepcionista, huésped.
- Procesos: consultar disponibilidad, registrar huésped, crear reserva, modificar reserva, cancelar reserva, generar reportes.
- Almacenes de datos: habitaciones, huéspedes, reservas.

### 4.4 Diagrama de Clases (DCD)

<p align="center">
  <img src="docs/img/Captura de Pantalla 2026-11-06 a la(s) 04.30.37.png" alt="Arquitectura del Sistema" width="100%" style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
</p>

---

## 5. Flujos y Arquitectura del Sistema

### 5.1 Flujo de comunicación del programa (Arquitectura)

<p align="center">
  <img src="docs/img/Captura de Pantalla 2026-11-06 a la(s) 04.01.17.png" alt="Arquitectura del Sistema" width="100%" style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
</p>

### 5.2 Flujos de datos (Capa DAO)
La capa DAO (Data Access Object) gestiona la persistencia de los objetos en la base de datos MySQL mediante la inyección de conexiones en cascada y transacciones seguras:
- **Lectura/Búsqueda:** Consultas parametrizadas (por ID, DNI, etc.) que transforman registros tabulares en instancias de Modelos de Dominio (`OBJECTS`).
- **Escritura/Modificación:** Operaciones CRUD desacopladas de la lógica de negocio pura, permitiendo reutilizar la misma conexión en operaciones complejas de tablas intermedias.

#### 5.2.1 Flujo de Escritura, Modificación y Conexión (Create/Update/Delete)
```mermaid
stateDiagram-v2
    [*] --> ValidarConexionExterna
    ValidarConexionExterna --> CrearNuevaSiEsNecesaria
    CrearNuevaSiEsNecesaria --> EjecutarOperacionCRUD
    EjecutarOperacionCRUD --> GestionarTransaccionSegura
    GestionarTransaccionSegura --> CerrarConexionSiCorresponde
    CerrarConexionSiCorresponde --> [*]
```

#### 5.2.2 Flujo de Lectura y Mapeo a Objetos (Read)
```mermaid
stateDiagram-v2
    [*] --> RecibirParametro
    RecibirParametro --> EjecutarQueryParametrizada
    EjecutarQueryParametrizada --> ObtenerRegistrosTabulares
    ObtenerRegistrosTabulares --> MapearAInstanciaDominio
    MapearAInstanciaDominio --> RetornarObjetoModel
    RetornarObjetoModel --> [*]
```

### 5.3 Flujos de lógica (Capa de Servicios) y procesos

#### 5.3.1 Crear una reserva
```mermaid
stateDiagram-v2
    [*] --> ConsultarDisponibilidad
    ConsultarDisponibilidad --> BuscarHabitacionesDisponibles
    BuscarHabitacionesDisponibles --> RegistrarDatosHuesped
    RegistrarDatosHuesped --> GenerarReserva
```

### 5.3.2 Modificar una reserva

```mermaid
stateDiagram-v2
    [*] --> SeleccionarReserva
    SeleccionarReserva --> ConsultarInfoActual
    ConsultarInfoActual --> ModificarLosDatos
    ModificarLosDatos --> ValidarCambios
    ValidarCambios --> SI
    SI --> ActualizarReserva
    ValidarCambios --> NO
    NO --> RechazarModificacion
```

### 5.3.3 Actualizar una reserva

```mermaid
stateDiagram-v2
    [*] --> ReservaViejaBD
    ReservaViejaBD --> UPDATE
    UPDATE --> ReservaModificadaBD
```

### 5.3.4 Eliminar una reserva

```mermaid
stateDiagram-v2
    [*] --> SeleccionarReserva(activo=True)
    SeleccionarReserva(activo=True) --> UPDATE
    UPDATE --> SeleccionarReserva(activo=False)
```

### 5.3.5 Estados de la reserva

```mermaid
stateDiagram-v2
    [*] --> RESERVADA
    RESERVADA --> CANCELADA
    CANCELADA --> [*]
```

## 6. Reglas del negocio

1. La fecha de egreso debe ser posterior a la fecha de ingreso.
2. No se pueden crear reservas con fecha de ingreso en el pasado.
3. Una habitación no puede tener dos reservas activas que se superpongan en fechas.
4. La cantidad de personas no puede superar la capacidad de la habitación.
5. Un huésped se identifica por un ID único.
6. Una reserva cancelada no se elimina: se conserva con su estado.
7. No se puede eliminar un huésped ni una habitación que tengan reservas asociadas.
8. Los atributos como nombre y apellidos solo se pediran atomicamente.
9. Una habitación solo puede tener las siguientes capacidades (camas): 1, 2, 3 y 4

## 7. Estructura del proyecto

```
proceso_reserva_hostal/
├── backups/
│   ├── storage/
│   └── backup_manager.py
├── certs
│   └──ca.pem
├── core/
│   └── reserva_manager.py
├── dao/
│   ├── db_connection.py
│   └── huesped_dao.py
├── database/
│   ├── init_db.py
│   ├── datos_prueba.sql
│   ├── queries.sql
│   └── schema.sql
├── docs
│   └── img
├── loggers/
│   └── logger_config.py
├── models/
│   ├── clientes.py
│   ├── habitaciones.py
│   ├── huesped.py
│   ├── persona.py
│   └── reservas.py
├── reports/
│   └── analytics.py
├── venv/
├── views/
│   ├── CLI/
│   ├── GUI/
│   └── web/
├── .env
├── .env.example
├── .gitignore
├── LICENSE
├── main.py
└── README.md
└── requirements.txt
```

## 8. Instalación y ejecución

> _Completar a medida que el proyecto avance._

```bash
# 1. Clonar el repositorio
git clone <URL-del-repositorio>
cd hostel

# 2. Crear y activar el entorno virtual
python -m venv venv
source venv/bin/activate          # Mac / Linux
venv\Scripts\activate             # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env              # y completar usuario y contraseña de MySQL

# 5. Instala DBeaver, y configura una nueva conexion con los datos del .env

# Aun falta a esto
```

**Pruebas:** `pytest`

## 9. Bitácora de avances

Registrar cada avance con fecha y responsable. Lo más reciente, arriba.

| Fecha | Quién | Qué se hizo | Enlace (commit / PR / archivo) |
|---|---|---|---|
| 28/10/2026 | _Costilla_ | Definición del proceso: gestionar reserva. Creación del README. | — |

## 10. Decisiones de diseño

Anotar acá cada decisión importante y el motivo, para poder explicarlas en la exposición.

| Fecha | Decisión | Motivo |
|---|---|---|
| 28/10/2026 | Modelar solo la gestión de reservas | Alcance acotado para llegar a tiempo con todos los requisitos obligatorios. |
| 28/10/2026 | Backups y reportes en JSON en lugar de CSV | Autorizado por el profesor. |
| 02/11/26 | Los atributos _nombre_, _apellido_ tanto de los Clientes como de los Huespedes seran _atomicos_. Ej: Solo se ingresara un nombre de cliente y un apellido sea de un Cliente o de un Huesped. | Para simplificar la lógica del sistema con relación a los datos.
| 05/11/26 | Las entidades tendrán un nuevo campo llamado activo | Para usar una Baja logica en vez de una eliminación en la base de datos.

## 11. Lista de pendientes

Marcar con `[x]` lo que esté terminado y probado.

**Documentación y modelado**
- [x] Definición del proceso a modelar
- [x] Narrativa descriptiva
- [x] Flujo: crear una reserva
- [x] Flujo: modificar una reserva
- [x] Flujo: actualizar una reserva
- [x] Flujo: eliminar una reserva
- [x] Diagrama Entidad-Relación (DER)
- [x] Derivación de las tablas ya normalizadas
- [ ] Diagrama de Flujo de Datos (DFD)
- [x] Diagrama de Clases (DCD)
- [ ] Modificar estructura estructura de carpetas para que cumpla la actual
- [x] Definir las capacidades de cada habitacion y formalizarlas en las reglas de negocio
- [x] Modelar Persona
- [x] Modelar Cliente
- [x] Modelar Huesped
- [x] Modelar Habitación
- [x] Modelar Reservas
- [x] Crear las validaciones de cada modelo
- [ ] Documentación Docstring actualizada
- [ ] Documentación de instalación actualizada
- [ ] Testeo actualiizado
- [ ] Bitacora actualzada
- [ ] MODIFICAR EL README POR EL NUEVO CAMPO ACTIVO

**Base de datos**
- [x] Conexión a MySQL
- [x] Crear un servidor en la nube
- [x] Crear las tablas
- [x] Tener en cuenta el UNIQUE en las tablas intermedias
- [x] Cargar datos de prueba
- [x] Configurar variables de entorno.

**Capa DAO (Persistencia)**
- [x] CRUD de Cliente
- [x] CRUD de Huesped
- [x] CRUD de Habitación
- [x] CRUD de Reserva

**Capa de Servicios y Lógica de Negocio**
- [ ] Servicio de Cliente
- [ ] Servicio de Huesped
- [ ] Servicio de Habitación
- [ ] Servicio de Reserva
- [ ] Consulta compleja 1
- [ ] Consulta compleja 2
- [ ] Consulta compleja 3
- [ ] Consulta compleja 4

**Reportes y backups**
- [ ] Reportes en JSON y texto
- [ ] Gráficos con Matplotlib
- [ ] Backup en JSON
- [ ] Restauración desde JSON

**Testeos**

- [ ] Testear modelo persona
- [ ] Testear modelo cliente
- [ ] Testear modelo huesped
- [ ] Testear modelo habitacion
- [ ] Testear modelo reserva
- [x] Testear equipo de sonido
- [x] Testear conexion a base de datos
- [x] Testear patron DAO cliente
- [x] Testear patron DAO huesped
- [x] Testear patron habitacion
- [x] Testear patron reserva
- [ ] Testear servicio cliente
- [ ] Testear servicio huesped
- [ ] Testear servicio habitacion
- [ ] Testear servicio reserva

**GUI**

**Otros**

- [x] Llenar .env.example para tener la un ejemplo documentado
- [x] Logging configurado
- [ ] Logging utilizado completamente
- [ ] Excepciones propias
- [x] Modelos (herencia, polimorfismo, encapsulamiento)

**Cierre**