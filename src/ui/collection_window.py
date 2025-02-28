from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLineEdit, QMessageBox, QHBoxLayout, QDialog, QLabel, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
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

        # List of collections
        self.collection_list = QListWidget()
        self.collection_list.itemClicked.connect(self.on_collection_selected)
        self.load_collections()
        layout.addWidget(self.collection_list)

        # Add and delete collection section
        collection_buttons_layout = QHBoxLayout()
        self.new_collection_name = QLineEdit()
        self.new_collection_name.setPlaceholderText("New Collection Name")
        collection_buttons_layout.addWidget(self.new_collection_name)

        btn_add_collection = QPushButton("Add Collection")
        btn_add_collection.clicked.connect(self.add_collection)
        collection_buttons_layout.addWidget(btn_add_collection)

        btn_delete_collection = QPushButton("Delete Collection")
        btn_delete_collection.clicked.connect(self.delete_collection)
        collection_buttons_layout.addWidget(btn_delete_collection)

        layout.addLayout(collection_buttons_layout)

        # Splitter for images in collection and preview
        splitter = QSplitter()

        # Left panel: List of images in the selected collection
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        self.collection_images_label = QLabel("Images in Collection")
        left_layout.addWidget(self.collection_images_label)

        self.collection_images_list = QListWidget()
        self.collection_images_list.itemClicked.connect(self.on_collection_image_selected)
        left_layout.addWidget(self.collection_images_list)

        # Button to delete selected image from collection
        btn_delete_image_from_collection = QPushButton("Delete Selected Image from Collection")
        btn_delete_image_from_collection.clicked.connect(self.delete_image_from_collection)
        left_layout.addWidget(btn_delete_image_from_collection)

        left_panel.setLayout(left_layout)

        # Right panel: Image preview
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        self.collection_preview_label = QLabel("Preview")
        self.collection_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.collection_preview_label.setStyleSheet("border: 1px solid black;")
        self.collection_preview_label.setFixedSize(400, 400)  # Fixed size for preview
        right_layout.addWidget(self.collection_preview_label)

        right_panel.setLayout(right_layout)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        layout.addWidget(splitter)

        # Button to add images to the selected collection
        btn_add_images_to_collection = QPushButton("Add Images to Collection")
        btn_add_images_to_collection.clicked.connect(self.add_images_to_collection)
        layout.addWidget(btn_add_images_to_collection)

        self.setLayout(layout)
        
    def load_collections(self):
        """Load all collections from the database."""
        self.collection_list.clear()
        conn = sqlite3.connect("image_timer.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM collections")
        collections = cursor.fetchall()
        conn.close()
        for collection_id, name in collections:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, collection_id)  # Store collection ID in the item
            self.collection_list.addItem(item)

    def on_collection_selected(self, item):
        """Load images for the selected collection."""
        collection_id = item.data(Qt.ItemDataRole.UserRole)
        self.collection_images_list.clear()
        self.collection_preview_label.clear()
        conn = sqlite3.connect("image_timer.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT collection_images.id, images.id, images.path 
            FROM images 
            JOIN collection_images ON images.id = collection_images.image_id 
            WHERE collection_images.collection_id = ?
        """, (collection_id,))
        images = cursor.fetchall()
        conn.close()

        for row_id, image_id, path in images:
            item = QListWidgetItem(f"{image_id}: {path}")
            item.setData(Qt.ItemDataRole.UserRole, row_id)  # Store the collection_images row ID
            self.collection_images_list.addItem(item)

    def on_collection_image_selected(self, item):
        """Show a preview of the selected image in the collection."""
        image_path = item.text().split(": ")[1]
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.collection_preview_label.size(),
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation
            )
            self.collection_preview_label.setPixmap(scaled_pixmap)
        else:
            self.collection_preview_label.setText("Failed to load image.")

    def add_collection(self):
        """Add a new collection to the database."""
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

    def delete_collection(self):
        """Delete the selected collection and all its associated images."""
        selected_collection = self.collection_list.currentItem()
        if not selected_collection:
            QMessageBox.warning(self, "Error", "Please select a collection to delete.")
            return

        collection_id = selected_collection.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox.question(
            self,
            "Delete Collection",
            "Are you sure you want to delete this collection and all its images?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.collection_preview_label.clear()
            conn = sqlite3.connect("image_timer.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM collection_images WHERE collection_id = ?", (collection_id,))
            cursor.execute("DELETE FROM collections WHERE id = ?", (collection_id,))
            conn.commit()
            conn.close()
            self.load_collections()
            self.collection_images_list.clear()

    def delete_image_from_collection(self):
        self.collection_preview_label.clear()
        """Delete the selected image from the collection."""
        selected_image = self.collection_images_list.currentItem()
        if not selected_image:
            QMessageBox.warning(self, "Error", "Please select an image to delete.")
            return

        row_id = selected_image.data(Qt.ItemDataRole.UserRole)  # Get the collection_images row ID

        conn = sqlite3.connect("image_timer.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM collection_images WHERE id = ?", (row_id,))
        conn.commit()
        conn.close()

        # Refresh the images list
        selected_collection = self.collection_list.currentItem()
        if selected_collection:
            self.on_collection_selected(selected_collection)


    def add_images_to_collection(self):
        """Open a dialog to add images from storage to the selected collection."""
        selected_collection = self.collection_list.currentItem()
        if not selected_collection:
            QMessageBox.warning(self, "Error", "Please select a collection first.")
            return

        collection_id = selected_collection.data(Qt.ItemDataRole.UserRole)

        # Open a dialog to select images from storage
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Images to Collection")
        layout = QVBoxLayout()
        dialog.setLayout(layout)

        splitter = QSplitter()

        # Left panel: List of images in storage
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        self.dialog_image_list = QListWidget()
        self.dialog_image_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)  # Enable multi-selection
        conn = sqlite3.connect("image_timer.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, path FROM images")
        images = cursor.fetchall()
        conn.close()

        for image_id, path in images:
            item = QListWidgetItem(f"{image_id}: {path}")
            item.setData(Qt.ItemDataRole.UserRole, image_id)  # Store image ID in the item
            self.dialog_image_list.addItem(item)

        self.dialog_image_list.itemClicked.connect(lambda item: self.on_dialog_image_selected(item, dialog_preview_label))
        left_layout.addWidget(self.dialog_image_list)

        left_panel.setLayout(left_layout)

        # Right panel: Image preview
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        dialog_preview_label = QLabel("Preview")
        dialog_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dialog_preview_label.setStyleSheet("border: 1px solid black;")
        dialog_preview_label.setFixedSize(400, 400)  # Fixed size for preview
        right_layout.addWidget(dialog_preview_label)

        right_panel.setLayout(right_layout)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        layout.addWidget(splitter)

        btn_add = QPushButton("Add Selected Images")
        btn_add.clicked.connect(lambda: self.add_selected_images_to_collection(collection_id, self.dialog_image_list, dialog))
        layout.addWidget(btn_add)

        dialog.exec()

    def on_dialog_image_selected(self, item, preview_label):
        """Show a preview of the selected image in the dialog."""
        image_path = item.text().split(": ")[1]
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                preview_label.size(),
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation
            )
            preview_label.setPixmap(scaled_pixmap)
        else:
            preview_label.setText("Failed to load image.")

    def add_selected_images_to_collection(self, collection_id, image_list, dialog):
        """Add selected images to the collection."""
        selected_items = image_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select at least one image.")
            return

        conn = sqlite3.connect("image_timer.db")
        cursor = conn.cursor()
        for item in selected_items:
            image_id = item.data(Qt.ItemDataRole.UserRole)
            cursor.execute("INSERT INTO collection_images (collection_id, image_id) VALUES (?, ?)", (collection_id, image_id))
        conn.commit()
        conn.close()

        dialog.close()
        self.on_collection_selected(self.collection_list.currentItem())  # Refresh the images list