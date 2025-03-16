from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget
from ui.session_window import SessionModeWindow
from ui.storage_window import StorageWindow
from ui.collection_window import CollectionsWindow
from ui.fixed_window import FixedTimeModeWindow

class ImageTimerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Timer Player")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
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
            QLabel {
                color: #ECEFF4;
                font-size: 16px;
            }
            QLineEdit {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QSplitter::handle {
                background-color: #4C566A;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.btn_storage = QPushButton("Manage Storage")
        self.btn_storage.clicked.connect(self.on_storage_button_clicked) 
        
        self.btn_collections = QPushButton("Manage Collections")
        self.btn_collections.clicked.connect(self.on_collection_button_clicked)

        self.btn_fixed_time = QPushButton("Fixed-Time Mode")
        self.btn_fixed_time.clicked.connect(self.on_fixed_button_clicked)

        self.btn_session_mode = QPushButton("Session Mode")
        self.btn_session_mode.clicked.connect(self.on_session_button_clicked)

        layout.addWidget(self.btn_storage)
        layout.addWidget(self.btn_collections)
        layout.addWidget(self.btn_fixed_time)
        layout.addWidget(self.btn_session_mode)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def on_storage_button_clicked(self):
        self.storage_window = StorageWindow()
        self.storage_window.show()
        
    def on_collection_button_clicked(self):
        self.collections_window = CollectionsWindow()
        self.collections_window.show()
        
    def on_fixed_button_clicked(self):
        """Open the fixed-time mode configuration window."""
        self.fixed_time_window = FixedTimeModeWindow()
        self.fixed_time_window.show()
    
    def on_session_button_clicked(self):
        self.session_window = SessionModeWindow()
        self.session_window.show()