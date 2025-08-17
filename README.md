# HedgeSim – FastAPI Order API + Hedger + Market Data Simulation

## Overview

HedgeSim is a production-style, local simulation environment for order intake, hedging, and market data streaming. It provides a complete stack including a FastAPI order API, asynchronous hedging worker, market data feeder, Redis cache, PostgreSQL database, Redpanda (Kafka-compatible) broker, and monitoring tools (Prometheus + Grafana).

It is designed for testing and simulating trading strategies across multiple asset classes: **crypto (BTCUSDT, ETHUSDT), equities (NVDA), and indices (SPX)**.

---

## Features

* **Order API**: FastAPI service for order intake and validation.
* **Hedger**: Async worker simulating hedge execution based on order flow.
* **Market Data**: Feeds both real (via CCXT) and synthetic market prices. Note: **CCXT usage does not include WebSockets implementation as it requires a paid subscription; this project is for educational purposes only.**
* **Database**: PostgreSQL for persisting orders, positions, and hedges.
* **Cache**: Redis for fast price lookups.
* **Messaging**: Redpanda (Kafka-compatible) for event streaming.
* **Observability**: Prometheus + Grafana preconfigured for metrics and dashboards.
* **Dockerized**: Fully containerized for local deployment.
* **Order Generator**: Docker service to randomly generate orders using the REST API for testing purposes.

---

## Repository Structure

```
hedge-sim/
├── docker-compose.yml
├── .env
├── api/
│   ├── app/                # FastAPI service
│   │   ├── __init__.py
│   │   ├── config.py       # Environment settings
│   │   ├── enums.py        # Asset classes, sides, order types
│   │   ├── schemas.py      # Pydantic models for API
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── db.py           # DB session
│   │   ├── kafka.py        # Kafka producer
│   │   ├── redis.py        # Redis client
│   │   ├── metrics.py      # Prometheus metrics
│   │   ├── routes.py       # API routes
│   │   └── main.py         # FastAPI entrypoint
│   ├── requirements.txt
│   └── Dockerfile
├── hedger/                 # Hedging worker
│   ├── main.py
│   ├── strategy.py
│   ├── requirements.txt
│   └── Dockerfile
├── marketdata/             # Market data feeder
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── order_generator/        # Random order generator
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
│       ├── dashboards/
│       │   └── hedgesim.json
│       └── provisioning/
│           ├── dashboards.yml
│           └── datasources.yml
└── README.md
```

---

## Services & Ports

| Service         | Port | Description                               |
| --------------- | ---- | ----------------------------------------- |
| API             | 8000 | FastAPI order intake, exposes `/metrics`  |
| Hedger          | 8001 | Async hedging worker, exposes `/metrics`  |
| MarketData      | 8002 | Price feeder, exposes `/metrics`          |
| Order Generator | -    | Randomly creates orders via REST API      |
| PostgreSQL      | 5432 | Database for orders & positions           |
| Redis           | 6379 | Price cache & fast lookups                |
| Redpanda        | 9092 | Kafka-compatible broker                   |
| Prometheus      | 9090 | Metrics scraping                          |
| Grafana         | 3000 | Dashboard (user: admin / password: admin) |

---

## Getting Started

### Prerequisites

* Docker >= 24
* Docker Compose >= 2.18

### Setup

1. Clone the repository:

```bash
git clone <repo_url>
cd hedge-sim
```

2. Optionally, create a `.env` file to override defaults:

```env
POSTGRES_DSN=postgresql+asyncpg://trader:traderpass@postgres:5432/trading
KAFKA_BOOTSTRAP_SERVERS=redpanda:9092
REDIS_URL=redis://redis:6379/0
```

3. Start all services with Docker Compose:

```bash
docker-compose up --build
```

4. Access services:

* API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
* Grafana: [http://localhost:3000](http://localhost:3000)
* Prometheus: [http://localhost:9090](http://localhost:9090)

---

## API Usage

### Place an Order

**Endpoint:** `POST /orders`
**Payload:**

```json
{
  "asset_class": "CRYPTO",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "quantity": 0.5,
  "order_type": "MARKET",
  "client_id": "client123"
}
```

**Response:**

```json
{
  "id": 1,
  "asset_class": "CRYPTO",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "quantity": 0.5,
  "order_type": "MARKET",
  "limit_price": null,
  "status": "ACCEPTED",
  "created_ts": "2025-08-17T12:34:56"
}
```

### Get Positions

**Endpoint:** `GET /positions`
**Response:**

```json
[
  {
    "symbol": "BTCUSDT",
    "spot_qty": 0.5,
    "perp_qty": 0.0,
    "usd_delta": 12500
  }
]
```

---

## Hedger & Strategy

* Subscribes to new orders from Kafka.
* Computes hedge needs based on predefined `HEDGE_BAND` and `CLIP_USD` parameters per symbol.
* Simulates execution, updates positions in the database.
* Metrics available at `/metrics`.

---

## Market Data Feeder

* Publishes price updates to Redis and Kafka.
* Supports real market data via **CCXT** (configurable via `USE_CCXT` environment variable). **Note: WebSocket support is not included because it requires a paid subscription; this project is for educational purposes only.**
* Synthetic tick generation for fast testing.
* Polling interval and tick interval configurable.

---

## Monitoring

* **Prometheus** scrapes metrics from API, Hedger, MarketData.
* **Grafana** preconfigured with dashboard `hedgesim.json` for live simulation stats.
* Metrics include:

  * Orders received
  * Hedging activity
  * Positions
  * Market prices

---

## Notes

* Symbols are configurable in `api/app/config.py`.
* All services expose Prometheus metrics for observability.
* Designed for local simulation; can be extended to real trading environment with proper connectors.

---

## License

MIT License
