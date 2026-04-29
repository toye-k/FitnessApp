"""
Main entry point for the Fitness Exercise Trainer application.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> int:
    """
    Main application entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Create Qt application
        app = QApplication(sys.argv)

        # Create and show main window
        window = MainWindow()
        window.show()

        logger.info("Application started successfully")

        # Run application event loop
        return app.exec()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
