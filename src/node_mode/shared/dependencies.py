from src.node_mode.shared.services.operating_mode import SharedNodeService


def get_node_service() -> SharedNodeService:
    return SharedNodeService()
