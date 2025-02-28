from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QHBoxLayout, QSplitter, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap
import sqlite3

class StorageWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Storage")
        self.setGeometry(150, 150, 800, 600)
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
            QLabel {
                color: #ECEFF4;
                font-size: 16px;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        splitter = QSplitter()

        # Left panel: List of images with thumbnails
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(64, 64))
        self.image_list.itemClicked.connect(self.on_image_selected)
        self.load_images()
        left_layout.addWidget(self.image_list)

        btn_add_images = QPushButton("Add Images")
        btn_add_images.clicked.connect(self.add_images)
        left_layout.addWidget(btn_add_images)

        btn_delete_image = QPushButton("Delete Selected Image")
        btn_delete_image.clicked.connect(self.delete_selected_image)
        left_layout.addWidget(btn_delete_image)

        left_panel.setLayout(left_layout)

        # Right panel: Image preview
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        self.preview_label = QLabel("Preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid black;")
        right_layout.addWidget(self.preview_label)

        right_panel.setLayout(right_layout)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def on_image_selected(self, item):
        image_path = item.text().split(": ")[1]
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # Set a fixed size for the preview label
            self.preview_label.setFixedSize(200, 200)  # Adjust the size as needed
            # Scale the image to fit the fixed size
            scaled_pixmap = pixmap.scaled(
                self.preview_label.size(),
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
        else:
            self.preview_label.setText("Failed to load image.")
            
    def load_images(self):
        self.image_list.clear()
        conn = sqlite3.connect("image_timer.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, path FROM images")
        images = cursor.fetchall()
        conn.close()
        for img in images:
            item = QListWidgetItem(f"{img[0]}: {img[1]}")
            self.image_list.addItem(item)

    def add_images(self):
        options = QFileDialog.Option.DontUseNativeDialog
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.gif *.webp)", options=options)
        
        if file_paths:
            conn = sqlite3.connect("image_timer.db")
            cursor = conn.cursor()
            for path in file_paths:
                cursor.execute("INSERT INTO images (path, collection) VALUES (?, ?)", (path, "Uncategorized"))
            conn.commit()
            conn.close()
            self.load_images()

    def delete_selected_image(self):
        selected_item = self.image_list.currentItem()
        if selected_item:
            image_id = selected_item.text().split(":")[0]
            conn = sqlite3.connect("image_timer.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM images WHERE id = ?", (image_id,))
            conn.commit()
            conn.close()
            self.load_images()