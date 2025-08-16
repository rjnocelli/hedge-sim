from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    app_name: str = "hedgesim-api"
    evironment: str = "local"
    host: str = "0.0.0.0"
    port: int = 8000
    kafka_bootstrap_servers: str = Field("redpanda:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    kafka_client_id: str = Field("hedgesim-api", env="KAFKA_CLIENT_ID")
    kafka_topic_orders: str = Field("orders.new", env="KAFKA_TOPIC_ORDERS")
    postgres_dsn: str = Field("postgresql+asyncpg://trader:traderpass@postgres:5432/trading", env="POSTGRES_DSN")
    class Config:
        env_file = ".env"

settings = Settings()
