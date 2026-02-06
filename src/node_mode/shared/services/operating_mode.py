from src.core.config import state, OperatingMode


class SharedNodeService:
    def get_operating_mode(self) -> OperatingMode:
        """Retrieve the current operating mode."""
        return state.operating_mode

    def get_app_version(self):
        return state.app_version