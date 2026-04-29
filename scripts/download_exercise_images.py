"""Download step-by-step exercise images from yuhonas/free-exercise-db (public domain)."""
import json, urllib.request, pathlib, time

BASE_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises"
DATA_FILE = "data/exercise_data.json"
OUT_DIR = pathlib.Path("assets/images")

# Manual overrides where our exercise name doesn't match free-exercise-db folder name
NAME_MAP = {
    # Arms
    "barbell_curl":             "Barbell_Curl",
    "dumbbell_curl":            "Dumbbell_Bicep_Curl",
    "hammer_curl":              "Dumbbell_Hammer_Curl",
    "triceps_dips":             "Dips_-_Triceps_Version",
    "skull_crushers":           "Lying_Triceps_Press",
    "cable_triceps_pushdown":   "Triceps_Pushdown",
    "incline_dumbbell_press":   "Dumbbell_Incline_Bench_Press",

    # Chest
    "push_ups":                 "Pushups",
    "barbell_bench_press":      "Barbell_Bench_Press",
    "dumbbell_bench_press":     "Dumbbell_Bench_Press",
    "cable_chest_fly":          "Cable_Fly",

    # Back
    "deadlift":                 "Barbell_Deadlift",
    "bent_over_row":            "Bent_Over_Barbell_Row",
    "seated_row":               "Seated_Cable_Rows",
    "lat_pulldown":             "Full_Range-Of-Motion_Lat_Pulldown",
    "dumbbell_row":             "Bent_Over_One-Arm_Dumbbell_Row",
    "back_extension":           "Hyperextensions_Back_Extensions",
    "good_mornings":            "Good_Morning",

    # Shoulders
    "dumbbell_shoulder_press":  "Dumbbell_Shoulder_Press",
    "lateral_raises":           "Dumbbell_Lateral_Raise",

    # Legs
    "squats":                   "Barbell_Full_Squat",
    "leg_press":                "Leg_Press",
    "leg_extension":            "Leg_Extension",
    "romanian_deadlift":        "Romanian_Deadlift",
    "hip_thrust":               "Barbell_Hip_Thrust",
    "glute_bridges":            "Barbell_Glute_Bridge",
    "calf_raises":              "Calf_Raise_On_A_Dumbbell",

    # Core
    "plank":                    "Plank",
    "side_plank":               "Push_Up_to_Side_Plank",
    "crunches":                 "Crunches",
    "leg_raises":               "Flat_Bench_Lying_Leg_Raise",
    "russian_twists":           "Russian_Twist",
    "hip_flexor_raises":        "Standing_Hip_Flexors",

    # Misc
    "farmers_carry":            "Farmers_Walk",
    "wrist_curls":              "Wrist_Roller",
    "clamshells":               "Thigh_Abductor",

    # Stretches
    "hip_flexor_stretch":       "Kneeling_Hip_Flexor",
    "hamstring_stretch":        "Hamstring_Stretch",
    "quad_stretch":             "Quad_Stretch",
    "calf_stretch":             "Calf_Stretch_Hands_Against_Wall",
    "chest_stretch":            "Chest_Stretch_on_Stability_Ball",
    "shoulder_cross_stretch":   "Shoulder_Stretch",
    "triceps_overhead_stretch": "Triceps_Stretch",
    "lower_back_stretch":       "Childs_Pose",
    "lat_stretch":              "Standing_Lateral_Stretch",
    "glute_stretch":            "Lying_Glute",
}


def repo_name(exercise_id: str) -> str:
    """Convert exercise_id to free-exercise-db folder name."""
    if exercise_id in NAME_MAP:
        return NAME_MAP[exercise_id]
    # Fallback: Title_Case
    return "_".join(w.capitalize() for w in exercise_id.split("_"))


def download_exercise(exercise_id: str) -> int:
    """Download images for a single exercise. Returns count of images downloaded."""
    folder = OUT_DIR / exercise_id
    folder.mkdir(parents=True, exist_ok=True)
    repo = repo_name(exercise_id)
    count = 0
    for step in range(4):  # try up to 4 steps
        url = f"{BASE_URL}/{repo}/{step}.jpg"
        dest = folder / f"{step}.jpg"
        if dest.exists():
            count += 1
            continue
        try:
            urllib.request.urlretrieve(url, dest)
            count += 1
            time.sleep(0.1)  # be polite to GitHub CDN
        except Exception:
            break  # stop when no more steps exist
    return count


if __name__ == "__main__":
    with open(DATA_FILE) as f:
        exercises = json.load(f)["exercises"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for ex in exercises:
        eid = ex["id"]
        n = download_exercise(eid)
        print(f"  {eid}: {n} image(s)")
        total += n
    print(f"\nDone. {total} images saved to {OUT_DIR}/")
