import tomllib
from pathlib import Path


def get_app_version(root_dir: Path) -> str:
    """
    Extracts the application version from the pyproject.toml file.
    
    Args:
        root_dir: Path to the project root directory containing pyproject.toml.
        
    Returns:
        The version string defined in the project configuration.
        
    Raises:
        RuntimeError: If the version cannot be retrieved due to missing file,
                     missing version key, or invalid TOML format.
    """
    try:
        poetry_path = root_dir / "pyproject.toml"
        with poetry_path.open("rb") as f:
            data = tomllib.load(f)
            version = data["project"]["version"]
        return version
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError) as e:
        raise RuntimeError(f"Failed to retrieve app version: {e}")
