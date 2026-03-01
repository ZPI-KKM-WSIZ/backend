# API Reference

Base path: `/api/v1`

> [!WARNING] This backend is under active development. Additional endpoints (federation and others) are not yet
> available.

---

## `GET /`

Root health check. Returns a minimal status object.

**Response `200 OK`**

```json
{
  "status": "ok"
}
```

---

## `GET /api/v1/health`

Health check. Returns service status and the identity of the responding node — useful for confirming which replica
handled a request when running multiple nodes.

**Response `200 OK`**

```json
{
  "status": "ok",
  "version": "0.1.0",
  "identity": "<server-id>"
}
```

---

## `POST /api/v1/readings`

Submit a single sensor reading. The node resolves the sensor by its registered token, finds or creates a matching
location by coordinates (within a 10 m radius), and persists the reading to Cassandra via the repository layer.

**Request body:** `SensorReadingDTO` (contract defined in `cassandra-repositories`)

**Response `201 Created`:** The persisted `SensorReading` model

**Error responses:**

| Status | Reason                                                 |
|--------|--------------------------------------------------------|
| `500`  | Sensor token not registered (`ConversionException`)    |
| `500`  | DTO-to-model conversion failed (`ConversionException`) |
| `500`  | Database insert failure (`ReadingInsertException`)     |

---

## `GET /api/v1/readings`

Retrieve sensor readings for a given sensor, with optional time range filtering.

**Query parameters:**

| Parameter    | Type       | Required | Description                                           |
|--------------|------------|----------|-------------------------------------------------------|
| `sensor_id`  | `UUID`     | ✅ Yes    | UUID of the sensor to fetch readings for              |
| `start_time` | `datetime` | ❌ No     | Filter readings on or after this timestamp            |
| `end_time`   | `datetime` | ❌ No     | Filter readings on or before this timestamp           |
| `limit`      | `int`      | ❌ No     | Maximum number of results to return (default: `1000`) |

**Response `201 Created`:** List of `SensorReading` models

> [!NOTE] The `201` status code is set explicitly in the route decorator. This is likely a bug — a `GET` endpoint
> conventionally returns `200 OK`.

---

## `POST /api/v1/readings/bulk`

Submit multiple sensor readings in a single request. Each reading is individually converted and persisted. If only some
readings are saved, a partial-success response is returned.

**Request body:** Array of `SensorReadingDTO`

**Response `201 Created`:** List of persisted `SensorReading` models

**Error responses:**

| Status | Reason                                                                                    |
|--------|-------------------------------------------------------------------------------------------|
| `500`  | Any DTO conversion failed (`ConversionException`)                                         |
| `207`  | Partial success — some readings were saved, others failed (`ReadingsBulkInsertException`) |
| `500`  | All readings failed to save (`ReadingsBulkInsertException`)                               |

---

## `GET /api/v1/sensors`

Retrieve a paginated list of all sensor boards.

**Query parameters:**

| Parameter   | Type  | Required | Description                         |
|-------------|-------|----------|-------------------------------------|
| `page_size` | `int` | ✅ Yes    | Maximum number of sensors to return |

**Response `200 OK`:** List of `SensorBoard` models

---

## `GET /api/v1/sensors/by`

Retrieve a list of sensor boards near a given location.

**Query parameters:**

| Parameter         | Type          | Required | Description                                                   |
|-------------------|---------------|----------|---------------------------------------------------------------|
| `location`        | `LocationDTO` | ✅ Yes    | Coordinates (`lat`, `long`) to search around                  |
| `radius`          | `int`         | ✅ Yes    | Search radius in km                                           |
| `page_size`       | `int`         | ✅ Yes    | Maximum number of sensors per location to return              |
| `locations_limit` | `int`         | ❌ No     | Maximum number of nearby locations to search (default: `500`) |

**Response `200 OK`:** List of `SensorBoard` models

**Error responses:**

| Status | Reason                                           |
|--------|--------------------------------------------------|
| `404`  | No location found matching the given coordinates |

---

## `POST /api/v1/sensors`

Upsert an existing sensor board. Requires a valid pre-existing token. Updates the sensor's record in the database.

**Request body:** `SensorBoardDTO`

**Response `200 OK`:** The upserted `SensorBoard` model

**Error responses:**

| Status | Reason                                  |
|--------|-----------------------------------------|
| `401`  | Token not found / sensor does not exist |

---

## `POST /api/v1/sensors/register`

Register a new sensor board. Creates a new sensor entry with an auto-generated UUID token, resolves or creates a
location, and associates the sensor with the default unassigned federation.

**Request body:** `SensorBoardRegisterDTO`

**Response `200 OK`:** The registered `SensorBoard` model (including the generated `token`)

**Error responses:**

| Status | Reason                                                                       |
|--------|------------------------------------------------------------------------------|
| `500`  | DTO conversion or database registration failure (`GenericDatabaseException`) |

---

## `GET /api/v1/locations`

Retrieve a paginated list of all known locations.

**Query parameters:**

| Parameter | Type  | Required | Description                                            |
|-----------|-------|----------|--------------------------------------------------------|
| `limit`   | `int` | ❌ No     | Maximum number of locations to return (default: `500`) |

**Response `200 OK`:** List of `Location` models

---

## `GET /api/v1/locations/by-sensor`

Retrieve the location associated with a specific sensor board.

**Query parameters:**

| Parameter   | Type   | Required | Description                         |
|-------------|--------|----------|-------------------------------------|
| `sensor_id` | `UUID` | ✅ Yes    | UUID of the sensor board to look up |

**Response `200 OK`:** The `Location` model linked to the given sensor

**Error responses:**

| Status | Reason                                       |
|--------|----------------------------------------------|
| `404`  | No sensor found with the given UUID          |
| `404`  | Sensor exists but has no associated location |

---

## Error Response Format

All application errors return a structured JSON body:

```json
{
  "detail": {
    "type": "ExceptionClassName",
    "message": "Human-readable error description"
  }
}
```

In **development** environments, a `stack_trace` field is additionally included.

For `ReadingInsertException`, a `reading-dump` field is included with the serialised failed reading:

```json
{
  "detail": {
    "type": "ReadingInsertException",
    "message": "Failed to save reading",
    "reading-dump": {
      ...
    }
  }
}
```

For bulk insert errors (`ReadingsBulkInsertException`), a `results` array is included with per-reading status codes (
`201` for success, `500` for failure), and an optional `exception` field if an underlying exception was captured:

```json
{
  "detail": {
    "type": "ReadingsBulkInsertException",
    "message": "Readings Partially Saved",
    "results": [
      {
        "entity": {
          ...
        },
        "status": 201
      },
      {
        "entity": {
          ...
        },
        "status": 500
      }
    ]
  }
}
```
