from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QSpinBox, QCheckBox, QLabel, QMessageBox, QHBoxLayout, QWidget, QSizePolicy, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, QSize, QUrl
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor, QKeyEvent, QResizeEvent
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

import sqlite3
import random
import typing
import os

class SessionModeWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Session Mode")
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
            QComboBox {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
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

        # Collection selection
        self.collection_list = QListWidget()
        self.load_collections()
        layout.addWidget(QLabel("Select Collection:"))
        layout.addWidget(self.collection_list)

        # Session duration selection
        self.session_duration_combo = QComboBox()
        self.load_session_durations()
        layout.addWidget(QLabel("Select Session Duration:"))
        layout.addWidget(self.session_duration_combo)

        # Custom duration input (initially hidden)
        self.custom_duration_input = QLineEdit()
        self.custom_duration_input.setPlaceholderText("Enter custom duration")
        self.custom_duration_input.hide()
        layout.addWidget(self.custom_duration_input)

        # Button to add custom session
        btn_add_custom_session = QPushButton("Add Custom Session")
        btn_add_custom_session.clicked.connect(self.add_custom_session)
        layout.addWidget(btn_add_custom_session)


        # Start button
        btn_start = QPushButton("Start Session")
        btn_start.clicked.connect(self.start_session)
        layout.addWidget(btn_start)

        self.setLayout(layout)

    def load_collections(self):
        """Load all collections from the database."""
        self.collection_list.clear()
        
        # Add the "All" collection
        all_collection_item = QListWidgetItem("All")
        all_collection_item.setData(Qt.ItemDataRole.UserRole, -1)  # Use -1 as a special ID for "All"
        self.collection_list.addItem(all_collection_item)
        
        conn = sqlite3.connect("image_timer.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM collections")
        collections = cursor.fetchall()
        conn.close()
        
        for collection_id, name in collections:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, collection_id)
            self.collection_list.addItem(item)

    def start_session(self):
        selected_collection = self.collection_list.currentItem()
        if not selected_collection:
            QMessageBox.warning(self, "Error", "Please select a collection.")
            return

        # Get the selected session duration
        session_duration = self.session_duration_combo.currentText()
        if session_duration == "Custom...":
            session_duration = self.custom_duration_input.text().strip()
            if not session_duration:
                QMessageBox.warning(self, "Error", "Please enter a custom session duration.")
                return

        # Fetch images based on the selected collection
        if selected_collection.data(Qt.ItemDataRole.UserRole) == -1:
            # "All" collection: Fetch all images from the database
            conn = sqlite3.connect("image_timer.db")
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM images")
            images = [row[0] for row in cursor.fetchall()]  # Get all image paths
            conn.close()
        else:
            # Regular collection: Fetch images for the selected collection
            collection_id = selected_collection.data(Qt.ItemDataRole.UserRole)
            conn = sqlite3.connect("image_timer.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT images.path 
                FROM images 
                JOIN collection_images ON images.id = collection_images.image_id 
                WHERE collection_images.collection_id = ?
            """, (collection_id,))
            images = [row[0] for row in cursor.fetchall()]  # Get image paths for the collection
            conn.close()

        # Open the session image ordering window
        self.session_ordering_window = SessionImageOrderingWindow(images, session_duration)
        self.session_ordering_window.show()
        self.close()

    def load_session_durations(self):
            """Load built-in and custom session durations from the database."""
            self.session_duration_combo.clear()

            # Load custom sessions from the database
            conn = sqlite3.connect("image_timer.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name, duration FROM sessions")
            sessions = cursor.fetchall()
            conn.close()

            for name, duration in sessions:
                self.session_duration_combo.addItem(f"{name}: {duration}")

    def add_custom_session(self):
        """Open the custom session creation dialog."""
        custom_session_dialog = CustomSessionDialog(self)
        custom_session_dialog.exec()
        self.load_session_durations()  # Refresh the session duration list

class SessionImageOrderingWindow(QDialog):
    def __init__(self, images, session_duration, parent=None):
        super().__init__(parent)
        self.images = images  # List of image paths
        self.session_duration = session_duration
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
        btn_start = QPushButton("Start Session Mode")
        btn_start.clicked.connect(self.start_session_mode)
        right_panel.addWidget(btn_start)

        layout.addLayout(right_panel)
        self.setLayout(layout)

    def load_images(self):
        """Load images from the provided list of paths."""
        for image_path in self.images:
            item = QListWidgetItem()
            item.setText(image_path)

            # Create a white background for the thumbnail
            pixmap = QPixmap(image_path)
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

    def start_session_mode(self):
        """Start the session mode with the customized order."""
        # Get the ordered image paths
        ordered_images = []
        for index in range(self.image_list.count()):
            item = self.image_list.item(index)
            if item is not None:
                ordered_images.append(item.text())

        # Open the session player window
        self.session_player = SessionPlayerWindow(ordered_images, self.session_duration, self.shuffle_checkbox.isChecked())
        self.session_player.show()
        self.close()


class SessionPlayerWindow(QWidget):
    def __init__(self, images, session_duration, shuffle_mode, parent=None):
        super().__init__(parent)
        self.images = images
        self.session_duration = session_duration
        self.shuffle_mode = shuffle_mode
        self.current_index = 0
        self.timer_running = False
        self.is_fullscreen = False  # Track fullscreen state
        self.setWindowTitle("Session Mode - Image Player")
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

        # Initialize the media player for sound cues
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        # Set volume to 50% (adjust as needed)
        self.audio_output.setVolume(0.5)

        # Load the sound file
        sound_file_path = os.path.abspath("src/assets/kahootSound.mp3")
        self.media_player.setSource(QUrl.fromLocalFile(sound_file_path))

        # Connect to the errorOccurred signal for debugging
        self.media_player.errorOccurred.connect(self.handle_media_error)
        
        # Parse the session duration into timings
        self.timings = self.parse_session_duration(self.session_duration)
        self.current_timing_index = 0  # Tracks which timing is currently active
        self.images_displayed_for_current_timing = 0  # Tracks how many images have been displayed for the current timing
        self.remaining_time = self.timings[self.current_timing_index][1]  # Initial duration in seconds

        # Shuffle the images if shuffle mode is enabled
        if self.shuffle_mode:
            random.shuffle(self.images)

        # Display the first image immediately
        self.show_current_image()

    def handle_media_error(self, error):
        """Handle errors from the media player."""
        error_message = self.media_player.errorString()
        print(f"Media player error: {error_message}")
        
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
        button_layout = QHBoxLayout()

        # Start button
        self.btn_start = QPushButton("Start (S)")
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 10px;
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
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 10px;
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
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 10px;
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
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 10px;
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
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
        """)
        self.btn_back.clicked.connect(self.previous_image)
        self.btn_back.hide()  # Initially hidden
        button_layout.addWidget(self.btn_back)

        # End button
        self.btn_end = QPushButton("End Session (E)")
        self.btn_end.setStyleSheet("""
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
        """)
        self.btn_end.clicked.connect(self.end_session)
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
            self.media_player.stop()

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
        """Reset the timer for the current image to its original duration."""
        self.remaining_time = self.timings[self.current_timing_index][1]  # Reset to the current timing's duration
        self.update_timer_display()

    def skip_image(self):
        """Skip to the next image."""
        self.show_next_image()

    def previous_image(self):
        """Go back to the previous image and update the timing."""
        if self.current_index > 0:
            self.current_index -= 1  # Move to the previous image

            # Update the timing state for the previous image
            self.update_timing_for_previous_image()

            # Show the previous image
            self.show_current_image()

        # Update the Back button state
        self.update_back_button_state()

    def update_timing_for_previous_image(self):
        """Update the timing state when going back to the previous image."""
        # Reset the timing state
        self.current_timing_index = 0
        self.images_displayed_for_current_timing = 0

        # Iterate through the images and timings to find the correct timing for the previous image
        for i in range(self.current_index):
            # Check if we've displayed enough images for the current timing
            current_timing_count, _, _ = self.timings[self.current_timing_index]
            if self.images_displayed_for_current_timing >= current_timing_count:
                # Move to the next timing
                self.current_timing_index = (self.current_timing_index + 1) % len(self.timings)
                self.images_displayed_for_current_timing = 0

            # Increment the counter for the current timing
            self.images_displayed_for_current_timing += 1

        # Update the remaining time for the current timing
        self.remaining_time = self.timings[self.current_timing_index][1]
        self.update_timer_display()
    
    def end_session(self):
        """End the session."""
        self.media_player.stop()
        self.stop_timer()
        self.close()

    def update_timer(self):
        """Update the countdown timer."""
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_timer_display()
            
            # Play a sound cue if the timer is under 10 seconds
            if self.remaining_time <= 10:
                self.media_player.play()
            else:
                self.media_player.stop()
        else:
            # Move to the next image and update the timing
            self.show_next_image()

    def show_current_image(self):
        """Display the current image or break message."""
        _, _, is_break = self.timings[self.current_timing_index]

        if is_break:
            # Show break message
            self.image_label.setText("You deserve a break!!")
            self.image_label.setStyleSheet("""
                QLabel {
                    font-size: 48px;
                    font-weight: bold;
                    color: #ECEFF4;
                }
            """)
        else:
            # Show the current image
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
        """Display the next image or break and update the timing."""
        # Increment the number of images displayed for the current timing
        self.images_displayed_for_current_timing += 1

        # Check if we've displayed enough images for the current timing
        current_timing_count, _, is_break = self.timings[self.current_timing_index]
        if self.images_displayed_for_current_timing >= current_timing_count:
            # Move to the next timing
            self.current_timing_index = (self.current_timing_index + 1) % len(self.timings)
            self.images_displayed_for_current_timing = 0  # Reset the counter for the new timing

        # Update the remaining time for the new timing
        self.remaining_time = self.timings[self.current_timing_index][1]

        # Move to the next image (if not a break)
        if not is_break:
            if self.current_index >= len(self.images) - 1:
                self.current_index = 0  # Restart from the beginning
                if self.shuffle_mode:
                    random.shuffle(self.images)  # Reshuffle if shuffle mode is enabled
            else:
                self.current_index += 1

        # Display the next image or break
        self.show_current_image()

    def reset_timing_for_current_image(self):
        """Reset the timing for the current image."""
        self.remaining_time = self.timings[self.current_timing_index][1]
        self.update_timer_display()

    def update_timer_display(self):
        """Update the timer display."""
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.timer_label.setText(f"{minutes:02}:{seconds:02}")

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
            elif a0.key() == Qt.Key.Key_R:  # Reset timer
                self.reset_timer()
            elif a0.key() == Qt.Key.Key_N:  # Skip to next image
                self.skip_image()
            elif a0.key() == Qt.Key.Key_B:  # Go back to previous image
                self.previous_image()
            elif a0.key() == Qt.Key.Key_E:  # End session
                self.end_session()
            elif a0.key() == Qt.Key.Key_F11:  # Toggle fullscreen
                self.toggle_fullscreen()

    def parse_session_duration(self, duration_str):
        """Parse a session duration string into a list of (count, duration, is_break) tuples."""
        # Extract the duration part from the session string (e.g., "keke: 2x30sec" -> "2x30sec")
        if ": " in duration_str:
            duration_str = duration_str.split(": ")[1]  # Get the part after ": "

        segments = duration_str.split(" + ")
        timings = []
        for segment in segments:
            if "break" in segment:
                # Handle break time
                # Example: "1x5min break" -> count=1, duration=5min
                count, duration_part = segment.split("x")
                duration = int(duration_part.replace("min break", "")) * 60
                timings.append((int(count), duration, True))  # Break is a single event
            else:
                # Handle regular image timings
                # Example: "2x30sec" -> count=2, duration=30sec
                count, duration_part = segment.split("x")
                if "sec" in duration_part:
                    duration = int(duration_part.replace("sec", ""))
                elif "min" in duration_part:
                    duration = int(duration_part.replace("min", "")) * 60
                if "sec" in duration_part:
                    duration = int(duration_part.replace("sec", ""))
                elif "min" in duration_part:
                    duration = int(duration_part.replace("min", "")) * 60
                else:
                    raise ValueError(f"Invalid duration format: {duration_part}")
                timings.append((int(count), duration, False))  # Regular image timing
        return timings

    
class CustomSessionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Custom Session")
        self.setGeometry(200, 200, 600, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Session name input
        self.session_name_input = QLineEdit()
        self.session_name_input.setPlaceholderText("Session Name")
        layout.addWidget(self.session_name_input)

        # Segment input fields
        segment_layout = QHBoxLayout()

        # Number of segments input
        self.segment_count_input = QSpinBox()
        self.segment_count_input.setRange(1, 999)  # Allow 1 to 999 repetitions
        self.segment_count_input.setValue(1)  # Default to 1
        segment_layout.addWidget(QLabel("Repeat:"))
        segment_layout.addWidget(self.segment_count_input)

        # Duration input
        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 999)  # Allow durations from 1 to 999
        self.duration_input.setValue(10)  # Default duration
        segment_layout.addWidget(QLabel("Duration:"))
        segment_layout.addWidget(self.duration_input)

        # Unit of time dropdown
        self.unit_dropdown = QComboBox()
        self.unit_dropdown.addItems(["seconds", "minutes"])
        segment_layout.addWidget(QLabel("Unit:"))
        segment_layout.addWidget(self.unit_dropdown)

        # Type dropdown (active or break)
        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems(["active", "break"])
        segment_layout.addWidget(QLabel("Type:"))
        segment_layout.addWidget(self.type_dropdown)

        # Add Segment button
        btn_add_segment = QPushButton("Add Segment")
        btn_add_segment.clicked.connect(self.add_segment)
        segment_layout.addWidget(btn_add_segment)

        layout.addLayout(segment_layout)

        # List to display added segments (with drag-and-drop reordering)
        self.segments_list = QListWidget()
        self.segments_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)  # Enable drag-and-drop
        layout.addWidget(self.segments_list)

        # Delete Segment button
        btn_delete_segment = QPushButton("Delete Selected Segment")
        btn_delete_segment.clicked.connect(self.delete_segment)
        layout.addWidget(btn_delete_segment)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.save_session)
        btn_layout.addWidget(btn_save)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Store added segments
        self.segments = []

    def add_segment(self):
        """Add a segment to the session."""
        count = self.segment_count_input.value()
        duration = self.duration_input.value()
        unit = self.unit_dropdown.currentText()
        segment_type = self.type_dropdown.currentText()

        # Add the segment to the list
        segment_str = f"{count}x{duration} {unit} ({segment_type})"
        self.segments_list.addItem(segment_str)

        # Store the segment in a list for saving
        self.segments.append((count, duration, unit, segment_type))

    def delete_segment(self):
        """Delete the selected segment from the list."""
        selected_item = self.segments_list.currentItem()
        if selected_item:
            row = self.segments_list.row(selected_item)
            self.segments_list.takeItem(row)  # Remove from the list widget
            del self.segments[row]  # Remove from the stored segments

    def save_session(self):
        """Save the session with the added segments."""
        session_name = self.session_name_input.text().strip()

        if not session_name:
            QMessageBox.warning(self, "Error", "Please enter a session name.")
            return

        if not self.segments:
            QMessageBox.warning(self, "Error", "Please add at least one segment.")
            return

        # Convert segments to a session duration string
        session_duration = self.convert_segments_to_duration(self.segments)

        # Save the session to the database
        conn = sqlite3.connect("image_timer.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sessions (name, duration) VALUES (?, ?)", (session_name, session_duration))
        conn.commit()
        conn.close()

        self.close()

    def convert_segments_to_duration(self, segments):
        """Convert segments to a session duration string."""
        duration_str = ""
        for count, duration, unit, segment_type in segments:
            if unit == "minutes":
                duration_str += f"{count}x{duration}min "
            else:
                duration_str += f"{count}x{duration}sec "
            if segment_type == "break":
                duration_str += "break "
            duration_str += "+ "
        return duration_str.strip(" + ")  # Remove the trailing "+ "