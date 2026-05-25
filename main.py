import sys
from PyQt6.QtWidgets import QApplication
from src.ui.app import App

if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(qapp.exec())
