
# StockPulse #

StockPulse is a lightweight streaming pipeline that ingests market tick data from a WebSocket source (Finnhub), publishes raw ticks to Kafka, and runs Spark Structured Streaming jobs to compute OHLC (open/high/low/close) aggregates and persist them to Parquet.

**Getting Started**
- **Requirements:** Go (see `go.mod`), Docker & Docker Compose, Java/Spark for running Spark jobs (if not using the containerized Spark), Python + pandas (for quick local data reads).
- **Clone:** `git clone https://github.com/cneluhena/StockPulse`

**Environment variables (.env)**
- **KAFKA_BROKER:** address of the Kafka broker (e.g. `kafka:9093`)
- **KAFKA_TOPIC:** topic to publish raw ticks (example: `raw_ticks`)
- **FINNHUB_TOKEN:** Finnhub API token for the WebSocket feed
- **SYMBOL_LIST:** comma-separated symbols (default: `BINANCE:ETHUSDT,BINANCE:BTCUSDT`)

Example `.env`:

```
KAFKA_BROKER=kafka:9093
KAFKA_TOPIC=raw_ticks
FINNHUB_TOKEN=your_finnhub_token_here
SYMBOL_LIST=BINANCE:ETHUSDT,BINANCE:BTCUSDT
```

**Components**
- **`cmd/api`**: HTTP API server using Gin. Exposes `/api/v1/ping` and `/api/v1/status` on port `:8080`.
- **`cmd/producer`**: WebSocket producer that subscribes to Finnhub and writes raw tick messages to the configured Kafka topic.
- **`internal/config`**: configuration loader (uses `godotenv`).
- **`internal/handlers`**: simple API handlers for health and config inspection.
- **`spark_apps/spark_processor.py`**: Spark Structured Streaming job reading from Kafka topic `raw_ticks` and computing 1-minute OHLC windows, writing Parquet output.
- **`data_read.py`**: small Python snippet to read local Parquet files and convert to JSON for ad-hoc inspection.
- **`docker-compose.yml`**: services for Kafka, Kafka UI and (containerized) Spark master/worker with the repository's `spark_apps` and `jars` mounted.

**Ports**
- Kafka broker: `9092` (host mapped), internal Kafka used by services: `9093`
- Kafka UI: `8085`
- API server: `8080`
- Spark master UI: `8086` (mapped) and Spark master port `7077`

**Build & Run**

1. Start Kafka and Spark via Docker Compose (recommended for local development):

```bash
docker compose up -d
```

2. Export environment variables or create a `.env` file in the repo root (see example above).

3. Run the API server (from repo root):

```bash
go run ./cmd/api
```

4. Run the producer (streams ticks to Kafka):

```bash
go run ./cmd/producer
```

5. Run the Spark processor (either in-cluster with spark-submit or via the container):

If Spark is running in the container from `docker-compose.yml`, you can `exec` into the container and run `spark-submit` pointing to `spark_apps/spark_processor.py`. Example (adjust paths to your environment):

```bash
docker exec -it spark_master /opt/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.1 /opt/spark/work-dir/spark_apps/spark_processor.py
```

Or run Spark locally with an appropriate Spark distribution:

```bash
spark-submit --master local[2] spark_apps/spark_processor.py
```

**Example API checks**

```bash
curl http://localhost:8080/api/v1/ping
curl http://localhost:8080/api/v1/status
```

**Kafka topic**
The Spark processor subscribes to the Kafka topic `raw_ticks` in the example code. Make sure `KAFKA_TOPIC` used by the producer matches the Spark subscription.

**Development notes & next steps**
- The project uses `godotenv` to load `.env` for local development but will fall back to system environment variables.
- Add more robust error handling and reconnect logic in the producer for production readiness.
- Add automated CI to build Go binaries and run static checks.

**Troubleshooting**
- If WebSocket connection fails, verify `FINNHUB_TOKEN` and network access.
- If Spark cannot connect to Kafka, confirm broker addresses and ports in `.env` match `docker-compose.yml` mappings.

---
