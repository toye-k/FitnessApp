"""
Fitness Exercise Trainer Application

A Python application for fitness training that provides 3D visualization of exercises
and muscle groups with detailed instructions and tutorials.
"""

__version__ = "1.0.0"
__author__ = "Fitness App Developer"

from . import config
from . import models
from . import data
from . import services
from . import utils

__all__ = [
    "config",
    "models",
    "data",
    "services",
    "utils",
]
