; Inno Setup Script para compilar el instalador de AuraBooks v1.5
; Define los parámetros del instalador, los archivos a copiar y los accesos directos.

[Setup]
AppName=AuraBooks
AppVersion=1.5
AppPublisher=Alan DMA
DefaultDirName={pf}\AuraBooks
DefaultGroupName=AuraBooks
UninstallDisplayIcon={app}\AuraBooks.exe
OutputDir=Output
OutputBaseFilename=AuraBooks_Setup
Compression=lzma2
SolidCompression=yes
DisableProgramGroupPage=yes

[Files]
; Copiar todo el contenido de la carpeta compilada por PyInstaller
Source: "dist\AuraBooks\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
; Crear accesos directos en el menú de inicio y en el escritorio
Name: "{group}\AuraBooks"; Filename: "{app}\AuraBooks.exe"
Name: "{commondesktop}\AuraBooks"; Filename: "{app}\AuraBooks.exe"

[Run]
; Opción para ejecutar la aplicación inmediatamente al finalizar la instalación
Filename: "{app}\AuraBooks.exe"; Description: "Ejecutar AuraBooks v1.5"; Flags: postinstall nowait skipifsilent
