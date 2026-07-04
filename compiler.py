# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import shutil

def run_command(command, shell=False):
    print(f"Ejecutando: {command}")
    res = subprocess.run(command, shell=shell)
    if res.returncode != 0:
        print(f"Error al ejecutar el comando (código de salida: {res.returncode})")
        sys.exit(res.returncode)

def main():
    print("--- INICIANDO PROCESO DE COMPILACIÓN DE AURABOOKS ---")
    
    # 1. Asegurar la instalación de PyInstaller en el entorno virtual
    print("\n1. Instalando/Actualizando PyInstaller en el entorno virtual...")
    pip_path = os.path.join(".venv", "Scripts", "pip.exe")
    if not os.path.exists(pip_path):
        print(f"Error: No se encontró el ejecutable pip en {pip_path}")
        sys.exit(1)
    run_command([pip_path, "install", "pyinstaller"])
    
    # 2. Compilar la aplicación con PyInstaller
    print("\n2. Compilando aplicación con PyInstaller...")
    pyinstaller_path = os.path.join(".venv", "Scripts", "pyinstaller.exe")
    
    # Eliminar carpetas previas para asegurar una compilación limpia
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            print(f"Limpiando carpeta de compilación previa: {folder}")
            shutil.rmtree(folder, ignore_errors=True)

    # Comando de PyInstaller:
    # --name AuraBooks: nombre del ejecutable
    # --noconfirm: sobrescribe archivos existentes sin preguntar
    # --onedir: empaqueta en una sola carpeta distribuible (ideal para instaladores)
    # --windowed: oculta la ventana negra de consola al arrancar la app
    # --clean: limpia la caché de compilaciones previas para evitar reutilizar dependencias incompletas
    # --add-data "logo.png;..": copia el archivo logo.png a la raíz del paquete compilado
    build_cmd = [
        pyinstaller_path,
        "--name", "AuraBooks",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--clean",
        "--add-data", "logo.png;.",
        "main.py"
    ]
    
    # Configurar las variables de entorno necesarias para la localización de Tcl/Tk y PythonHome
    # debido a la instalación fragmentada de Python 3.14 en el sistema.
    os.environ["PYTHONHOME"] = r"C:\Users\aland\AppData\Local\Programs\Python\Python314"
    os.environ["TCL_LIBRARY"] = r"C:\Users\aland\AppData\Local\Programs\Python\Python314\tcl\tcl8.6"
    os.environ["TK_LIBRARY"] = r"C:\Users\aland\AppData\Local\Programs\Python\Python314\tcl\tk8.6"
    
    run_command(build_cmd)
    print("Compilación con PyInstaller finalizada con éxito.")
    
    # 3. Detectar e instalar Inno Setup si no está presente
    print("\n3. Localizando compilador de Inno Setup (ISCC.exe)...")
    iscc_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe"
    ]
    
    iscc_executable = None
    for path in iscc_paths:
        if os.path.exists(path):
            iscc_executable = path
            break
            
    if not iscc_executable:
        # Buscar en el PATH del sistema
        iscc_executable = shutil.which("ISCC")
        
    if not iscc_executable:
        print("Inno Setup no detectado. Intentando instalar mediante Chocolatey...")
        # Intentar instalar Inno Setup vía Chocolatey (requiere privilegios de administrador)
        try:
            # Comando choco install
            run_command(["choco", "install", "innosetup", "-y"], shell=True)
            # Reintentar la búsqueda en la ruta por defecto tras la instalación
            for path in iscc_paths:
                if os.path.exists(path):
                    iscc_executable = path
                    break
            if not iscc_executable:
                iscc_executable = shutil.which("ISCC")
        except Exception as e:
            print("No se pudo instalar Inno Setup automáticamente:", e)
            
    if not iscc_executable:
        print("\n[!] ERROR: No se encontró Inno Setup (ISCC.exe).")
        print("Por favor instálalo manualmente desde: https://jrsoftware.org/isdownload.php")
        print("Una vez instalado, vuelve a correr este script o compila 'installer.iss' en Inno Setup.")
        sys.exit(1)
        
    print(f"Compilador de Inno Setup localizado en: {iscc_executable}")
    
    # 4. Generar el instalador ejecutable final
    print("\n4. Generando instalador de Windows (AuraBooks_Setup.exe)...")
    run_command([iscc_executable, "installer.iss"])
    
    setup_path = os.path.abspath(os.path.join("Output", "AuraBooks_Setup.exe"))
    print("\n-------------------------------------------------------------")
    print("¡PROCESO FINALIZADO CON ÉXITO!")
    print(f"El instalador de Windows está listo en: {setup_path}")
    print("-------------------------------------------------------------")

if __name__ == "__main__":
    main()
