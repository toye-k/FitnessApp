# Fitness Exercise Trainer

A Python-based desktop fitness training application featuring interactive 3D human body visualization, exercise selection, and detailed workout instructions.

## Features

- **3D Body Model Visualization**: Interactive 3D model of the human body with clickable, selectable muscle groups
- **Exercise Database**: Comprehensive database of exercises with instructions, tips, difficulty levels, and equipment requirements
- **Filtering System**: Toggle filters for machines, bodyweight exercises, and stretches
- **Step-by-Step Exercise Photos**: Visual guides with anatomical muscle highlight diagrams
- **Auto-Search YouTube Tutorials**: Automatically finds and plays the most-viewed YouTube Short for any exercise (no API key needed)
- **Direct Video Links**: Opens YouTube directly for exercises with a known video ID
- **Modular Architecture**: Clean layered architecture separating data, models, services, visualization, and UI

## Project Structure

```
project_root/
├── src/
│   ├── config.py                # Configuration constants
│   ├── models/                  # Data models (Exercise, Muscle)
│   ├── data/                    # Data loading and processing
│   ├── services/                # Business logic layer
│   ├── utils/                   # Utilities and logging
│   ├── ui/                      # PyQt6 UI components
│   └── visualization/           # 3D visualization with Vispy
├── data/                        # JSON data files
├── assets/
│   ├── highlights/              # Muscle highlight diagrams (generated)
│   ├── images/                  # Exercise step-by-step photos
│   └── models/                  # 3D anatomical models (not in repo — see below)
├── tests/                       # Unit and integration tests
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
└── README.md                    # This file
```

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the project**
   ```bash
   cd Fitness_Exercise_Trainer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the 3D anatomical models**
   The BodyParts3D models are not included in this repo (1.4 GB). Clone them into the correct location:
   ```bash
   git clone https://github.com/Kevin-Mattheus-Moerman/BodyParts3D assets/models/BodyParts3D-main
   ```
   See [CREDITS.md](CREDITS.md) for license details on these models (CC BY-SA 2.1 JP).

5. **Run the application**
   ```bash
   python run_app.py
   ```

## Running Tests

Execute unit tests with pytest:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=src
```

## Architecture Overview

### Layered Architecture

1. **Data Layer** (`src/data/`)
   - Loads and caches exercise and muscle data from JSON
   - Provides data access interfaces
   - Handles data transformation

2. **Model Layer** (`src/models/`)
   - Defines data structures (Exercise, Muscle, Enums)
   - Provides serialization/deserialization
   - Validates data integrity

3. **Service Layer** (`src/services/`)
   - Implements business logic
   - Filters and processes exercises
   - Handles external integrations (YouTube)

4. **Visualization Layer** (`src/visualization/`)
   - 3D model rendering with Vispy
   - Mesh management
   - Interaction handling

5. **UI Layer** (`src/ui/`)
   - PyQt6 widgets and windows
   - Signal-slot connections
   - User interaction

### Design Patterns

- **Singleton**: DataLoader ensures single instance
- **Strategy**: Multiple filtering strategies
- **Observer**: PyQt signals for UI updates
- **Model-View**: Separation of data and presentation

## Required Libraries

All dependencies are listed in `requirements.txt` and installed via `pip install -r requirements.txt`.

### Core Runtime Dependencies

| Package | Version | Purpose |
|---|---|---|
| **PyQt6** | >=6.4.0 | UI framework |
| **PyQt6-WebEngine** | >=6.4.0 | Web content rendering |
| **vispy** | >=0.14.0 | 3D OpenGL visualization |
| **numpy** | >=1.24.0 | Numerical computing |
| **trimesh** | >=3.23.0 | 3D mesh loading (STL files from BodyParts3D) |
| **Pillow** | >=10.0.0 | Image processing |
| **pandas** | >=1.5.0 | Data management |
| **PyYAML** | >=6.0 | Configuration files |
| **imageio** | >=2.31.0 | Image I/O |
| **imageio-ffmpeg** | >=0.4.8 | Video/animation support |
| **requests** | >=2.31.0 | HTTP requests |
| **pytube** | >=15.0.0 | YouTube integration (future) |
| **youtubesearchpython** | latest | YouTube Short search — auto-installed on first use |

### Development Dependencies

| Package | Version | Purpose |
|---|---|---|
| **pytest** | >=7.4.0 | Testing framework |
| **black** | >=23.0.0 | Code formatting |
| **pylint** | >=3.0.0 | Code linting |

Note: `youtubesearchpython` is auto-installed the first time a user clicks "Search Tutorial on YouTube" on an exercise without a known video ID.

## Data Files

### Muscle Data (`data/muscle_data.json`)
Contains definitions for all muscle groups:
- ID and display name
- Anatomical location
- Description
- Color for visualization
- Mesh vertices and faces for 3D rendering

### Exercise Data (`data/exercise_data.json`)
Contains exercise definitions:
- Exercise name and ID
- Target muscles
- Equipment required
- Difficulty level
- Step-by-step instructions
- Tips and form cues
- Animation file path
- YouTube video ID

## Configuration

All configuration is centralized in `src/config.py`:
- Window dimensions
- Color scheme
- Data file paths
- UI labels and messages
- Performance thresholds

## Usage

### Using the Data Layer

```python
from src.data import DataLoader
from src.services import ExerciseService

# Load all exercises
loader = DataLoader()
exercises = loader.load_exercises()
muscles = loader.load_muscles()

# Get exercises for specific muscles
service = ExerciseService()
bicep_exercises = service.get_exercises_for_muscles(["biceps"])

# Filter exercises
filtered = service.get_exercises_by_muscles_and_filters(
    muscle_ids=["chest"],
    show_machines=True,
    show_bodyweight=False
)
```

### Using Services

```python
from src.services import YouTubeService, AnimationService

# Get YouTube URLs
video_url = YouTubeService.get_watch_url("dQw4w9WgXcQ")
search_url = YouTubeService.get_exercise_tutorial_url("Barbell Curl")

# Load animations
anim_service = AnimationService()
gif = anim_service.load_animation("barbell_curl.gif")
```

## Development Status

The application is complete and fully functional. All core features have been implemented:

- **Phase 1** (Data Layer): Complete — data models, loading, services, and filtering logic
- **Phase 2** (3D Visualization): Complete — Vispy integration with interactive 3D body model, mesh loading, and mouse-based muscle selection
- **Phase 3** (UI): Complete — PyQt6 main window, exercise list widget, and detailed exercise popup with photos and YouTube integration
- **Phase 4** (Integration): Complete — Signal-slot connections and state management
- **Phase 5** (Testing & Polish): Complete — unit tests, code quality standards (PEP 8, type hints, docstrings)

### Future Expansion Points

The following service stubs are in place for future enhancement:
- `YouTubeService` in `src/services/youtube_service.py` — for advanced YouTube integration
- `AnimationService` in `src/services/animation_service.py` — for animated exercise demonstrations

## Known Limitations

- No user account or workout history persistence
- YouTubeService and AnimationService stubs not yet wired into the UI
- No offline caching of YouTube search results or thumbnails

## Future Enhancements

- User workout tracking and history
- Custom workout creation
- Social features (share workouts)
- Mobile app version
- Video form checking with computer vision
- Nutrition planning integration

## Testing

The project includes comprehensive unit tests:

- **test_models.py** - Data model validation
- **test_data.py** - Data loading and processing
- **test_services.py** - Service layer business logic

Run tests with:
```bash
pytest -v
```

## Code Quality

The codebase follows:
- **PEP 8** style guidelines
- **Type hints** for all functions
- **Docstrings** for modules and functions
- **DRY** principles (no code duplication)
- **SOLID** principles where applicable

## Contributing

When adding features:
1. Follow the existing architecture and patterns
2. Add unit tests for new functionality
3. Update documentation
4. Ensure code passes linting and formatting checks

## Open-Source Credits

This project is built on top of several open-source projects:

### BodyParts3D Anatomical Models
- **License**: CC BY-SA 2.1 JP (Creative Commons Attribution-Share Alike)
- **Copyright**: Database Center for Life Science (DBCLS)
- **Source**: https://github.com/Kevin-Mattheus-Moerman/BodyParts3D
- **Citation**: Mitsuhashi N, et al. "BodyParts3D: 3D structure database for anatomical concepts." *Nucleic Acids Res.* 2009. https://doi.org/10.1093/nar/gkn613

### Exercise Database & Images
- **Project**: yuhonas/free-exercise-db
- **License**: Public Domain (Unlicense)
- **Source**: https://github.com/yuhonas/free-exercise-db
- **Purpose**: Exercise data, descriptions, and step-by-step instructional photos

### YouTube Search Library
- **Package**: youtubesearchpython
- **License**: MIT
- **PyPI**: https://pypi.org/project/youtubesearchpython/
- **Purpose**: Search YouTube for fitness videos without requiring an API key

For more details on all libraries and dependencies, see [CREDITS.md](CREDITS.md).

## License

MIT License - Feel free to use this project for educational and personal purposes.

Note: The 3D anatomical models are licensed under CC BY-SA 2.1 JP. Please see CREDITS.md for details.

## Support

For issues or questions, please check:
1. The code documentation and docstrings
2. Unit tests for usage examples
3. The project architecture overview in this README
