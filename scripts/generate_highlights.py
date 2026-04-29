"""
Generate muscle highlight screenshots for assets/highlights/.
Renders the 3D body model with each muscle group highlighted in red.
"""

import sys
import os
sys.path.insert(0, os.getcwd())

import numpy as np
from pathlib import Path

# Use offscreen rendering
try:
    from vispy import use as vispy_use
    vispy_use('egl')
except Exception:
    try:
        vispy_use('osmesa')
    except Exception:
        vispy_use('pyqt6')

from vispy import scene
from vispy.scene import visuals
from vispy.visuals.filters import ShadingFilter
from PIL import Image

from src.visualization.isolated_muscles_loader import IsolatedMusclesLoader

OUT_DIR = Path("assets/highlights")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Muscles that should be rendered from back view
BACK_VIEW_MUSCLES = {
    'upper_back', 'lats', 'lower_back',
    'gluteus_maximus', 'gluteus_medius', 'gluteus_minimus',
    'hamstrings'
}

# All muscles from muscle_data.json in order
ALL_MUSCLES = [
    'chest', 'shoulders', 'biceps', 'triceps', 'forearms',
    'upper_back', 'lats', 'lower_back',
    'upper_abs', 'lower_abs', 'obliques',
    'gluteus_maximus', 'gluteus_medius', 'gluteus_minimus',
    'quadriceps', 'hamstrings', 'hip_flexors', 'calves'
]

# Color values from body_viewer.py
COLOR_DEFAULT = (0.7, 0.5, 0.4, 0.9)      # Default skin tone
COLOR_HIGHLIGHT = (1.0, 0.2, 0.2, 1.0)    # Red highlight


def get_azimuth(muscle_name: str) -> int:
    """Get camera azimuth angle for muscle (front or back view)."""
    return 225 if muscle_name in BACK_VIEW_MUSCLES else 45


def render_highlight(muscle_all_meshes: dict, target_muscle: str) -> np.ndarray:
    """Render one muscle group highlighted, all others in default color."""
    canvas = scene.SceneCanvas(size=(800, 600), bgcolor='black', show=False)
    view = canvas.central_widget.add_view()

    azimuth = get_azimuth(target_muscle)
    view.camera = scene.cameras.TurntableCamera(
        distance=3.0, elevation=30, azimuth=azimuth
    )

    # Add all meshes
    for muscle_name, (vertices, faces) in muscle_all_meshes.items():
        # Use highlight color for target muscle, default for others
        color = COLOR_HIGHLIGHT if muscle_name == target_muscle else COLOR_DEFAULT

        mesh = visuals.Mesh(
            vertices=vertices,
            faces=faces,
            color=color,
            shading=None
        )
        mesh.attach(ShadingFilter(shading='smooth', light_dir=(0, 0, 2)))
        view.add(mesh)

    # Render and return RGBA array
    img = canvas.render()
    return img


if __name__ == "__main__":
    print("Generating muscle highlight screenshots...\n")

    # Load all muscle meshes once
    print("  Loading mesh data...", end=" ")
    all_meshes = IsolatedMusclesLoader.get_major_muscles()
    if not all_meshes:
        print("[ERROR] Failed to load muscle meshes")
        sys.exit(1)
    print(f"[OK] ({len(all_meshes)} muscle groups)")

    generated_count = 0
    skipped_count = 0

    for muscle_name in ALL_MUSCLES:
        output_file = OUT_DIR / f"{muscle_name}.png"

        # Skip if already exists
        if output_file.exists():
            print(f"  {muscle_name}.png — [SKIP] already exists")
            skipped_count += 1
            continue

        try:
            print(f"  {muscle_name}.png — rendering...", end=" ")

            # Special case: lower_back has no mesh in MUSCLE_GROUPS
            # Render all muscles in default color to show back of body
            if muscle_name == 'lower_back' or muscle_name not in all_meshes:
                # For lower_back or any muscle not in the loader, render all in default
                canvas = scene.SceneCanvas(size=(800, 600), bgcolor='black', show=False)
                view = canvas.central_widget.add_view()
                view.camera = scene.cameras.TurntableCamera(
                    distance=3.0, elevation=30, azimuth=225  # back view
                )
                for mname, (vertices, faces) in all_meshes.items():
                    mesh = visuals.Mesh(
                        vertices=vertices, faces=faces,
                        color=COLOR_DEFAULT, shading=None
                    )
                    mesh.attach(ShadingFilter(shading='smooth', light_dir=(0, 0, 2)))
                    view.add(mesh)
                img = canvas.render()
            else:
                # Render with target muscle highlighted
                img = render_highlight(all_meshes, muscle_name)

            Image.fromarray(img).save(output_file)
            print(f"[OK] ({img.shape[0]}x{img.shape[1]})")
            generated_count += 1

        except Exception as e:
            print(f"[ERROR] {e}")

    print(f"\nDone. Generated: {generated_count}, Skipped: {skipped_count}")
    print(f"Output: {OUT_DIR}/")
