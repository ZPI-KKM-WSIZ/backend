from src.core.config import state


class InfoService:
    def get_app_version(self):
        return state.app_version
