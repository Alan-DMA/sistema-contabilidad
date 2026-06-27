# CONSTITUCIÓN DEL PROYECTO
## Reglas de Desarrollo e Interacción con IA (Antigravity Rules)

Este documento establece las directrices tecnológicas, arquitectónicas y de desarrollo inquebrantables para el **Sistema Contable v1.0**. Cualquier Agente de IA o desarrollador que opere en este repositorio debe respetar de forma estricta y sin excepciones cada uno de los siguientes artículos.

---

### ARTÍCULO 1: STACK TECNOLÓGICO Y ENTORNO
* **Lenguaje Base:** Python 3 (compatible con entornos Windows, Linux Debian/Pop!_OS/ChromeOS Crostini).
* **Codificación de Archivos:** Todos los archivos de código fuente Python (`.py`) deben guardarse obligatoriamente en formato `UTF-8` e incluir como primera línea la declaración explícita `# -*- coding: utf-8 -*-` para evitar "mojibake" en caracteres latinos.
* **Librería Gráfica:** `customtkinter` (importada estrictamente como `import customtkinter as ctk`).
* **Base de Datos:** SQLite 3 nativo mediante un único archivo local denominado `contabilidad.db` ubicado en el directorio raíz.
* **Restricción de Red:** El sistema debe ser 100% autónomo y funcional en modo *offline*. Queda estrictamente prohibido el uso de librerías de terceros que requieran conexión a internet, servicios en la nube o API externas.

---

### ARTÍCULO 2: FILOSOFÍA Y REGLAS DE DISEÑO DE INTERFAZ (GUI)
* **Prohibición de Layout:** Queda terminantemente prohibido el uso del gestor de geometría `.pack()` para el posicionamiento de componentes principales. Toda la interfaz debe estructurarse mediante `.grid()`.
* **Diseño Responsivo:** Cada contenedor o marco (`CTkFrame`) debe implementar explícitamente `grid_rowconfigure` y `grid_columnconfigure` asignando pesos (`weight`) para que la interfaz se estire de forma fluida.
* **Estilo Visual Moderno (Flat Design):** * El sistema abandona la estética heredada y adopta un diseño minimalista.
    * Modo de apariencia fijado permanentemente en claro: `ctk.set_appearance_mode("light")`.
    * **Paleta estricta:** Fondos de aplicación gris muy claro (`#F8FAFC`), contenedores/tarjetas en blanco puro (`#FFFFFF`) con bordes redondeados (`corner_radius=8`).
    * **Color de Acento:** Verde Esmeralda (`#10B981`) para botones primarios y acciones de éxito. Rojo suave (`#EF4444`) para cierres o acciones destructivas.
    * **Prohibición de 3D:** Quedan prohibidos los bordes con relieve, gradientes o aspecto de "Visual Basic clásico".
* **Navegación (Single-Page Application):** El menú lateral izquierdo es fijo. Las vistas cambian en el lienzo derecho limpiamente destruyendo o cambiando la visibilidad de los marcos, sin abrir ventanas emergentes (`CTkToplevel`).

---

### ARTÍCULO 3: INTEGRIDAD Y LÓGICA DE NEGOCIO (BACKEND)
* **Regla de Oro Contable:** El sistema jamás debe autorizar una sentencia `INSERT` en la tabla `detalle_asientos` si la sumatoria del debe no es exactamente igual a la del haber ($\sum \text{Debe} = \sum \text{Haber}$). Se debe aplicar redondeo estricto a 2 decimales para evitar fallos de punto flotante.
* **Separación de Responsabilidades:** La captura de datos (Nuevo Asiento) y la lectura histórica (Reporte de Diario) deben existir en módulos visuales y lógicos separados.
* **Inmutabilidad y Reverso:** Queda prohibido el borrado físico (`DELETE`) de asientos ya guardados. Para corregir errores, el sistema debe implementar una lógica de **Asiento de Reverso** que anule la transacción original invirtiendo las cuentas, manteniendo intacta la pista de auditoría.
* **Cierre Contable y Bloqueo:** El asiento automático de cierre debe aislar el resultado en "Utilidad del Ejercicio" o "Pérdida del Ejercicio", jamás tocando el "Capital Social" general. Al ejecutarse, debe activar un **bloqueo estricto por fecha**, impidiendo el registro de nuevos asientos en periodos cerrados.

---

### ARTÍCULO 4: PROTOCOLO DE INTERACCIÓN CON EL AGENTE DE IA
* **Lectura Obligatoria de Contexto:** Antes de generar código, el Agente debe validar el archivo `@ESPECIFICACIONES.md` para asimilar el alcance y la estructura visual.
* **Prohibición de Código Incompleto:** El Agente no debe omitir lógica con comentarios como `# Aquí va tu código anterior`. Debe entregar los bloques funcionales estructurados o indicar con precisión dónde insertar la modificación.