from langgraph.store.postgres.aio import AsyncPostgresStore
from contextlib import asynccontextmanager

DB_URI = "postgresql://postgres:postgres123@192.168.179.5:5432/langgraph_db"

@asynccontextmanager
async def get_store():
    """自定义 Store 工厂 —— langgraph dev 自动调用"""
    async with AsyncPostgresStore.from_conn_string(DB_URI) as store:
        await store.setup()
        yield store