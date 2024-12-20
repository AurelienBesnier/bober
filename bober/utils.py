import os
from pathlib import Path


def assets_folder():
    path = os.path.join(str(Path(__file__).parent.resolve()), "assets")

    return path


def bober_path():
    return os.path.join(assets_folder(), "bober", "bober.png")
