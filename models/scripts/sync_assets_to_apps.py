"""Copy benchmark assets into Flutter and Android Native harness apps.

Assets copied:
- assets/inputs/vision -> apps/*/assets/inputs/vision
- assets/inputs/text.jsonl -> apps/*/assets/inputs/text.jsonl
- models/*.tflite -> apps/*/assets/models/
"""

import shutil
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[2]
    models_dir = root / "models"
    inputs_dir = root / "assets" / "inputs"

    destinations = [
        root / "apps" / "flutter_bench" / "assets",
        root / "apps" / "android_native_bench" / "app" / "src" / "main" / "assets"
    ]

    for dest in destinations:
        dest_inputs = dest / "inputs"
        dest_models = dest / "models"

        dest_inputs.mkdir(parents=True, exist_ok=True)
        dest_models.mkdir(parents=True, exist_ok=True)

        # Copy inputs/vision
        dest_vision = dest_inputs / "vision"
        if dest_vision.exists():
            shutil.rmtree(dest_vision)
        shutil.copytree(inputs_dir / "vision", dest_vision)

        # Copy text.jsonl
        shutil.copy2(inputs_dir / "text.jsonl", dest_inputs / "text.jsonl")

        # Copy models
        for model_file in models_dir.glob("*.tflite"):
            shutil.copy2(model_file, dest_models / model_file.name)

        print(f"Copied inputs and models to {dest}")


if __name__ == "__main__":
    main()

