"""
Load BodyParts3D muscle models as isolated, selectable objects.
Maintains correct positioning and allows individual muscle selection.
"""

import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)

try:
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False


class IsolatedMusclesLoader:
    """Load individual muscle models that maintain their positions."""

    # FMA IDs to EXCLUDE (organs, nerves, skin, hair, genitalia)
    EXCLUDE_FMA_IDS = {
        # Integument
        7163,    # Skin
        53667,   # Hair
        10464,   # Skin of breast

        # Major organs
        7088,    # Heart
        7197,    # Liver
        7148,    # Stomach
        7203,    # Kidney
        7195,    # Lung
        7274,    # Spleen
        7214,    # Esophagus
        7394,    # Rectum

        # Nervous system
        50801,   # Brain
        50802,   # Spinal cord
        50803,   # Cauda equina
        7647,    # Cerebral hemisphere

        # Reproductive/Genital organs
        7210,    # Testis
        7209,    # Ovary
        17558,   # Uterus
        18252,   # Scrotum
        9707,    # Penis
        9909,    # Clitoris
        18256,   # Testis (alternate)
        18400,   # Ovary (alternate)
        18592,   # Uterus (alternate)
        19612,   # Penis (alternate)
        20045,   # Clitoris (alternate)

        # Breasts
        9601,    # Breast
        268893,  # Set of breasts
        268898,  # Set of female breasts
        268896,  # Set of male breasts
        19910,   # Left female breast
    }

    # Map FMA codes to muscle names (verified against parts_list_e.txt + STL file existence)
    MUSCLE_NAMES = {
        # Chest - pectoralis major parts
        'fma34690': 'pectoralis_major_right',
        'fma34691': 'pectoralis_major_left',
        'fma79979': 'pectoralis_major_sternocostal_right',
        'fma79980': 'pectoralis_major_sternocostal_left',
        'fma45874': 'pectoralis_major_abdominal_right',
        'fma45875': 'pectoralis_major_abdominal_left',
        # Shoulders - deltoid parts
        'fma34680': 'deltoid_clavicular_right',
        'fma34681': 'deltoid_clavicular_left',
        'fma34682': 'deltoid_acromial_right',
        'fma34683': 'deltoid_acromial_left',
        'fma34684': 'deltoid_spinal_right',
        'fma34685': 'deltoid_spinal_left',
        # Back - trapezius parts
        'fma33581': 'trapezius_ascending_right',
        'fma33583': 'trapezius_ascending_left',
        'fma33584': 'trapezius_transverse_right',
        'fma33585': 'trapezius_transverse_left',
        'fma33586': 'trapezius_descending_right',
        'fma33587': 'trapezius_descending_left',
        # Back - latissimus dorsi
        'fma13358': 'latissimus_dorsi_right',
        'fma13359': 'latissimus_dorsi_left',
        # Arms - biceps brachii
        'fma37684': 'biceps_brachii_short_right',
        'fma37685': 'biceps_brachii_short_left',
        'fma37686': 'biceps_brachii_long_right',
        'fma37687': 'biceps_brachii_long_left',
        # Arms - triceps brachii
        'fma37695': 'triceps_brachii_medial_right',
        'fma37696': 'triceps_brachii_medial_left',
        'fma37697': 'triceps_brachii_lateral_right',
        'fma37698': 'triceps_brachii_lateral_left',
        'fma37699': 'triceps_brachii_long_right',
        'fma37700': 'triceps_brachii_long_left',
        # Glutes
        'fma22328': 'gluteus_maximus_right',
        'fma22329': 'gluteus_maximus_left',
        'fma22330': 'gluteus_medius_right',
        'fma22331': 'gluteus_medius_left',
        'fma22332': 'gluteus_minimus_right',
        'fma22333': 'gluteus_minimus_left',
        # Quadriceps
        'fma38928': 'rectus_femoris_right',
        'fma38929': 'rectus_femoris_left',
        'fma38932': 'vastus_medialis_right',
        'fma38933': 'vastus_medialis_left',
        # Hamstrings
        'fma45888': 'biceps_femoris_long_right',
        'fma45889': 'biceps_femoris_long_left',
        'fma45891': 'biceps_femoris_short_right',
        'fma45892': 'biceps_femoris_short_left',
        'fma22358': 'semitendinosus_right',
        'fma22359': 'semitendinosus_left',
        'fma22448': 'semimembranosus_right',
        'fma22449': 'semimembranosus_left',
        # Hip adductors
        'fma22452': 'adductor_brevis_right',
        'fma22454': 'adductor_brevis_left',
        'fma22456': 'adductor_longus_right',
        'fma22457': 'adductor_longus_left',
        'fma22459': 'adductor_magnus_right',
        'fma22460': 'adductor_magnus_left',
        # Hip flexors - sartorius
        'fma22354': 'sartorius_right',
        'fma22355': 'sartorius_left',
        # Calves - gastrocnemius
        'fma45957': 'gastrocnemius_medial_right',
        'fma45958': 'gastrocnemius_medial_left',
        'fma45960': 'gastrocnemius_lateral_right',
        'fma45961': 'gastrocnemius_lateral_left',
        # Calves - soleus
        'fma22558': 'soleus_right',
        'fma22559': 'soleus_left',
        # Shins - tibialis anterior
        'fma22544': 'tibialis_anterior_right',
        'fma22545': 'tibialis_anterior_left',
        # Abs - rectus abdominis
        'fma13377': 'rectus_abdominis_right',
        'fma13378': 'rectus_abdominis_left',
        # Abs - external oblique
        'fma13336': 'external_oblique_right',
        'fma13337': 'external_oblique_left',
        # Abs - internal oblique
        'fma13892': 'internal_oblique_right',
        'fma13893': 'internal_oblique_left',
        # Abs - transversus abdominis
        'fma22344': 'transversus_abdominis_right',
        'fma22345': 'transversus_abdominis_left',
        # Forearms
        'fma38486': 'brachioradialis_right',
        'fma38487': 'brachioradialis_left',
        'fma38460': 'flexor_carpi_radialis_right',
        'fma38461': 'flexor_carpi_radialis_left',
        'fma38495': 'extensor_carpi_radialis_longus_right',
        'fma38496': 'extensor_carpi_radialis_longus_left',
        'fma38507': 'extensor_carpi_ulnaris_right',
        'fma38508': 'extensor_carpi_ulnaris_left',
        'fma38560': 'pronator_teres_right',
        'fma38561': 'pronator_teres_left',
        'fma38479': 'flexor_digitorum_profundus_right',
        'fma38480': 'flexor_digitorum_profundus_left',
    }

    @staticmethod
    def should_exclude(stl_file: Path) -> bool:
        """Check if a file should be excluded based on FMA code."""
        code = stl_file.stem.lower()

        # Keep all BodyParts (BP) codes - they're manually curated
        if code.startswith('bp'):
            return False

        # For FMA codes, exclude known organs/nerves/skin
        if code.startswith('fma'):
            try:
                fma_id = int(code[3:])
                return fma_id in IsolatedMusclesLoader.EXCLUDE_FMA_IDS
            except ValueError:
                return False

        return False

    @staticmethod
    def find_stl_directory() -> Optional[Path]:
        """Find BodyParts3D STL directory."""
        possible_paths = [
            Path("assets/BodyParts3D-main/assets/BodyParts3D_data/stl"),
            Path("assets/models/BodyParts3D-main/assets/BodyParts3D_data/stl"),
            Path("assets/models/bodyparts/stl"),
            Path("BodyParts3D-main/assets/BodyParts3D_data/stl"),
        ]

        for path in possible_paths:
            if path.exists():
                stl_count = len(list(path.glob("*.stl")))
                if stl_count > 0:
                    logger.info(f"Found {stl_count} STL files in {path}")
                    return path

        return None

    @staticmethod
    def load_muscle_models() -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """
        Load individual muscle models while preserving their spatial positions.

        Returns:
            Dictionary mapping muscle names to (vertices, faces) tuples
        """
        if not TRIMESH_AVAILABLE:
            logger.error("trimesh not available")
            return {}

        stl_dir = IsolatedMusclesLoader.find_stl_directory()
        if not stl_dir:
            logger.warning("STL directory not found")
            return {}

        # Load all muscle STLs
        all_vertices = []
        all_faces = []
        muscle_bounds = {}
        vertex_offset = 0

        # First pass: load all files and determine bounds
        loaded_files = []
        for stl_file in sorted(stl_dir.glob("*.stl")):
            try:
                mesh = trimesh.load(str(stl_file))
                if mesh.vertices.size == 0:
                    continue

                loaded_files.append((stl_file, mesh))
            except Exception as e:
                logger.debug(f"Failed to load {stl_file}: {e}")

        if not loaded_files:
            logger.error("No STL files loaded")
            return {}

        logger.info(f"Loaded {len(loaded_files)} STL files")

        # Calculate global bounds for proper normalization
        all_verts = np.vstack([mesh.vertices for _, mesh in loaded_files])
        global_min = all_verts.min(axis=0)
        global_max = all_verts.max(axis=0)
        global_center = (global_min + global_max) / 2
        global_scale = np.max(global_max - global_min)

        logger.info(f"Global bounds: {global_scale}")

        # Second pass: normalize while preserving relative positions
        muscle_models = {}
        for stl_file, mesh in loaded_files:
            try:
                vertices = mesh.vertices.astype(np.float32)
                faces = mesh.faces.astype(np.uint32)

                # Normalize: center and scale globally (preserves relative positions)
                vertices = (vertices - global_center) / global_scale * 2

                # Get muscle name
                muscle_id = stl_file.stem.lower()
                muscle_name = IsolatedMusclesLoader.MUSCLE_NAMES.get(
                    muscle_id, muscle_id
                )

                muscle_models[muscle_name] = (vertices, faces)
                muscle_bounds[muscle_name] = {
                    'min': vertices.min(axis=0),
                    'max': vertices.max(axis=0),
                }
            except Exception as e:
                logger.debug(f"Failed to process {stl_file}: {e}")

        logger.info(f"Prepared {len(muscle_models)} muscle models")
        return muscle_models

    # Map individual muscles to anatomical groups
    MUSCLE_GROUPS = {
        'chest': [
            'pectoralis_major_right', 'pectoralis_major_left',
            'pectoralis_major_sternocostal_right', 'pectoralis_major_sternocostal_left',
            'pectoralis_major_abdominal_right', 'pectoralis_major_abdominal_left',
        ],
        'shoulders': [
            'deltoid_clavicular_right', 'deltoid_clavicular_left',
            'deltoid_acromial_right', 'deltoid_acromial_left',
            'deltoid_spinal_right', 'deltoid_spinal_left',
        ],
        'upper_back': [
            'trapezius_ascending_right', 'trapezius_ascending_left',
            'trapezius_transverse_right', 'trapezius_transverse_left',
            'trapezius_descending_right', 'trapezius_descending_left',
        ],
        'lats': [
            'latissimus_dorsi_right', 'latissimus_dorsi_left',
        ],
        'biceps': [
            'biceps_brachii_short_right', 'biceps_brachii_short_left',
            'biceps_brachii_long_right', 'biceps_brachii_long_left',
        ],
        'triceps': [
            'triceps_brachii_medial_right', 'triceps_brachii_medial_left',
            'triceps_brachii_lateral_right', 'triceps_brachii_lateral_left',
            'triceps_brachii_long_right', 'triceps_brachii_long_left',
        ],
        'gluteus_maximus': [
            'gluteus_maximus_right', 'gluteus_maximus_left',
        ],
        'gluteus_medius': [
            'gluteus_medius_right', 'gluteus_medius_left',
        ],
        'gluteus_minimus': [
            'gluteus_minimus_right', 'gluteus_minimus_left',
        ],
        'quadriceps': [
            'rectus_femoris_right', 'rectus_femoris_left',
            'vastus_medialis_right', 'vastus_medialis_left',
        ],
        'hamstrings': [
            'biceps_femoris_long_right', 'biceps_femoris_long_left',
            'biceps_femoris_short_right', 'biceps_femoris_short_left',
            'semitendinosus_right', 'semitendinosus_left',
            'semimembranosus_right', 'semimembranosus_left',
        ],
        'hip_adductors': [
            'adductor_brevis_right', 'adductor_brevis_left',
            'adductor_longus_right', 'adductor_longus_left',
            'adductor_magnus_right', 'adductor_magnus_left',
        ],
        'hip_flexors': ['sartorius_right', 'sartorius_left'],
        'calves': [
            'gastrocnemius_medial_right', 'gastrocnemius_medial_left',
            'gastrocnemius_lateral_right', 'gastrocnemius_lateral_left',
            'soleus_right', 'soleus_left',
        ],
        'shins': ['tibialis_anterior_right', 'tibialis_anterior_left'],
        'upper_abs': [
            'rectus_abdominis_right', 'rectus_abdominis_left',
        ],
        'lower_abs': [
            'transversus_abdominis_right', 'transversus_abdominis_left',
        ],
        'obliques': [
            'external_oblique_right', 'external_oblique_left',
            'internal_oblique_right', 'internal_oblique_left',
        ],
        'forearms': [
            'brachioradialis_right', 'brachioradialis_left',
            'flexor_carpi_radialis_right', 'flexor_carpi_radialis_left',
            'extensor_carpi_radialis_longus_right', 'extensor_carpi_radialis_longus_left',
            'extensor_carpi_ulnaris_right', 'extensor_carpi_ulnaris_left',
            'pronator_teres_right', 'pronator_teres_left',
            'flexor_digitorum_profundus_right', 'flexor_digitorum_profundus_left',
        ],
    }

    @staticmethod
    def get_major_muscles() -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """
        Load only major muscle groups (subset for performance).

        Returns:
            Dictionary of major muscle models
        """
        if not TRIMESH_AVAILABLE:
            logger.error("trimesh not available")
            return {}

        stl_dir = IsolatedMusclesLoader.find_stl_directory()
        if not stl_dir:
            logger.warning("STL directory not found")
            return {}

        # Calculate global bounds first
        all_loaded = []
        for stl_file in sorted(stl_dir.glob("*.stl")):
            try:
                mesh = trimesh.load(str(stl_file))
                if mesh.vertices.size > 0:
                    all_loaded.append((stl_file, mesh))
            except:
                pass

        if not all_loaded:
            logger.error("No STL files could be loaded")
            return {}

        all_verts = np.vstack([mesh.vertices for _, mesh in all_loaded])
        global_min = all_verts.min(axis=0)
        global_max = all_verts.max(axis=0)
        global_center = (global_min + global_max) / 2
        global_scale = np.max(global_max - global_min)

        # Load only known muscles (whitelist)
        individual_muscles = {}

        for stl_file, mesh in all_loaded:
            try:
                # Skip excluded structures
                if IsolatedMusclesLoader.should_exclude(stl_file):
                    continue

                muscle_id = stl_file.stem.lower()

                # Only keep muscles in MUSCLE_NAMES (whitelist)
                if muscle_id not in IsolatedMusclesLoader.MUSCLE_NAMES:
                    continue

                vertices = mesh.vertices.astype(np.float32)
                faces = mesh.faces.astype(np.uint32)

                # Normalize globally
                vertices = (vertices - global_center) / global_scale * 2

                muscle_name = IsolatedMusclesLoader.MUSCLE_NAMES[muscle_id]
                individual_muscles[muscle_name] = (vertices, faces)

            except Exception as e:
                logger.debug(f"Failed to process {stl_file}: {e}")

        # Group muscles by anatomical area
        grouped_muscles = {}
        for group_name, muscle_list in IsolatedMusclesLoader.MUSCLE_GROUPS.items():
            group_vertices = []
            group_faces = []
            vertex_offset = 0

            for muscle_name in muscle_list:
                if muscle_name in individual_muscles:
                    verts, faces = individual_muscles[muscle_name]
                    group_vertices.append(verts)
                    # Offset face indices for each new mesh
                    group_faces.append(faces + vertex_offset)
                    vertex_offset += len(verts)

            # Combine if group has muscles
            if group_vertices:
                combined_verts = np.vstack(group_vertices).astype(np.float32)
                combined_faces = np.vstack(group_faces).astype(np.uint32)
                grouped_muscles[group_name] = (combined_verts, combined_faces)

        logger.info(f"Loaded {len(individual_muscles)} individual muscles grouped into {len(grouped_muscles)} muscle groups")
        return grouped_muscles
