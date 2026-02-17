import uuid

from contracts import SensorReadingDTO, SensorReading, IReadingsRepository


class ReadingsService:
    def __init__(self, readings_repo: IReadingsRepository):
        self.readings_repo = readings_repo

    @staticmethod
    def convert_dto_to_db_model(reading: SensorReadingDTO) -> SensorReading:
        return SensorReading(
            id_sensor=uuid.uuid4(),
            created_at=reading.created_at,
            token=reading.token,
            disputed=False,
            co2=reading.sensors.co2,
            tvoc=reading.sensors.tvoc,
            pm1=reading.sensors.pm1,
            pm10=reading.sensors.pm10,
            pm25=reading.sensors.pm25,
            pressure=reading.sensors.pressure,
            humidity=reading.sensors.humidity,
            temperature=reading.sensors.temperature,
        )

    async def add_reading_to_db(self, reading: SensorReading) -> str | bool:
        try:
            await self.readings_repo.save(reading)
            return True
        except Exception as e:
            return f"Error saving reading: {str(e)}"
