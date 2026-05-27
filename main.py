import sys
from PyQt6.QtWidgets import QApplication
from src.ui.app import App

if __name__ == "__main__":
    # Evitar que Windows agrupe el proceso bajo python.exe en la barra de tareas
    try:
        import ctypes
        myappid = "malumalovers.teoriacolas.kendall.1.0.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    qapp = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(qapp.exec())

