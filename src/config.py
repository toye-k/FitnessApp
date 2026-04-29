"""
Configuration constants for the fitness exercise application.
All tunable parameters are defined here to maintain DRY principles.
"""

# Application Settings
APP_NAME = "Fitness Exercise Trainer"
APP_VERSION = "1.0.0"
DEBUG = False

# UI Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600

# Color Scheme
COLOR_PRIMARY = "#2C3E50"
COLOR_SECONDARY = "#3498DB"
COLOR_BACKGROUND = "#ECF0F1"
COLOR_TEXT = "#2C3E50"
COLOR_HIGHLIGHT = "#FF6B6B"
COLOR_SELECTED = "#FFA500"
COLOR_HOVER = "#FF8C42"
COLOR_MUSCLE_DEFAULT = "#808080"

# 3D Visualization Settings
MESH_LOD_REDUCTION = 0.5  # Level of Detail reduction factor
RENDER_FPS_TARGET = 30
CAMERA_DISTANCE = 5.0
CAMERA_ROTATION_SPEED = 0.5

# Data File Paths
DATA_DIR = "data"
EXERCISE_DATA_FILE = "exercise_data.json"
MUSCLE_DATA_FILE = "muscle_data.json"
MUSCLE_MESH_MAPPING_FILE = "muscle_mesh_mapping.json"

# Exercise Filtering
MIN_EXERCISES_PER_MUSCLE = 5
DEFAULT_SHOW_MACHINES = True
DEFAULT_SHOW_BODYWEIGHT = True
DEFAULT_SHOW_STRETCHES = True

# YouTube Integration
YOUTUBE_VIDEO_TIMEOUT = 5  # seconds
YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query={}"

# Animation Settings
GIF_MAX_SIZE = (400, 400)  # Max dimensions for exercise GIF display
GIF_DEFAULT_DURATION = 1000  # ms
GIF_LOOP_COUNT = 0  # 0 = infinite

# Performance Thresholds
CACHE_SIZE_MB = 100
MEMORY_WARNING_THRESHOLD_MB = 500

# Logging
LOG_DIR = "logs"
LOG_FILE = "app.log"
LOG_LEVEL = "INFO"

# Testing
TEST_DATA_DIR = "tests/data"
TEST_TIMEOUT = 30  # seconds
