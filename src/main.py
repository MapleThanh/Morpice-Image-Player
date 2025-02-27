import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import ImageTimerApp
from storage import init_db

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    window = ImageTimerApp()
    window.show()
    sys.exit(app.exec())