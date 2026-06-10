# CONSTITUCIÓN DEL PROYECTO
## Reglas de Desarrollo e Interacción con IA (Antigravity Rules)

Este documento establece las directrices tecnológicas, arquitectónicas y de desarrollo inquebrantables para el **Sistema Contable v1.0**. Cualquier Agente de IA o desarrollador que opere en este repositorio debe respetar de forma estricta y sin excepciones cada uno de los siguientes artículos.

---

### ARTÍCULO 1: STACK TECNOLÓGICO Y ENTORNO
* **Lenguaje Base:** Python 3 (compatible con entornos windows,Linux Debian/Pop!_OS/ChromeOS Crostini).
* **Librería Gráfica:** `customtkinter` (importada estrictamente como `import customtkinter as ctk`).
* **Base de Datos:** SQLite 3 nativo mediante un único archivo local denominado `contabilidad.db` ubicado en el directorio raíz.
* **Restricción de Red:** El sistema debe ser 100% autónomo y funcional en modo *offline*. Queda estrictamente prohibido el uso de librerías de terceros que requieran conexión a internet, servicios en la nube o API externas.

---

### ARTÍCULO 2: FILOSOFÍA Y REGLAS DE DISEÑO DE INTERFAZ (GUI)
* **Prohibición de Layout:** Queda terminantemente prohibido el uso del gestor de geometría `.pack()` para el posicionamiento de componentes principales. Toda la interfaz debe estructurarse mediante `.grid()`.
* **Diseño Responsivo:** Cada contenedor o marco (`CTkFrame`) debe implementar explícitamente `grid_rowconfigure` y `grid_columnconfigure` asignando pesos (`weight`) para garantizar que la interfaz se estire y adapte de forma fluida a cualquier resolución de pantalla.
* **Paradigma de Código:** Toda ventana o módulo debe estar programado bajo el paradigma de Programación Orientada a Objetos (POO), heredando de las clases base de CustomTkinter (ej. `class SistemaContableGUI(ctk.CTk):` o `class ModuloDiario(ctk.CTkFrame):`). Además, el código debe dividirse de forma modular en distintos archivos con nombres fáciles de comprender (ej. `base_datos.py`, `main.py`, `interfaz.py`).
* **Estilo Visual:** * Modo de apariencia fijado permanentemente en oscuro: `ctk.set_appearance_mode("dark")`.
    * Tema de color oficial: `ctk.set_default_color_theme("green")`.
    * Tipografía base unificada: "Roboto" o "Arial" sans-serif.
* **Navegación:** Se debe implementar una arquitectura de Panel Único (Single-Page Application). Está prohibido abusar de las ventanas emergentes flotantes (`CTkToplevel`); los módulos se intercambiarán limpiamente destruyendo o cambiando la visibilidad de los marcos dentro del área de trabajo principal.

---

### ARTÍCULO 3: INTEGRIDAD Y LÓGICA DE NEGOCIO (BACKEND)
* **Regla de Oro Contable:** El sistema jamás debe autorizar una sentencia `INSERT` o `UPDATE` en la tabla `detalle_asientos` si la sumatoria de la columna `debe` no es exactamente igual a la sumatoria de la columna `haber` ($\sum 	ext{Debe} = \sum 	ext{Haber}$).
* **Validación Preventiva:** Antes de ejecutar cualquier transacción en la base de datos, el backend debe validar matemáticamente los tipos de datos (evitar nulos, textos en campos numéricos o montos negativos).
* **Semántica de Colores:** Los indicadores visuales de balance deben interactuar con el usuario. Si un asiento está descuadrado, el indicador debe tornarse rojo y el botón de guardado debe deshabilitarse. Al cuadrar, pasará a verde o azul y se habilitará la acción.
* **Autoconfiguración Inicial:** Es obligatorio que el sistema inyecte un catálogo de cuentas base de forma automática al inicializar la base de datos.
* **Cierre Contable:** El asiento automático de cierre debe afectar directamente sumando o restando el resultado a la cuenta "Capital Social", cuidando de no afectar la coherencia de reportes futuros.

---

### ARTÍCULO 4: PROTOCOLO DE INTERACCIÓN CON EL AGENTE DE IA
* **Lectura Obligatoria de Contexto:** Antes de generar código, el Agente debe validar el archivo `@ESPECIFICACIONES.md` para asimilar el alcance, el diccionario de datos y los módulos requeridos.
* **Prohibición de Código Incompleto:** Al generar soluciones o componentes, el Agente no debe omitir lógica crítica con comentarios del tipo `# Aquí va tu código anterior`. Se deben entregar los bloques funcionales estructurados o indicar con precisión milimétrica dónde insertar la modificación.
* **Fase de Clarificación:** Si una instrucción del desarrollador entra en conflicto con esta Constitución o las Especificaciones, el Agente tiene la obligación de detenerse y realizar un proceso de clarificación de tres preguntas como máximo antes de proceder a la escritura de archivos.
CONSTITUCION.md
Mostrando CONSTITUCION.md.