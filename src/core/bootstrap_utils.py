import tomllib
from pathlib import Path


def get_app_version(root_dir: Path) -> str:
    poetry_path = root_dir / "pyproject.toml"
    with poetry_path.open("rb") as f:
        data = tomllib.load(f)
        version = data["project"]["version"]
    return version
