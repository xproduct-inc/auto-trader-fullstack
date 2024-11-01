import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_latest_market_data(client: AsyncClient):
    response = await client.get("/api/v1/market-data/latest/binance/BTC-USD")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_historical_market_data(client: AsyncClient):
    response = await client.get(
        "/api/v1/market-data/historical/binance/BTC-USD",
        params={"start_time": "2024-01-01T00:00:00Z"}
    )
    assert response.status_code == 200 