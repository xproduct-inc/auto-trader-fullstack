src/
├── api/
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   ├── market_data.py
│   │   │   └── trading.py
│   │   └── router.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── logging.py
├── db/
│   ├── __init__.py
│   ├── base.py
│   ├── session.py
│   └── models/
│       ├── __init__.py
│       ├── market_data.py
│       └── trading.py
├── services/
│   ├── __init__.py
│   ├── data_ingestion.py
│   ├── strategy.py
│   ├── risk_manager.py
│   └── trade_executor.py
├── schemas/
│   ├── __init__.py
│   ├── market_data.py
│   └── trading.py
├── agents/
│   ├── __init__.py
│   └── trading_agent.py
└── utils/
    ├── __init__.py
    └── redis_client.py 