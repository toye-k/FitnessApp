"""
Exercise detail popup dialog for displaying exercise information.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton,
    QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QThread
from PyQt6.QtGui import QFont, QDesktopServices, QPixmap
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from typing import Optional
from pathlib import Path
import urllib.parse

from src.models import Exercise
from src.utils.logger import get_logger
from src import config

logger = get_logger(__name__)


def _ensure_package(package: str, import_name: str = None) -> bool:
    """Import package, installing via pip if missing. Returns True on success."""
    import importlib
    import subprocess
    import sys

    name = import_name or package
    try:
        importlib.import_module(name)
        return True
    except ImportError:
        logger.info(f"Installing {package}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True
        )
        try:
            importlib.import_module(name)
            return True
        except ImportError:
            logger.warning(f"Failed to install {package}")
            return False


class TutorialSearchWorker(QThread):
    """Worker thread for searching YouTube tutorials."""

    found = pyqtSignal(str)   # emits the video URL
    failed = pyqtSignal()

    def __init__(self, exercise_name: str):
        super().__init__()
        self.exercise_name = exercise_name

    def run(self):
        if not _ensure_package("youtubesearchpython", "youtubesearchpython"):
            self.failed.emit()
            return
        try:
            from youtubesearchpython import VideosSearch
            search = VideosSearch(f"{self.exercise_name} shorts", limit=15)
            videos = search.result().get("result", [])
            if not videos:
                self.failed.emit()
                return

            best_url, best_views = None, -1
            for video in videos:
                try:
                    count_text = video.get("viewCount", {}).get("text", "0")
                    count = int("".join(c for c in count_text if c.isdigit()) or "0")
                    if count > best_views:
                        best_views = count
                        best_url = f"https://www.youtube.com/watch?v={video['id']}"
                except (ValueError, KeyError):
                    continue

            if best_url:
                self.found.emit(best_url)
            else:
                self.failed.emit()
        except Exception as e:
            logger.warning(f"Tutorial search failed: {e}")
            self.failed.emit()


class ExerciseDetailDialog(QDialog):
    """
    Dialog for displaying detailed information about an exercise.
    Shows instructions, tips, animation (if available), and YouTube links.
    """

    # Signals
    youtube_clicked = pyqtSignal(str)  # Emitted when YouTube button is clicked

    def __init__(
        self,
        exercise: Exercise,
        parent: Optional[QDialog] = None
    ) -> None:
        """
        Initialize the exercise detail dialog.

        Args:
            exercise: The Exercise object to display
            parent: Parent widget
        """
        super().__init__(parent)
        self.exercise = exercise
        self.setWindowTitle(f"Exercise Details - {exercise.name}")
        self.setGeometry(100, 100, 700, 750)
        self._search_worker = None

        self._setup_ui()
        logger.info(f"Initialized exercise detail dialog for: {exercise.name}")

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        main_layout = QVBoxLayout()

        # Title
        title_label = QLabel(self.exercise.name)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # Difficulty
        difficulty_label = QLabel(f"Difficulty: {self.exercise.difficulty.value.capitalize()}")
        main_layout.addWidget(difficulty_label)

        # Step-by-step images + Muscle highlight image (side-by-side)
        image_dir = Path("assets/images") / self.exercise.id
        images = sorted(image_dir.glob("*.jpg")) if image_dir.exists() else []
        highlight_path = Path("assets/highlights") / f"{self.exercise.target_muscles[0]}.png" if self.exercise.target_muscles else None
        has_highlight = highlight_path and highlight_path.exists()

        if images or has_highlight:
            # Horizontal layout for images side-by-side
            image_row_layout = QHBoxLayout()

            # Step-by-step images (left side)
            if images:
                img_scroll = QScrollArea()
                img_scroll.setFixedHeight(220)
                img_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                img_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                img_scroll.setWidgetResizable(True)

                img_container = QWidget()
                img_layout = QHBoxLayout(img_container)
                img_layout.setSpacing(8)

                for i, img_path in enumerate(images):
                    step_widget = QWidget()
                    step_layout = QVBoxLayout(step_widget)
                    step_layout.setSpacing(4)

                    pixmap = QPixmap(str(img_path)).scaledToHeight(
                        170, Qt.TransformationMode.SmoothTransformation
                    )
                    img_label = QLabel()
                    img_label.setPixmap(pixmap)
                    img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    step_layout.addWidget(img_label)

                    caption = QLabel(f"Step {i + 1}")
                    caption_font = QFont()
                    caption_font.setPointSize(8)
                    caption.setFont(caption_font)
                    caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    step_layout.addWidget(caption)

                    img_layout.addWidget(step_widget)

                img_layout.addStretch()
                img_scroll.setWidget(img_container)
                image_row_layout.addWidget(img_scroll, stretch=1)

            # Muscle highlight image (right side)
            if has_highlight:
                highlight_pixmap = QPixmap(str(highlight_path)).scaledToHeight(
                    200, Qt.TransformationMode.SmoothTransformation
                )
                highlight_label = QLabel()
                highlight_label.setPixmap(highlight_pixmap)
                highlight_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                highlight_label.setFixedWidth(200)
                image_row_layout.addWidget(highlight_label)

            main_layout.addLayout(image_row_layout)

        # Create scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Description
        if self.exercise.description:
            desc_label = QLabel("Description:")
            desc_font = QFont()
            desc_font.setBold(True)
            desc_label.setFont(desc_font)
            scroll_layout.addWidget(desc_label)

            desc_text = QLabel(self.exercise.description)
            desc_text.setWordWrap(True)
            scroll_layout.addWidget(desc_text)

        # Target Muscles
        if self.exercise.target_muscles:
            target_label = QLabel("Target Muscles:")
            target_font = QFont()
            target_font.setBold(True)
            target_label.setFont(target_font)
            scroll_layout.addWidget(target_label)

            target_text = QLabel(", ".join(self.exercise.target_muscles))
            target_text.setWordWrap(True)
            scroll_layout.addWidget(target_text)

        # Secondary Muscles
        if self.exercise.secondary_muscles:
            secondary_label = QLabel("Secondary Muscles:")
            secondary_font = QFont()
            secondary_font.setBold(True)
            secondary_label.setFont(secondary_font)
            scroll_layout.addWidget(secondary_label)

            secondary_text = QLabel(", ".join(self.exercise.secondary_muscles))
            secondary_text.setWordWrap(True)
            scroll_layout.addWidget(secondary_text)

        # Equipment
        if self.exercise.equipment:
            equipment_label = QLabel("Equipment:")
            equipment_font = QFont()
            equipment_font.setBold(True)
            equipment_label.setFont(equipment_font)
            scroll_layout.addWidget(equipment_label)

            equipment_text = QLabel(
                ", ".join([eq.value for eq in self.exercise.equipment])
            )
            equipment_text.setWordWrap(True)
            scroll_layout.addWidget(equipment_text)

        # Instructions
        if self.exercise.instructions:
            instructions_label = QLabel("Instructions:")
            instructions_font = QFont()
            instructions_font.setBold(True)
            instructions_label.setFont(instructions_font)
            scroll_layout.addWidget(instructions_label)

            for i, instruction in enumerate(self.exercise.instructions, 1):
                instruction_text = QLabel(f"{i}. {instruction}")
                instruction_text.setWordWrap(True)
                scroll_layout.addWidget(instruction_text)

        # Tips
        if self.exercise.tips:
            tips_label = QLabel("Tips:")
            tips_font = QFont()
            tips_font.setBold(True)
            tips_label.setFont(tips_font)
            scroll_layout.addWidget(tips_label)

            for tip in self.exercise.tips:
                tip_text = QLabel(f"• {tip}")
                tip_text.setWordWrap(True)
                scroll_layout.addWidget(tip_text)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        # Buttons
        button_layout = QHBoxLayout()

        if self.exercise.youtube_video_id:
            self.tutorial_button = QPushButton("Watch on YouTube")
        else:
            self.tutorial_button = QPushButton("Search Tutorial on YouTube")
        self.tutorial_button.clicked.connect(self._on_youtube_clicked)
        button_layout.addWidget(self.tutorial_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _on_youtube_clicked(self) -> None:
        """Handle YouTube button click - open video or search."""
        if self.exercise.youtube_video_id:
            url = self.exercise.get_youtube_url()
            if url:
                QDesktopServices.openUrl(QUrl(url))
                self.youtube_clicked.emit(self.exercise.youtube_video_id)
                logger.debug(f"Opened YouTube video: {url}")
        else:
            self.tutorial_button.setEnabled(False)
            self.tutorial_button.setText("Searching...")
            self._search_worker = TutorialSearchWorker(self.exercise.name)
            self._search_worker.found.connect(self._on_tutorial_found)
            self._search_worker.failed.connect(self._on_tutorial_failed)
            self._search_worker.start()

    def _on_tutorial_found(self, url: str) -> None:
        """Handle successful tutorial search - open the video."""
        QDesktopServices.openUrl(QUrl(url))
        self.tutorial_button.setEnabled(True)
        self.tutorial_button.setText("Search Tutorial on YouTube")

    def _on_tutorial_failed(self) -> None:
        """Handle failed tutorial search - fallback to search page."""
        query = urllib.parse.quote(f"{self.exercise.name} exercise tutorial")
        url = f"https://www.youtube.com/results?search_query={query}"
        QDesktopServices.openUrl(QUrl(url))
        self.tutorial_button.setEnabled(True)
        self.tutorial_button.setText("Search Tutorial on YouTube")

    def get_exercise(self) -> Exercise:
        """
        Get the exercise being displayed.

        Returns:
            The Exercise object
        """
        return self.exercise
