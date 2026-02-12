from src.fast_api.services.info import InfoService


def get_info_service() -> InfoService:
    return InfoService()
