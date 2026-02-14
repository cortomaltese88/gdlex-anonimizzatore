from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from gdlex_anonimizzatore.ui.main_window import MainWindow, apply_dark_theme


def main() -> None:
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
