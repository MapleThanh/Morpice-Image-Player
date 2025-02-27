from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QLineEdit, QMessageBox
import sqlite3

class CollectionsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Collections")
        self.setGeometry(150, 150, 400, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #2E3440;
            }
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
            QListWidget {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #5E81AC;
                color: #ECEFF4;
            }
            QLineEdit {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.collection_list = QListWidget()
        self.load_collections()
        layout.addWidget(self.collection_list)
        
        self.new_collection_name = QLineEdit()
        self.new_collection_name.setPlaceholderText("New Collection Name")
        layout.addWidget(self.new_collection_name)
        
        btn_add_collection = QPushButton("Add Collection")
        btn_add_collection.clicked.connect(self.add_collection)
        layout.addWidget(btn_add_collection)
        
        self.setLayout(layout)

    def load_collections(self):
        self.collection_list.clear()
        conn = sqlite3.connect("image_timer.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM collections")
        collections = cursor.fetchall()
        conn.close()
        for name in collections:
            self.collection_list.addItem(name[0])
    
    def add_collection(self):
        name = self.new_collection_name.text().strip()
        if name:
            conn = sqlite3.connect("image_timer.db")
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO collections (name) VALUES (?)", (name,))
                conn.commit()
                self.new_collection_name.clear()
                self.load_collections()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", "Collection name already exists.")
            conn.close()