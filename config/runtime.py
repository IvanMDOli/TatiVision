import sys
from pathlib import Path


APP_DIR = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent.parent
)


def resolve_app_path(path):
    if not path:
        return ""

    resolved_path = Path(path)
    if not resolved_path.is_absolute():
        resolved_path = APP_DIR / resolved_path

    return str(resolved_path)


def resource_path(path):
    bundle_directory = Path(
        getattr(sys, "_MEIPASS", APP_DIR)
    )
    return bundle_directory / path
