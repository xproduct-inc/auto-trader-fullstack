from clickhouse_driver.asyncio import Client
from core.config import get_settings

settings = get_settings()

class ClickHouseClient:
    def __init__(self):
        self.client = None

    async def connect(self):
        """Connect to ClickHouse"""
        if not self.client:
            self.client = Client(
                host=settings.CLICKHOUSE_HOST,
                port=settings.CLICKHOUSE_PORT,
                database=settings.CLICKHOUSE_DB
            )

    async def store_analytics(self, table: str, data: dict):
        """Store analytics data"""
        if not self.client:
            await self.connect()
            
        query = f"""
        INSERT INTO {table} FORMAT JSONEachRow
        {data}
        """
        await self.client.execute(query)

    async def close(self):
        """Close connection"""
        if self.client:
            await self.client.disconnect() 