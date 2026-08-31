from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from contextlib import asynccontextmanager

DB_URI = "postgresql://postgres:postgres123@192.168.179.5:5432/langgraph_db"

@asynccontextmanager
async def get_checkpointer():
    """创建 AsyncPostgresSaver 实例"""
    async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
        await checkpointer.setup()
        yield checkpointer