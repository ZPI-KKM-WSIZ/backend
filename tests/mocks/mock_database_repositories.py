from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from contracts.data_models.federation import Federation
from contracts.data_models.sensor_board import (
    Location,
    SensorBoard,
    SensorReading,
    Token,
)
from contracts.interfaces.repositories import (
    IFederationRepository,
    ILocationRepository,
    IReadingsRepository,
    IRepository,
    ISensorRepository,
    ITokenRepository,
)
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute the great-circle distance between two points using the Haversine formula.

    All coordinate inputs must be in decimal degrees. The result is always
    non-negative and represents the shortest path along the Earth's surface.

    Args:
        lat1: Latitude of the first point, in decimal degrees.
        lon1: Longitude of the first point, in decimal degrees.
        lat2: Latitude of the second point, in decimal degrees.
        lon2: Longitude of the second point, in decimal degrees.

    Returns:
        Distance in kilometres between the two points.
    """

    R = 6_371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


class MockBaseRepository(IRepository, Generic[T]):
    """
    Generic in-memory repository for use in tests and local development.

    Stores entities in a plain dict keyed by their `id` attribute.
    All operations are synchronous in behaviour but declared async to
    satisfy the IRepository interface. No data is persisted between runs.

    Attributes:
        storage: Internal dict mapping entity keys to stored entities.
    """

    def __init__(self) -> None:
        self.storage: dict[object, T] = {}

    async def save(self, entity: T) -> T:
        key = getattr(entity, "id", None)
        logging.debug(f"[MOCK SAVE] Would upsert entity into DB: {entity!r} (key={key!r})")
        self.storage[key] = entity
        return entity


class MockFederationRepository(MockBaseRepository[Federation], IFederationRepository):
    """
    In-memory test double for IFederationRepository.

    Now fully compliant with the IFederationRepository interface, supporting
    lookups by both UUID and token_id.
    """

    async def save(self, entity: Federation) -> Federation:
        """Saves or updates a federation using its UUID as the key."""
        key = entity.id
        logging.debug(f"[MOCK SAVE] Upserting federation: {entity!r} (id={key!r})")
        self.storage[key] = entity
        return entity

    async def get_by_id(self, id: UUID) -> None | Federation:
        """Get federation by its primary UUID."""
        return self.storage.get(id)

    async def get_by_token(self, token_id: str) -> None | Federation:
        """Search the storage for a federation matching the given token_id."""
        return next(
            (f for f in self.storage.values() if f.token_id == token_id),
            None
        )

    async def delete(self, id: UUID) -> None:
        """Delete a federation by its UUID."""
        logging.debug(f"[MOCK DELETE] Removing federation id={id}")
        self.storage.pop(id, None)

    async def get_all(self) -> list[Federation]:
        """Returns all stored federations."""
        return list(self.storage.values())

    async def get_or_create_unassigned(self) -> Federation:
        """
        Retrieves a default 'Unassigned' federation or creates one if it doesn't exist.
        This is a common pattern for handling entities not yet linked to a specific group.
        """
        unassigned_id = UUID("00000000-0000-0000-0000-000000000000")

        if unassigned_id not in self.storage:
            logging.info("[MOCK] Creating default unassigned federation.")
            new_fed = Federation(
                id=unassigned_id,
                token=[],
                trust_score=50,
                name="Unassigned Federation"
            )
            self.storage[unassigned_id] = new_fed

        return self.storage[unassigned_id]


class MockLocationRepository(MockBaseRepository[Location], ILocationRepository):
    """
    In-memory test double for ILocationRepository.

    Supports coordinate-based lookup and proximity search via the Haversine
    formula. Pagination always returns all items with no continuation token.
    """

    async def get_by_id(self, entity_id: UUID) -> Location | None:
        return self.storage.get(entity_id)

    async def get_by_coordinates(self, lat: float, lon: float) -> Location | None:
        return next(
            (
                loc for loc in self.storage.values()
                if getattr(loc, "lat", None) == lat and getattr(loc, "lon", None) == lon
            ),
            None,
        )

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

    async def find_nearest(
            self,
            target_lat: float,
            target_lon: float,
            radius_km: float,
            limit: int = 10,
    ) -> list[Location]:
        candidates: list[tuple[float, Location]] = []
        for loc in self.storage.values():
            lat = getattr(loc, "lat", None)
            lon = getattr(loc, "lon", None)
            if lat is None or lon is None:
                continue
            dist = _haversine_km(target_lat, target_lon, lat, lon)
            if dist <= radius_km:
                candidates.append((dist, loc))
        candidates.sort(key=lambda x: x[0])
        return [loc for _, loc in candidates[:limit]]


class MockReadingsRepository(MockBaseRepository[SensorReading], IReadingsRepository):
    """
    In-memory test double for IReadingsRepository.

    Supports bulk save, time-range filtering by sensor, latest-first retrieval,
    and deletion of readings older than a given timestamp. The `concurrency`
    and `max_retries` parameters of `save_bulk` are accepted but ignored.
    """

    async def save_bulk(
            self,
            entities: list[SensorReading],
            concurrency: int = 50,
            max_retries: int = 3,
    ) -> tuple[list[SensorReading], list[SensorReading]]:
        saved: list[SensorReading] = []
        for reading in entities:
            saved.append(await self.save(reading))
        return saved, []

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
    """
    In-memory test double for ISensorRepository.

    Supports lookup by sensor ID, by token string, and by location ID.
    Pagination always returns all matching items with no continuation token.
    """

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

    async def get_by_location(self, location_id: UUID, limit: int = 100) -> list[SensorBoard]:
        logging.debug(f"[MOCK QUERY] sensors by location location_id={location_id} limit={limit}")
        return [
            e for e in self.storage.values()
            if getattr(e, "location_id", None) == location_id
        ][:limit]


class MockTokenRepository(MockBaseRepository[Token], ITokenRepository):
    """
    In-memory test double for ITokenRepository.

    Overrides the default key strategy to use the `token` string as the
    storage key. Supports bulk save, lookup by token, and federation-scoped
    listing and deletion.
    """

    async def save(self, entity: Token) -> Token:
        key = getattr(entity, "token", None)
        logging.debug(f"[MOCK SAVE] Would upsert token: {entity!r} (token={key!r})")
        self.storage[key] = entity
        return entity

    async def save_bulk(self, entities: list[Token]) -> list[Token]:
        return [await self.save(t) for t in entities]

    async def get_by_token(self, token: str) -> Token | None:
        return self.storage.get(token)

    async def delete(self, token: str) -> None:
        logging.debug(f"[MOCK DELETE] token={token}")
        self.storage.pop(token, None)

    async def get_paginated_by_federation(
            self,
            federation_id: UUID,
            page_size: int = 100,
            paging_state: bytes | None = None,
    ) -> tuple[list[Token], bytes | None]:
        items = [
            e for e in self.storage.values()
            if getattr(e, "federation_id", None) == federation_id
        ]
        return items[:page_size], None

    async def get_by_federation(self, federation_id: UUID, limit: int = 100) -> list[Token]:
        return [
            e for e in self.storage.values()
            if getattr(e, "federation_id", None) == federation_id
        ][:limit]

    async def delete_by_federation(self, federation_id: UUID, token: str) -> None:
        logging.debug(f"[MOCK DELETE] token by federation federation_id={federation_id} token={token}")
        self.storage.pop(token, None)
