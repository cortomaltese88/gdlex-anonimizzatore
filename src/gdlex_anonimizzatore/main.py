from PySide6.QtWidgets import QApplication, QLabel
import sys


def main():
    app = QApplication(sys.argv)
    label = QLabel("GDLEX Anonimizzatore v0.1")
    label.resize(400, 100)
    label.show()
    sys.exit(app.exec())
