import os
from typing import List, Dict, Any

from pymilvus import MilvusClient, AnnSearchRequest, WeightedRanker

from milvus_db.collections_operator import client, COLLECTION_NAME
from utils.embeddings_utils import image_to_base64, call_dashscope_once


# --------------------------
# Embedding + Retriever
# --------------------------
class MilvusRetriever:
    def __init__(self, collection_name: str, milvus_client: MilvusClient, top_k: int =3):
        self.collection_name = collection_name
        self.milvus_client = milvus_client
        self.top_k = top_k

    def dense_search(self, query_dense_embedding, limit=10):
        search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
        res = self.milvus_client.search(
            collection_name=self.collection_name,
            data=[query_dense_embedding],
            anns_field="dense",
            limit=limit,
            output_fields=["text", 'category', 'filename', 'image_path', 'title'],
            search_params=search_params,
        )
        return res[0]

    def sparse_search(self, query_sparse_embedding, limit=10):
        return self.milvus_client.search(
            collection_name=self.collection_name,
            data=query_sparse_embedding,
            anns_field="sparse",
            limit=limit,
            output_fields=["text", 'category', 'filename', 'image_path', 'title'],
            search_params={"metric_type": "BM25", "params": {'drop_ratio_search': 0.2}} # 搜索时要忽略的低重要性词语的比例。,
        )[0]

    def hybrid_search(
            self,
            query_dense_embedding,
            query_sparse_embedding,
            sparse_weight=1.0,
            dense_weight=1.0,
            limit=10,
    ):
        filter_expr = None
        # filter_expr = 'category == "text"'
        dense_search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
        dense_req = AnnSearchRequest(
            [query_dense_embedding], "dense", dense_search_params, limit=limit, expr=filter_expr
        )
        sparse_search_params = {"metric_type": "BM25", 'params': {'drop_ratio_search': 0.2}}
        sparse_req = AnnSearchRequest(
            [query_sparse_embedding], "sparse", sparse_search_params, limit=limit, expr=filter_expr
        )
        rerank = WeightedRanker(sparse_weight, dense_weight)
        return self.milvus_client.hybrid_search(
            collection_name=self.collection_name,
            reqs=[sparse_req, dense_req],
            ranker=rerank, # 重排算法
            limit=limit,
            output_fields=["text", 'category', 'filename', 'image_path', 'title'],
        )[0]

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        if os.path.isfile(query):
            # 构建图像输入数据
            input_data = [{'image': image_to_base64(query)[0]}]
            # 调用API获取图像嵌入向量
            ok, embedding, status, retry_after = call_dashscope_once(input_data)
        else:
            # 构建文本输入数据
            input_data = [{'text': query}]
            # 调用API获取嵌入向量
            ok, embedding, status, retry_after = call_dashscope_once(input_data)

        if ok:
            if os.path.isfile(query):  # 纯图片不能用混合检索
                results = self.dense_search(embedding, limit=self.top_k)
            else:
                print('混合检索')
                results = self.hybrid_search(embedding, query, limit=self.top_k)
                # results = self.dense_search(embedding, limit=self.top_k)
        # 返回文档内容
        # return results

        docs = []
        print(results)
        for hit in results:
            docs.append({"text": hit.get("text"), "category": hit.get("category"), "image_path": hit.get("image_path"), "filename": hit.get("filename"),})

        return docs

    def hybrid_search2(
            self,
            query_dense_embedding,
            query_sparse_embedding,
            sparse_weight=1.0,
            dense_weight=1.0,
            limit=10,
    ):
        dense_search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
        dense_req = AnnSearchRequest(
            [query_dense_embedding], "dense", dense_search_params, limit=limit
        )
        sparse_search_params = {"metric_type": "BM25", 'params': {'drop_ratio_search': 0.2}}
        sparse_req = AnnSearchRequest(
            [query_sparse_embedding], "sparse", sparse_search_params, limit=limit
        )

        # search1 = [sparse_req, dense_req]
        # search2 = AnnSearchRequest(
        #     [query_dense_embedding], "dense", dense_search_params, limit=limit
        # )
        # 重排算法
        rerank = WeightedRanker(sparse_weight, dense_weight)
        return self.client.hybrid_search(
            collection_name=self.collection_name,
            reqs=[sparse_req, dense_req],
            ranker=rerank,  # 重排算法
            limit=limit,
            output_fields=["text", 'category', 'filename', 'image_path', 'title']
        )[0]



if __name__ == '__main__':
    m_re = MilvusRetriever(collection_name=COLLECTION_NAME, milvus_client=client)
    docs = m_re.retrieve("有界流和无界流")  # 输入的是文本 Any-To-Any
    # docs = m_re.retrieve(r"C:\Users\goldbin\Pictures\Snipaste_2025-09-20_19-42-06.png")
    for d in docs:
        print(d)