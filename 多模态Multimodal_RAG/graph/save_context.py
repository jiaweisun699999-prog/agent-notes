import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from pymilvus import MilvusClient

from milvus_db.collections_operator import client, CONTEXT_COLLECTION_NAME
from my_llm import embedding
from utils.log_utils import log


# 全局线程池用于异步操作
thread_pool = ThreadPoolExecutor(max_workers=5) # 创建一个线程池

class OptimizedMilvusAsyncWriter:
    def __init__(self,
                 client: MilvusClient,
                 collection_name: str = "t_context_collection"):

        self.client = client
        self.collection_name = collection_name

    def _get_dense_vector(self, text: str):
        """异步生成稠密向量"""
        try:

            # 稠密向量生成（假设使用OpenAI或本地模型）
            dense_vector = embedding.embed_query(text)
            return dense_vector

        except Exception as e:
            log.exception(f"向量生成失败: {e}")
            return None


    def _sync_insert(self, data: Dict[str, Any]):
        """同步插入数据到Milvus"""
        try:
            # 插入数据
            result = self.client.insert(collection_name=self.collection_name, data=data)
            log.info(f"[Milvus] 成功插入 {result['insert_count']} 条记录。IDs 示例: {result['ids'][:5]}")

        except Exception as e:
            log.exception(f"插入数据到Milvus失败: {e}")


    async def async_insert(self, context_text: str, user: str, message_type: str = "AIMessage"):
        """异步插入数据"""
        # 准备数据
        data = {
            "context_text": context_text,
            "user": user,
            "timestamp": int(time.time() * 1000),  # 毫秒时间戳
            "message_type": message_type,
            "context_dense": self._get_dense_vector(context_text)
        }

        log.info(f"准备使用线程池异步插入数据: {data}")
        # 使用线程池异步执行插入操作
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(thread_pool, self._sync_insert, data)


# 全局写入器实例（单例模式）
_milvus_writer_instance = None

def get_milvus_writer() -> OptimizedMilvusAsyncWriter:
    """获取全局Milvus写入器实例（单例）"""
    global _milvus_writer_instance
    if _milvus_writer_instance is None:
        _milvus_writer_instance = OptimizedMilvusAsyncWriter(
            client=client,
            collection_name=CONTEXT_COLLECTION_NAME
        )
    return _milvus_writer_instance