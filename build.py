# build.py
# Automation script for compiling the Teoría de Colas app using PyInstaller.
# Generates Windows version metadata dynamically from version.py.
# Highly robust path resolution and environment checking.

import os
import sys
import subprocess

def main():
    print("=" * 60)
    print("Teoría de Colas - Compilador Automatizado (PyInstaller)")
    print("=" * 60)

    # Obtener el directorio base de forma absoluta para robustez de ejecución
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Asegurar que el directorio raíz del proyecto esté en sys.path para importar version
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    # 0. Verificar si el archivo ejecutable de salida está bloqueado (en ejecución)
    output_exe = os.path.join(base_dir, "dist", "teoria_colas_kendall.exe")

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
    version_file_path = os.path.join(base_dir, "file_version_info.txt")
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

    # 3. Detectar y seleccionar el entorno de ejecución
    # Buscar carpetas de entorno virtual comunes en el directorio base
    venv_dirs = [".venv", "venv"]
    venv_python = None
    
    for venv_dir in venv_dirs:
        # En Windows, python.exe está en Scripts/
        path = os.path.join(base_dir, venv_dir, "Scripts", "python.exe")
        if os.path.exists(path):
            venv_python = path
            break
            
    # Determinar qué intérprete de Python usar
    if sys.prefix != sys.base_prefix:
        # Ya estamos ejecutando dentro de un entorno virtual activo
        active_python = sys.executable
    elif venv_python:
        # No estamos en un entorno virtual activo, pero detectamos uno local
        active_python = venv_python
    else:
        # Fallback a la instalación de Python global actual
        active_python = sys.executable

    print(f"Intérprete de Python seleccionado: '{active_python}'")

    # 4. Validar dependencias clave requeridas para compilar e iniciar la app
    dependencies = ["PyQt6", "matplotlib", "numpy", "PyInstaller"]
    missing_deps = []
    
    for dep in dependencies:
        try:
            # Ejecutar importación silenciosa de prueba
            subprocess.run([active_python, "-c", f"import {dep}"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_deps.append(dep)
            
    if missing_deps:
        print("\n" + "!" * 70)
        print("ADVERTENCIA DE DEPENDENCIAS FALTANTES:")
        print(f"No se pudieron importar los siguientes paquetes en el entorno: {', '.join(missing_deps)}")
        print("La compilación podría fallar o el ejecutable podría cerrarse al iniciarse.")
        print("Sugerencia: Ejecuta el siguiente comando para instalar todas las dependencias:")
        print(f"  {os.path.basename(active_python)} -m pip install -r requirements.txt")
        print("!" * 70 + "\n")
        
    # 5. Construir el comando de PyInstaller
    # Intentamos usar el módulo PyInstaller directo del entorno seleccionado si está disponible
    if "PyInstaller" not in missing_deps:
        cmd = [active_python, "-m", "PyInstaller"]
    else:
        # Fallback a buscar el ejecutable de PyInstaller directamente
        pyinstaller_bin = None
        # Buscar en Scripts/ del entorno virtual detectado
        for venv_dir in venv_dirs:
            path = os.path.join(base_dir, venv_dir, "Scripts", "pyinstaller.exe")
            if os.path.exists(path):
                pyinstaller_bin = path
                break
        if not pyinstaller_bin:
            pyinstaller_bin = "pyinstaller" # Fallback global
        cmd = [pyinstaller_bin]

    # Agregar argumentos estándar de PyInstaller
    cmd.extend([
        "--onefile",
        "--windowed", # No mostrar consola negra en producción
        f"--version-file={version_file_path}",
        "--name=teoria_colas_kendall"
    ])

    # Agregar la carpeta de assets para empaquetar recursos dentro del .exe
    assets_src = os.path.join(base_dir, "assets")
    if os.path.exists(assets_src):
        cmd.append(f"--add-data={assets_src};assets")


    # Detectar dinámicamente si existe un archivo .ico en el directorio raíz o en assets
    icon_file = None
    ico_candidates = [
        os.path.join(base_dir, "app.ico"),
        os.path.join(base_dir, "assets", "app.ico")
    ]
    for candidate in ico_candidates:
        if os.path.exists(candidate):
            icon_file = candidate
            break
            
    if not icon_file:
        # Buscar cualquier otro archivo .ico en la raíz
        try:
            ico_files = [os.path.join(base_dir, f) for f in os.listdir(base_dir) if f.endswith(".ico")]
            if ico_files:
                icon_file = ico_files[0]
        except OSError:
            pass

    if icon_file:
        print(f"Icono detectado: '{icon_file}'. Agregándolo al comando de compilación...")
        cmd.append(f"--icon={icon_file}")
    else:
        print("No se detectó ningún archivo .ico. Compilando con el icono por defecto.")

    # Añadir archivo principal resolviendo ruta absoluta
    cmd.append(os.path.join(base_dir, "main.py"))

    print("\nEjecutando compilación...")
    print("Comando:", " ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "=" * 60)
        print("¡COMPILACIÓN EXITOSA!")
        print("=" * 60)
        print(f"El ejecutable se encuentra en: {os.path.join(base_dir, 'dist', 'teoria_colas_kendall.exe')}")
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
