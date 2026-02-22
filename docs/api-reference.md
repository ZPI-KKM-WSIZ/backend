# API Reference

Base path: `/api/v1`

> ⚠️ This backend is under active development. Additional endpoints (sensor registration, locations, federation, and
> others) are not yet available.

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
location by coordinates, and persists the reading to Cassandra via the repository layer.

**Request body:** `SensorReadingDTO` (contract defined in `cassandra-repositories`)

**Response `201 Created`:** The persisted `SensorReading` model

**Error responses:**

| Status | Reason                                              |
|--------|-----------------------------------------------------|
| `500`  | Sensor token not registered / DTO conversion failed |
| `500`  | Database insert failure                             |
