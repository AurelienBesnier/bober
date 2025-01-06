from pathlib import Path


def assets_folder():
    path = Path(__file__).parent.resolve() / "assets"

    return path


def bober_path():
    return Path(assets_folder(), "bober", "bober.png")
