# ESPECIFICACIONES TÉCNICAS Y DISEÑO DE SOFTWARE (SDD)
## Sistema Contable v1.0

---

### 1. INTRODUCCIÓN Y ALCANCE DEL PROYECTO

#### 1.1. Propósito del Documento
Este Documento de Diseño de Software (SDD) define las especificaciones funcionales, el diseño de datos, la arquitectura lógica y los lineamientos de interfaz para el desarrollo del "Sistema Contable v1.0". Funciona como la documentación técnica de referencia para el equipo de desarrollo y certifica el cumplimiento de los requerimientos académicos evaluados por la cátedra de las profesoras Elsy e Yancelis.

#### 1.2. Descripción General
La aplicación es un sistema de escritorio monolítico local diseñado para registrar, procesar y consolidar transacciones financieras bajo el método de partida doble. Centraliza las operaciones del ciclo contable desde el asiento inicial en el Libro Diario hasta la emisión automatizada de Estados Financieros definitivos.

#### 1.3. Alcance del Desarrollo
* **Módulos Incluidos (En Alcance):**
    * **Registro Cronológico:** Formulario dinámico para la inserción de asientos en el Libro Diario con control estricto de balance.
    * **Mayorización Automatizada:** Motor de consulta que procesa el historial transaccional para agrupar movimientos y generar los saldos del Libro Mayor.
    * **Balance de Comprobación:** Vista analítica para verificar la integridad de los saldos deudores y acreedores.
    * **Ajustes y Cierre Contable:** Interfaz especializada para ejecutar la cancelación automática de cuentas nominales (Ingresos y Egresos) y determinar la utilidad o pérdida del ejercicio.
    * **Estados Financieros:** Generación de reportes estructurados listos para visualización: Balance General (Estado de Situación Financiera) y Estado de Resultados.
    * **Operación Local:** Funcionamiento totalmente desconectado (Offline), asegurando portabilidad e independencia de red.
* **Componentes Excluidos (Fuera de Alcance):**
    * Multiusuario, login administrativo complejo o roles distribuidos.
    * Conexión con impresoras fiscales, facturación electrónica o cálculo automatizado de tributos nacionales.
    * Sincronización automática con servidores en la nube.

---

### 2. REGLAS DE NEGOCIO Y PRINCIPIOS CONTABLES

El núcleo lógico de la aplicación (Backend) valida de forma obligatoria los siguientes principios:

* **Equidad:** Los datos se procesan de manera neutral y objetiva sin alteraciones.
* **Entidad Contable:** La base de datos asume que el patrimonio de la entidad jurídica está separado de los fondos personales de los socios.
* **Moneda Común:** Todos los valores numéricos se homogeneizan bajo una única unidad monetaria local con precisión estricta de dos decimales.
* **Ejercicio Económico:** Cada transacción incluye una fecha (`YYYY-MM-DD`), delimitando de forma precisa los registros para permitir cierres mensuales o anuales aislados.
* **Devengado:** Los ingresos y gastos se reconocen y asientan en la fecha de su ocurrencia económica, independientemente de la fecha efectiva del flujo de caja.
* **Partida Doble:** Restricción matemática de control primario. Ningún asiento puede consolidarse si la suma de los débitos no es igual a la suma de los créditos.

---

### 3. ARQUITECTURA DEL SISTEMA

El sistema se estructura bajo una arquitectura monolítica local dividida en tres capas funcionales:

* **Capa de Presentación (Frontend):** Construida con `customtkinter`. Gestiona el renderizado de los componentes gráficos, formularios de captura y la actualización interactiva de los reportes en pantalla.
* **Capa de Lógica (Backend):** Desarrollada nativamente en `Python 3`. Centraliza el procesamiento matemático, los algoritmos de mayorización y la ejecución del script de cierre.
* **Capa de Datos (Persistencia):** Administrada mediante el motor relacional local `SQLite 3` embebido en un único archivo físico llamado `contabilidad.db`.
* **Estructura de Archivos:** El proyecto adoptará una estructura modular organizada en distintos archivos con nombres fáciles de comprender (ej. `main.py`, `base_datos.py`, `interfaz.py`) manteniendo su naturaleza de sistema de escritorio local.

---

### 4. DISEÑO Y DICCIONARIO DE DATOS

Para garantizar un copiado limpio en entornos de desarrollo y evitar errores de tabulación, la base de datos relacional se describe bajo una estructura de lista técnica estructurada:

#### Entidad 1: `cuentas` (Catálogo de Cuentas)
* **Población Inicial:** Al crear la base de datos, el sistema inyectará automáticamente un catálogo de cuentas base (Caja, Banco, Cuentas por Pagar, Capital Social, etc.) para acelerar la implementación.
* **`id`** [Tipo: INTEGER]: Clave Primaria. Autoincremental. Identificador único de control interno.
* **`codigo`** [Tipo: VARCHAR]: Restricción: Único, No Nulo. Código numérico indexado (Ej: "1.1.01" para Caja Chica).
* **`nombre`** [Tipo: VARCHAR]: Restricción: No Nulo. Denominación formal de la cuenta (Ej: "Banco Central").
* **`tipo`** [Tipo: VARCHAR]: Restricción: No Nulo. Clasificación de la cuenta (Valores permitidos: Activo, Pasivo, Capital, Ingreso, Egreso).

#### Entidad 2: `asientos` (Cabecera del Libro Diario)
* **`id`** [Tipo: INTEGER]: Clave Primaria. Autoincremental. Número correlativo único del hecho contable.
* **`fecha`** [Tipo: DATE]: Restricción: No Nulo. Fecha de registro con formato estricto `AAAA-MM-DD`.
* **`descripcion`** [Tipo: VARCHAR]: Restricción: No Nulo. Glosa descriptiva general que justifica la operación.

#### Entidad 3: `detalle_asientos` (Cuerpo de Transacciones)
* **`id`** [Tipo: INTEGER]: Clave Primaria. Autoincremental. Identificador de la línea transaccional.
* **`asiento_id`** [Tipo: INTEGER]: Clave Foránea. Vincula directamente la línea con el número de control en la tabla `asientos`.
* **`cuenta_id`** [Tipo: INTEGER]: Clave Foránea. Vincula la línea con el identificador del catálogo en la tabla `cuentas`.
* **`debe`** [Tipo: DECIMAL]: Restricción: Valor mínimo 0.00. Monto debitado o cargado a la cuenta.
* **`haber`** [Tipo: DECIMAL]: Restricción: Valor mínimo 0.00. Monto acreditado o abonado a la cuenta.

---

### 5. DISEÑO DE LA INTERFAZ DE USUARIO (GUI)

La aplicación implementa una arquitectura visual de Panel Único (Single-Page Application). El menú lateral permanece fijo en la zona izquierda controlling la carga dinámica de vistas en el lienzo de trabajo derecho.

```text
+------------------------------------------------------------------------------------+
|  SISTEMA CONTABLE v1.0                                                     [-][X]  |
+====================+===============================================================+
|                    |                                                               |
|   MENÚ PRINCIPAL   |   NUEVO ASIENTO - LIBRO DIARIO                                |
|  ----------------  |  -----------------------------------------------------------  |
|                    |                                                               |
|  [ Inicio        ] |   Fecha: [ YYYY-MM-DD ]   Concepto: [ Descripción general ]   |
|                    |                                                               |
|  [ Libro Diario  ] |   +-------------------------------------------------------+   |
|   <-- (Activo)     |   | Cód  | Cuenta de Movimiento    | Debe ($)  | Haber ($)|   |
|                    |   |------+-------------------------+-----------+----------|   |
|  [ Libro Mayor   ] |   |      |                         |           |          |   |
|                    |   +-------------------------------------------------------+   |
|  [ Estados Fin.  ] |                                                               |
|                    |   [ + Agregar línea ]                   [ - Eliminar línea ]  |
|  [ Cierre        ] |                                                               |
|                    |   TOTALES:            [ Debe: 0.00 ]     [ Haber: 0.00 ]      |
|                    |   Estado: [ INDICADOR DE CUADRE ]                             |
|                    |                                   [ GUARDAR EN BASE DE DATOS ]|
+====================+===============================================================+

---

### 6. LÓGICA CORE Y ALGORITMOS

### 6.1. Validación de Equilibrio Financiero

Previo al guardado de cualquier operación, el backend ejecuta un ciclo de control sobre el lote transaccional. La persistencia de datos se bloquea de forma absoluta si el resultado neto de la siguiente ecuación difiere de cero:

$$\sum \text{Debe} - \sum \text{Haber} = 0$$

### 6.2. Mayorización Dinámica en Memoria

Los saldos de los reportes se calculan acumulando cronológicamente los registros históricos. El algoritmo aplica operaciones aritméticas basándose estrictamente en el tipo de cuenta:

* **Cuentas Deudoras** (Activos y Egresos): Saldo Neto = Sumatoria Debe - Sumatoria Haber.
* **Cuentas Acreedoras** (Pasivos, Capital e Ingresos): Saldo Neto = Sumatoria Haber - Sumatoria Debe.

### 6.3. Script de Cierre Contable Automatizado

Al dispararse el cierre del ejercicio, el backend realiza de forma atómica:

1. Consulta y consolidación de saldos de todas las cuentas con tipo "Ingreso" o "Egreso".
2. Determinación de la utilidad o pérdida del ejercicio por diferencia simple.
3. Inyección automática de un asiento de cierre en el Libro Diario para cargar los Ingresos por su saldo, abonar los Egresos por su saldo (dejando ambas naturalezas en cero) y transferir la diferencia resultante sumándola o restándola directamente a la cuenta de **Capital Social**.
