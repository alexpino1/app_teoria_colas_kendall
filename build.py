# build.py
# Automation script for compiling the Teoría de Colas app using PyInstaller.
# Generates Windows version metadata dynamically from version.py.

import os
import sys
import subprocess

def main():
    print("=" * 60)
    print("Teoría de Colas - Compilador Automatizado (PyInstaller)")
    print("=" * 60)

    # 0. Verificar si el archivo ejecutable de salida está bloqueado (en ejecución)
    output_exe = os.path.join("dist", "teoria_colas_kendall.exe")

    if os.path.exists(output_exe):
        try:
            # Intentar abrir el archivo en modo exclusivo de escritura
            with open(output_exe, "a+b"):
                pass
        except OSError:
            print("\n" + "!" * 70)
            print("ERROR DE ACCESO DENEGADO: El ejecutable de salida está bloqueado.")
            print("Esto ocurre porque la aplicación 'teoria_colas_kendall.exe' está abierta.")
            print("Por favor, cierra la aplicación antes de intentar compilar nuevamente.")
            print("!" * 70 + "\n")
            sys.exit(1)

    # 1. Importar metadatos desde el archivo modular version.py
    try:
        import version
        print(f"Versión detectada: {version.VERSION_STR}")
        print(f"Título del producto: {version.APP_TITLE}")
        print(f"Autor: {version.AUTHOR}")
    except ImportError:
        print("Error: No se pudo importar 'version.py'. Asegúrate de que existe.")
        sys.exit(1)

    # 2. Generar el archivo de información de versión para Windows (VSVersionInfo)
    version_file_path = "file_version_info.txt"
    print(f"Generando metadatos para Windows en '{version_file_path}'...")
    
    # Formato de versión de 4 tuplas
    major, minor, patch = version.VERSION_INFO
    
    version_info_content = f"""# UTF-8
# Archivo de información de versión generado dinámicamente por build.py
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, 0),
    prodvers=({major}, {minor}, {patch}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          '040904b0',
          [
            StringStruct('CompanyName', '{version.AUTHOR}'),
            StringStruct('FileDescription', '{version.APP_DESCRIPTION}'),
            StringStruct('FileVersion', '{version.VERSION_STR}'),
            StringStruct('InternalName', 'teoria_colas_kendall'),
            StringStruct('LegalCopyright', '{version.COPYRIGHT}'),
            StringStruct('OriginalFilename', 'teoria_colas_kendall.exe'),
            StringStruct('ProductName', '{version.APP_TITLE}'),
            StringStruct('ProductVersion', '{version.VERSION_STR}')
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    with open(version_file_path, "w", encoding="utf-8") as f:
        f.write(version_info_content)

    # 3. Construir el comando de PyInstaller
    # Detectar el ejecutable de pyinstaller en el entorno virtual o global
    pyinstaller_bin = os.path.join("venv", "Scripts", "pyinstaller.exe")
    if not os.path.exists(pyinstaller_bin):
        pyinstaller_bin = "pyinstaller"  # fall back to global
        
    print(f"Usando PyInstaller: '{pyinstaller_bin}'")

    cmd = [
        pyinstaller_bin,
        "--onefile",
        "--windowed", # No mostrar consola negra en producción
        f"--version-file={version_file_path}",
        "--name=teoria_colas_kendall"
    ]

    # Detectar dinámicamente si existe un archivo .ico en el directorio raíz
    icon_file = None
    if os.path.exists("app.ico"):
        icon_file = "app.ico"
    else:
        ico_files = [f for f in os.listdir(".") if f.endswith(".ico") and os.path.isfile(f)]
        if ico_files:
            icon_file = ico_files[0]

    if icon_file:
        print(f"Icono detectado: '{icon_file}'. Agregándolo al comando de compilación...")
        cmd.append(f"--icon={icon_file}")
    else:
        print("No se detectó ningún archivo .ico en la raíz. Compilando con el icono por defecto.")

    cmd.append("main.py")

    print("\nEjecutando compilación...")
    print("Comando:", " ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "=" * 60)
        print("¡COMPILACIÓN EXITOSA!")
        print("=" * 60)
        print("El ejecutable se encuentra en: dist/teoria_colas_kendall.exe")
    except subprocess.CalledProcessError as e:
        print(f"\nError en la compilación: {e}")
        sys.exit(1)
    finally:
        # Limpiar archivo de versión
        if os.path.exists(version_file_path):
            os.remove(version_file_path)
            print("Limpieza de archivos temporales completada.")

if __name__ == "__main__":
    main()
