from __future__ import annotations

import logging
from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel

from contracts import IRepository
from contracts.data_models.backend import Backend, Error
from contracts.data_models.federation import Federation
from contracts.data_models.sensor_board import (
    Location,
    SensorBoard,
    SensorReading,
    SensorStatus,
    SensorVersion,
)
from contracts.data_models.shard import Shard, ShardRole
from contracts.interfaces.repositories.backend_repository import IBackendRepository
from contracts.interfaces.repositories.error_repository import IErrorRepository
from contracts.interfaces.repositories.federation_repository import IFederationRepository
from contracts.interfaces.repositories.location_repository import ILocationRepository
from contracts.interfaces.repositories.readings_repository import IReadingsRepository
from contracts.interfaces.repositories.sensor_repository import ISensorRepository
from contracts.interfaces.repositories.sensor_status_repository import ISensorStatusRepository
from contracts.interfaces.repositories.shard_repository import IShardRepository
from contracts.interfaces.repositories.shard_role_repository import IShardRoleRepository
from contracts.interfaces.repositories.version_repository import IVersionRepository

T = TypeVar("T", bound=BaseModel)


class MockBaseRepository(IRepository, Generic[T]):
    def __init__(self) -> None:
        self.storage: dict[object, T] = {}

    async def save(self, entity: T) -> T:
        key = getattr(entity, "id", None)
        logging.debug(f"[MOCK SAVE] Would upsert entity into DB: {entity!r} (key={key!r})")
        self.storage[key] = entity
        return entity


class MockBackendRepository(MockBaseRepository[Backend], IBackendRepository):
    async def get_by_id(self, entity_id: UUID) -> Backend | None:
        return self.storage.get(entity_id)

    async def delete(self, entity_id: UUID) -> None:
        logging.debug(f"[MOCK DELETE] backend id={entity_id}")
        self.storage.pop(entity_id, None)

    async def get_paginated(
        self,
        partition_key: UUID,
        page_size: int = 100,
        paging_state: bytes | None = None,
    ) -> tuple[list[Backend], bytes | None]:
        items = list(self.storage.values())
        return items[:page_size], None

    async def get_by_shard(
        self,
        shard_id: UUID,
        limit: int = 100,
    ) -> list[Backend]:
        logging.debug(f"[MOCK QUERY] get_by_shard shard_id={shard_id} limit={limit}")
        return list(self.storage.values())[:limit]


class MockErrorRepository(MockBaseRepository[Error], IErrorRepository):
    async def get_by_backend(
        self,
        backend_id: UUID,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 1000,
    ) -> list[Error]:
        results: list[Error] = []
        for e in self.storage.values():
            if getattr(e, "backend_id", None) != backend_id:
                continue
            ts: datetime = getattr(e, "timestamp")
            if start_time and ts < start_time:
                continue
            if end_time and ts > end_time:
                continue
            results.append(e)
            if len(results) >= limit:
                break
        return results

    async def delete_before_date(self, backend_id: UUID, before: datetime) -> None:
        logging.debug(f"[MOCK DELETE] errors backend_id={backend_id} before={before.isoformat()}")
        to_delete = [
            key for key, e in self.storage.items()
            if getattr(e, "backend_id", None) == backend_id
            and getattr(e, "timestamp") < before
        ]
        for key in to_delete:
            self.storage.pop(key, None)


class MockFederationRepository(MockBaseRepository[Federation], IFederationRepository):
    async def save(self, entity: Federation) -> Federation:
        key = getattr(entity, "token_id", None)
        logging.debug(f"[MOCK SAVE] Would upsert federation: {entity!r} (token_id={key!r})")
        self.storage[key] = entity
        return entity

    async def get_by_token_id(self, token_id: str) -> Federation | None:
        return self.storage.get(token_id)

    async def delete(self, token_id: str) -> None:
        logging.debug(f"[MOCK DELETE] federation token_id={token_id}")
        self.storage.pop(token_id, None)

    async def get_all(self) -> list[Federation]:
        return list(self.storage.values())


class MockLocationRepository(MockBaseRepository[Location], ILocationRepository):
    async def get_by_id(self, entity_id: UUID) -> Location | None:
        return self.storage.get(entity_id)

    async def delete(self, entity_id: UUID) -> None:
        logging.debug(f"[MOCK DELETE] location id={entity_id}")
        self.storage.pop(entity_id, None)

    async def get_paginated(
        self,
        partition_key: UUID,
        page_size: int = 100,
        paging_state: bytes | None = None,
    ) -> tuple[list[Location], bytes | None]:
        items = list(self.storage.values())
        return items[:page_size], None


class MockReadingsRepository(MockBaseRepository[SensorReading], IReadingsRepository):
    async def get_by_sensor(
        self,
        sensor_id: UUID,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 1000,
    ) -> list[SensorReading]:
        results: list[SensorReading] = []
        for e in self.storage.values():
            if getattr(e, "sensor_id", None) != sensor_id:
                continue
            ts: datetime = getattr(e, "timestamp")
            if start_time and ts < start_time:
                continue
            if end_time and ts > end_time:
                continue
            results.append(e)
            if len(results) >= limit:
                break
        return results

    async def get_latest(self, sensor_id: UUID, limit: int = 10) -> list[SensorReading]:
        readings = await self.get_by_sensor(sensor_id)
        readings.sort(key=lambda r: getattr(r, "timestamp"), reverse=True)
        return readings[:limit]

    async def delete_before_date(self, sensor_id: UUID, before: datetime) -> None:
        logging.debug(f"[MOCK DELETE] readings sensor_id={sensor_id} before={before.isoformat()}")
        to_delete = [
            key for key, e in self.storage.items()
            if getattr(e, "sensor_id", None) == sensor_id
            and getattr(e, "timestamp") < before
        ]
        for key in to_delete:
            self.storage.pop(key, None)


class MockSensorRepository(MockBaseRepository[SensorBoard], ISensorRepository):
    async def get_by_id(self, sensor_id: UUID) -> SensorBoard | None:
        return self.storage.get(sensor_id)

    async def delete(self, entity_id: UUID) -> None:
        logging.debug(f"[MOCK DELETE] sensor id={entity_id}")
        self.storage.pop(entity_id, None)

    async def get_paginated(
        self,
        partition_key: UUID,
        page_size: int = 100,
        paging_state: bytes | None = None,
    ) -> tuple[list[SensorBoard], bytes | None]:
        items = list(self.storage.values())
        return items[:page_size], None

    async def get_by_token(self, token: str) -> SensorBoard | None:
        return next(
            (e for e in self.storage.values() if getattr(e, "token", None) == token),
            None,
        )

    async def get_by_backend(self, backend_id: UUID, limit: int = 100) -> list[SensorBoard]:
        logging.debug(f"[MOCK QUERY] sensors by backend backend_id={backend_id} limit={limit}")
        return [
            e for e in list(self.storage.values())
            if getattr(e, "backend_id", None) == backend_id
        ][:limit]

    async def get_by_location(self, location_id: UUID, limit: int = 100) -> list[SensorBoard]:
        logging.debug(f"[MOCK QUERY] sensors by location location_id={location_id} limit={limit}")
        return [
            e for e in list(self.storage.values())
            if getattr(e, "location_id", None) == location_id
        ][:limit]


class MockSensorStatusRepository(MockBaseRepository[SensorStatus], ISensorStatusRepository):
    async def get_by_id(self, entity_id: UUID) -> SensorStatus | None:
        return self.storage.get(entity_id)

    async def delete(self, entity_id: UUID) -> None:
        logging.debug(f"[MOCK DELETE] sensor_status id={entity_id}")
        self.storage.pop(entity_id, None)

    async def get_all(self) -> list[SensorStatus]:
        return list(self.storage.values())


class MockShardRepository(MockBaseRepository[Shard], IShardRepository):
    async def get_by_id(self, entity_id: UUID) -> Shard | None:
        return self.storage.get(entity_id)

    async def delete(self, entity_id: UUID) -> None:
        logging.debug(f"[MOCK DELETE] shard id={entity_id}")
        self.storage.pop(entity_id, None)

    async def get_paginated(
        self,
        partition_key: UUID,
        page_size: int = 100,
        paging_state: bytes | None = None,
    ) -> tuple[list[Shard], bytes | None]:
        items = list(self.storage.values())
        return items[:page_size], None

    async def get_by_parent(self, parent_id: UUID, limit: int = 100) -> list[Shard]:
        logging.debug(f"[MOCK QUERY] shard by parent parent_id={parent_id} limit={limit}")
        return [
            e for e in list(self.storage.values())
            if getattr(e, "parent_id", None) == parent_id
        ][:limit]

    async def get_all(self) -> list[Shard]:
        return list(self.storage.values())


class MockShardRoleRepository(MockBaseRepository[ShardRole], IShardRoleRepository):
    async def get_by_id(self, entity_id: UUID) -> ShardRole | None:
        return self.storage.get(entity_id)

    async def delete(self, entity_id: UUID) -> None:
        logging.debug(f"[MOCK DELETE] shard_role id={entity_id}")
        self.storage.pop(entity_id, None)

    async def get_all(self) -> list[ShardRole]:
        return list(self.storage.values())


class MockVersionRepository(MockBaseRepository[SensorVersion], IVersionRepository):
    async def get_by_id(self, entity_id: UUID) -> SensorVersion | None:
        return self.storage.get(entity_id)

    async def delete(self, entity_id: UUID) -> None:
        logging.debug(f"[MOCK DELETE] version id={entity_id}")
        self.storage.pop(entity_id, None)

    async def get_all(self) -> list[SensorVersion]:
        return list(self.storage.values())
