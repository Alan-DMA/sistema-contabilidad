# ESPECIFICACIONES TÉCNICAS Y DISEÑO DE SOFTWARE (SDD)
## Sistema Contable v1.0

---

### 1. INTRODUCCIÓN Y ALCANCE DEL PROYECTO

#### 1.1. Propósito del Documento
Este Documento de Diseño de Software (SDD) define las especificaciones funcionales, el diseño de datos, la arquitectura lógica y los lineamientos de interfaz para el desarrollo del "Sistema Contable v1.0". 

#### 1.2. Descripción General
La aplicación es un software contable puro de escritorio monolítico. Centraliza las operaciones del ciclo contable desde el asiento inicial hasta la emisión automatizada de Estados Financieros, aplicando un diseño de interfaz de usuario moderno, limpio y minimalista.

#### 1.3. Alcance del Desarrollo
* **Módulos Incluidos (En Alcance - Sistema Contable Puro):**
    * **Login y Roles:** Acceso de seguridad básico discriminando entre Administrador y Operador.
    * **Nuevo Asiento (Registro):** Formulario dinámico para la captura de transacciones con validación matemática en tiempo real.
    * **Reporte de Libro Diario:** Vista independiente de solo lectura para auditar el historial de asientos ordenados cronológicamente.
    * **Libro Mayor:** Motor de consulta para agrupar movimientos y visualizar el historial de saldos por cuenta específica.
    * **Hoja de Trabajo (12 Columnas):** Matriz analítica para verificar comprobación, ajustes, saldos ajustados, resultados y situación financiera.
    * **Estados Financieros:** Reportes formales y jerárquicos (Estado de Resultados de pasos múltiples y Balance General).
    * **Cierre Contable:** Cancelación de cuentas nominales y bloqueo de periodo.
* **Componentes Excluidos (Corrupción de Alcance Rechazada):**
    * Módulos de ERP corporativo (Inventario, Facturación, Nómina, Compras).
    * Botones "fantasma" o módulos inactivos bajo la etiqueta "Próximamente".

---

### 2. REGLAS DE NEGOCIO Y PRINCIPIOS CONTABLES
* **Partida Doble:** Restricción matemática obligatoria.
* **Auditoría Inmutable:** Los errores no se borran, se reversan.
* **Precisión:** Manejo numérico estricto de dos decimales para la moneda local.

---

### 3. ARQUITECTURA DEL SISTEMA
El sistema se divide en 5 archivos principales siguiendo el patrón MVC/Modular:
* `main.py`: Punto de entrada y orquestador.
* `database.py`: Capa de persistencia (SQLite 3).
* `logic.py`: Reglas de negocio, bloqueos y algoritmos de mayorización.
* `ui_main.py`: Contenedor principal, ruteo SPA y Sidebar.
* `ui_views.py`: Componentes gráficos independientes (`LoginView`, `RegistroDiarioView`, `ReporteDiarioView`, `MayorView`, `ReportesView`, `CierreView`).

---

### 4. DISEÑO DE LA INTERFAZ DE USUARIO (GUI)
La aplicación implementa una estética de "Flat Design" inspirada en aplicaciones web modernas, separando el menú de navegación del área de trabajo.

```text
+------------------------------------------------------------------------------------+
|   [C] Conta v1.0           |  Nuevo Asiento Contable                      [🔔][⚙️] |
+============================+=======================================================+
|                            |                                                       |
|   [+] Nuevo Asiento        |  +-------------------------------------------------+  |
|                            |  | Fecha: [ YYYY-MM-DD ]   Concepto: [         ]   |  |
|   [📖] Reporte Diario      |  |                                                 |  |
|                            |  | Cuenta Contable           Debe ($)    Haber ($) |  |
|   [📚] Libro Mayor         |  | ----------------------------------------------- |  |
|                            |  | [ Dropdown Cuenta ]       [ 0.00 ]    [ 0.00 ]  |  |
|   [📊] Reportes            |  |                                                 |  |
|                            |  |               [ + Agregar Fila ]                |  |
|   [🔒] Cierre Contable     |  |                                                 |  |
|                            |  | Totales                   1,000.00    1,000.00  |  |
|                            |  | [ CUADRADO ]             [ GUARDAR ASIENTO ]    |  |
|                            |  +-------------------------------------------------+  |
|   [->] Logout              |                                                       |
+============================+=======================================================+