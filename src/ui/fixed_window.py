from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QSpinBox, QCheckBox, QLabel, QMessageBox, QHBoxLayout, QWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor, QKeyEvent, QResizeEvent
import sqlite3
import random
import typing

class FixedTimeModeWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fixed-Time Mode")
        self.setGeometry(200, 200, 600, 500)
        self.setStyleSheet("""
            QDialog {
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
            QSpinBox {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QCheckBox {
                color: #ECEFF4;
                font-size: 14px;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Timer input (hours, minutes, seconds)
        timer_layout = QHBoxLayout()

        self.minutes_input = QSpinBox()
        self.minutes_input.setRange(0, 59)  # 0 to 59 minutes
        self.minutes_input.setValue(0)
        timer_layout.addWidget(QLabel("Minutes:"))
        timer_layout.addWidget(self.minutes_input)

        self.seconds_input = QSpinBox()
        self.seconds_input.setRange(0, 59)  # 0 to 59 seconds
        self.seconds_input.setValue(30)  # Default to 30 seconds
        timer_layout.addWidget(QLabel("Seconds:"))
        timer_layout.addWidget(self.seconds_input)

        layout.addLayout(timer_layout)

        # Collection selection
        self.collection_list = QListWidget()
        self.load_collections()
        layout.addWidget(QLabel("Select Collection:"))
        layout.addWidget(self.collection_list)

        # Start button
        btn_start = QPushButton("Start")
        btn_start.clicked.connect(self.start_fixed_time_mode)
        layout.addWidget(btn_start)

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

    def start_fixed_time_mode(self):
        """Start the fixed-time mode with the selected settings."""
        selected_collection = self.collection_list.currentItem()
        if not selected_collection:
            QMessageBox.warning(self, "Error", "Please select a collection.")
            return

        # Calculate total timer duration in milliseconds
        minutes = self.minutes_input.value()
        seconds = self.seconds_input.value()
        timer_duration = (minutes * 60 + seconds) * 1000

        # Open the image ordering window
        self.image_ordering_window = ImageOrderingWindow(selected_collection.data(Qt.ItemDataRole.UserRole), timer_duration)
        self.image_ordering_window.show()
        self.close()

class ImageOrderingWindow(QDialog):
    def __init__(self, collection_id, timer_duration, parent=None):
        super().__init__(parent)
        self.collection_id = collection_id
        self.timer_duration = timer_duration
        self.setWindowTitle("Customize Image Order")
        self.setGeometry(250, 250, 800, 600)
        self.setStyleSheet("""
            QDialog {
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
            QCheckBox {
                color: #ECEFF4;
                font-size: 14px;
            }
        """)
        self.setup_ui()
        self.load_images()

    def setup_ui(self):
        layout = QHBoxLayout()

        # Left panel: List of images with drag-and-drop reordering
        self.image_list = QListWidget()
        self.image_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)  # Enable drag-and-drop reordering
        self.image_list.setIconSize(QSize(100, 100))  # Set thumbnail size
        layout.addWidget(self.image_list)

        # Right panel: Image preview and shuffle toggle
        right_panel = QVBoxLayout()

        # Image preview
        self.preview_label = QLabel("Preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid #4C566A; border-radius: 5px;")
        self.preview_label.setFixedSize(400, 400)  # Fixed size for preview
        right_panel.addWidget(self.preview_label)

        # Shuffle mode toggle
        self.shuffle_checkbox = QCheckBox("Shuffle Mode")
        self.shuffle_checkbox.stateChanged.connect(self.toggle_shuffle_mode)
        right_panel.addWidget(self.shuffle_checkbox)

        # Start button
        btn_start = QPushButton("Start Fixed-Time Mode")
        btn_start.clicked.connect(self.start_fixed_time_mode)
        right_panel.addWidget(btn_start)

        layout.addLayout(right_panel)

        self.setLayout(layout)

    def load_images(self):
        """Load images for the selected collection."""
        conn = sqlite3.connect("image_timer.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT images.id, images.path 
            FROM images 
            JOIN collection_images ON images.id = collection_images.image_id 
            WHERE collection_images.collection_id = ?
        """, (self.collection_id,))
        self.images = [{"id": row[0], "path": row[1]} for row in cursor.fetchall()]
        conn.close()

        for image in self.images:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, image["id"])  # Store image ID in the item

            # Create a white background for the thumbnail
            pixmap = QPixmap(image["path"])
            if not pixmap.isNull():
                # Create a white background image
                background = QPixmap(100, 100)
                background.fill(QColor("white"))
                painter = QPainter(background)
                scaled_pixmap = pixmap.scaled(100, 100, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
                painter.drawPixmap(
                    (background.width() - scaled_pixmap.width()) // 2,
                    (background.height() - scaled_pixmap.height()) // 2,
                    scaled_pixmap
                )
                painter.end()
                item.setIcon(QIcon(background))

            item.setText(image["path"])
            self.image_list.addItem(item)

        # Connect item selection to preview
        self.image_list.itemClicked.connect(self.on_image_selected)

    def on_image_selected(self, item):
        """Show a preview of the selected image."""
        image_path = item.text()
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.preview_label.size(),
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
        else:
            self.preview_label.setText("Failed to load image.")

    def toggle_shuffle_mode(self):
        """Enable or disable drag-and-drop based on shuffle mode."""
        if self.shuffle_checkbox.isChecked():
            self.image_list.setDragDropMode(QListWidget.DragDropMode.NoDragDrop)
            self.image_list.setStyleSheet("background-color: #3B4252;")  # Visual indicator for shuffle mode
        else:
            self.image_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
            self.image_list.setStyleSheet("")  # Reset style

    def start_fixed_time_mode(self):
        """Start the fixed-time mode with the customized order."""
        # Get the ordered image paths
        ordered_images = []
        for index in range(self.image_list.count()):
            item = self.image_list.item(index)
            if item is not None:
                ordered_images.append(item.text())

        # Open the image player window
        self.image_player = ImagePlayerWindow(ordered_images, self.timer_duration, self.shuffle_checkbox.isChecked())
        self.image_player.show()
        self.close()
        
class ImagePlayerWindow(QWidget):
    def __init__(self, images, timer_duration, shuffle_mode, parent=None):
        super().__init__(parent)
        self.images = images
        self.timer_duration = timer_duration
        self.shuffle_mode = shuffle_mode
        self.current_index = 0
        self.remaining_time = timer_duration // 1000  # Convert to seconds
        self.timer_running = False
        self.is_fullscreen = False  # Track fullscreen state
        self.setWindowTitle("Fixed-Time Mode - Image Player")
        self.setGeometry(100, 100, 800, 600)
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
            QLabel {
                color: #ECEFF4;
                font-size: 16px;
            }
        """)
        self.setup_ui()

        # Shuffle the images if shuffle mode is enabled
        if self.shuffle_mode:
            random.shuffle(self.images)

        # Display the first image immediately
        self.show_current_image()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Image display
        self.image_label = QLabel("Image Preview")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px solid #4C566A;
                border-radius: 10px;
                background-color: #3B4252;
            }
        """)
        
        # Set QLabel size policy to prevent infinite window growth
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image_label.setScaledContents(False)  # Don't allow QLabel to scale its content automatically

        layout.addWidget(self.image_label, stretch=1)  # Allow the image label to expand

        # Timer display
        self.timer_label = QLabel("00:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: bold;
                color: #ECEFF4;
            }
        """)
        layout.addWidget(self.timer_label)

        # Button layout (horizontal)
        button_layout = QHBoxLayout()  # Use QHBoxLayout for horizontal alignment

        # Start button
        self.btn_start = QPushButton("Start (S)")
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                font-size: 14px;  # Smaller font size
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 10px;  # Smaller padding
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
        """)
        self.btn_start.clicked.connect(self.start_timer)
        button_layout.addWidget(self.btn_start)

        # Stop button
        self.btn_stop = QPushButton("Stop (P)")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                font-size: 14px;  # Smaller font size
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 10px;  # Smaller padding
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
        """)
        self.btn_stop.clicked.connect(self.stop_timer)
        self.btn_stop.hide()  # Initially hidden
        button_layout.addWidget(self.btn_stop)

       # Reset Timer button
        self.btn_reset = QPushButton("Reset (R)")
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                font-size: 14px;  # Smaller font size
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 10px;  # Smaller padding
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
        """)
        self.btn_reset.clicked.connect(self.reset_timer)
        self.btn_reset.hide()  # Initially hidden
        button_layout.addWidget(self.btn_reset)

        # Skip button
        self.btn_skip = QPushButton("Skip (N)")
        self.btn_skip.setStyleSheet("""
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                font-size: 14px;  # Smaller font size
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 10px;  # Smaller padding
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
        """)
        self.btn_skip.clicked.connect(self.skip_image)
        self.btn_skip.hide()  # Initially hidden
        button_layout.addWidget(self.btn_skip)

        # Back button
        self.btn_back = QPushButton("Back (B)")
        self.btn_back.setStyleSheet("""
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                font-size: 14px;  # Smaller font size
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 10px;  # Smaller padding
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
        """)
        self.btn_back.clicked.connect(self.previous_image)
        self.btn_back.hide()  # Initially hidden
        button_layout.addWidget(self.btn_back)

        # End button
        self.btn_end = QPushButton("End Practice (E)")
        self.btn_end.setStyleSheet("""
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                font-size: 14px;  # Smaller font size
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 10px;  # Smaller padding
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
        """)
        self.btn_end.clicked.connect(self.end_practice)
        self.btn_end.hide()  # Initially hidden
        button_layout.addWidget(self.btn_end)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def start_timer(self):
        """Start the timer to display images."""
        if not self.timer_running:
            self.timer_running = True
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_timer)
            self.timer.start(1000)  # Update every second

            # Hide the Start button and show the other buttons
            self.btn_start.hide()
            self.btn_stop.show()
            self.btn_skip.show()
            self.btn_back.show()
            self.btn_reset.show()
            self.btn_end.show()

            # Update the timer label style to indicate running state
            self.timer_label.setStyleSheet("""
                QLabel {
                    font-size: 48px;
                    font-weight: bold;
                    color: #4CAF50;
                }
            """)

    def stop_timer(self):
        """Stop the timer."""
        if self.timer_running:
            self.timer_running = False
            self.timer.stop()

            # Show the Start button and hide the other buttons
            self.btn_start.show()
            self.btn_stop.hide()
            self.btn_skip.hide()
            self.btn_back.hide()
            self.btn_reset.hide()
            self.btn_end.hide()

            # Update the timer label style to indicate paused state
            self.timer_label.setStyleSheet("""
                QLabel {
                    font-size: 48px;
                    font-weight: bold;
                    color: #f44336;
                }
            """)

    def reset_timer(self):
        """Reset the timer to its initial duration."""
        self.remaining_time = self.timer_duration // 1000  # Reset to initial time
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.timer_label.setText(f"{minutes:02}:{seconds:02}")  # Update the timer display
            
    def skip_image(self):
        """Skip to the next image."""
        self.show_next_image()

    def previous_image(self):
        """Go back to the previous image."""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_image()
            self.remaining_time = self.timer_duration // 1000  # Reset timer
        self.update_back_button_state()

    def end_practice(self):
        """End the practice session."""
        self.stop_timer()
        self.close()

    def update_timer(self):
        """Update the countdown timer."""
        if self.remaining_time > 0:
            self.remaining_time -= 1
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60
            self.timer_label.setText(f"{minutes:02}:{seconds:02}")
        else:
            self.show_next_image()
            self.remaining_time = self.timer_duration // 1000  # Reset timer

    def show_current_image(self):
        """Display the current image in the collection."""
        image_path = self.images[self.current_index]
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.current_pixmap = pixmap  # Store the original pixmap
            self.update_image_size()
        else:
            self.image_label.setText("Failed to load image.")
        self.update_back_button_state()

    def update_image_size(self):
        """Update image size dynamically without resizing QLabel."""
        if hasattr(self, "current_pixmap") and not self.current_pixmap.isNull():
            scaled_pixmap = self.current_pixmap.scaled(
                self.image_label.width(), 
                self.image_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, a0: typing.Optional[QResizeEvent]):
        """Prevent QLabel from causing infinite window growth."""
        if hasattr(self, "current_pixmap") and not self.current_pixmap.isNull():
            self.update_image_size()
        super().resizeEvent(a0)

    def show_next_image(self):
        """Display the next image in the collection."""
        if self.current_index >= len(self.images) - 1:
            self.current_index = 0  # Restart from the beginning
            if self.shuffle_mode:
                random.shuffle(self.images)  # Reshuffle if shuffle mode is enabled
        else:
            self.current_index += 1

        self.show_current_image()
        self.remaining_time = self.timer_duration // 1000  # Reset timer

    def update_back_button_state(self):
        """Enable or disable the Back button based on the current image index."""
        if self.current_index == 0:
            self.btn_back.setEnabled(False)  # Disable if it's the first image
        else:
            self.btn_back.setEnabled(True)  # Enable otherwise

    def toggle_fullscreen(self):
        """Toggle between fullscreen and normal mode."""
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True

    def keyPressEvent(self, a0: typing.Optional[QKeyEvent]):
        """Handle hotkeys."""
        if a0 is not None:
            if a0.key() == Qt.Key.Key_S:  # Start timer
                self.start_timer()
            elif a0.key() == Qt.Key.Key_P:  # Stop timer
                self.stop_timer()
            elif a0.key() == Qt.Key.Key_R:  # Stop timer
                self.reset_timer()
            elif a0.key() == Qt.Key.Key_N:  # Skip to next image
                self.skip_image()
            elif a0.key() == Qt.Key.Key_B:  # Go back to previous image
                self.previous_image()
            elif a0.key() == Qt.Key.Key_E:  # End practice
                self.end_practice()
            elif a0.key() == Qt.Key.Key_F11:  # Toggle fullscreen
                self.toggle_fullscreen()