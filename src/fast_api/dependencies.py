from src.fast_api.services.info import InfoService


def get_node_service() -> InfoService:
    return InfoService()
