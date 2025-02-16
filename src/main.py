from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QListWidget
from storage import init_db

import sys
import sqlite3
import os


# Main application class
class ImageTimerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Timer Player")
        self.setGeometry(100, 100, 800, 600)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Buttons for navigation
        self.btn_storage = QPushButton("Manage Storage")
        self.btn_storage.clicked.connect(self.manage_storage)
        
        self.btn_collections = QPushButton("Manage Collections")
        self.btn_fixed_time = QPushButton("Fixed-Time Mode")
        self.btn_session_mode = QPushButton("Session Mode")
        
        # Add buttons to layout
        layout.addWidget(self.btn_storage)
        layout.addWidget(self.btn_collections)
        layout.addWidget(self.btn_fixed_time)
        layout.addWidget(self.btn_session_mode)
        
        # Set main widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def manage_storage(self):
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.gif *.webp)", options=options)
        
        if file_paths:
            conn = sqlite3.connect("image_timer.db")
            cursor = conn.cursor()
            
            for path in file_paths:
                cursor.execute("INSERT INTO images (path, collection) VALUES (?, ?)", (path, "Uncategorized"))
            
            conn.commit()
            conn.close()

# Run application
if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    window = ImageTimerApp()
    window.show()
    sys.exit(app.exec())
