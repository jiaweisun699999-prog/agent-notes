from langchain_milvus import Milvus, BM25BuiltInFunction
from pymilvus import MilvusClient, DataType, Function, FunctionType, AnnSearchRequest, RRFRanker

from documents.markdown_parser import MarkdownParser
from documents.milvus_db import MilvusVectorSave
from llm_models.embeddings_model import bge_embedding
from utils.env_utils import MILVUS_URI, COLLECTION_NAME


def test1():
    # 第一种
    mv = MilvusVectorSave()
    mv.create_connection(is_first=False)
    # result = mv.vector_store_saved.similarity_search(
    result = mv.vector_store_saved.similarity_search_with_score(
        query='现在，最先进的纳米级清洗技术是什么？',
        k=2,
        expr='category == "content"'
    )
    # similarity_search_with_score：返回的是一个二元组的列表，二元组中第二个值：分数
    for doc in result:
        print(doc)


def test2():
    """创建一个新的collection"""
    client = MilvusClient(uri=MILVUS_URI)

    schema = client.create_schema()
    schema.add_field(field_name='id', datatype=DataType.INT64, is_primary=True, auto_id=True)
    schema.add_field(field_name='text', datatype=DataType.VARCHAR, max_length=6000, enable_analyzer=True,
                     analyzer_params={"tokenizer": "jieba", "filter": ["cnalphanumonly"]})
    # schema.add_field(field_name='text', datatype=DataType.VARCHAR, max_length=6000, enable_analyzer=True)
    schema.add_field(field_name='category', datatype=DataType.VARCHAR, max_length=1000)
    schema.add_field(field_name='sparse', datatype=DataType.SPARSE_FLOAT_VECTOR)

    bm25_function = Function(
        name="text_bm25_emb",  # Function name
        input_field_names=["text"],  # Name of the VARCHAR field containing raw text data
        output_field_names=["sparse"],  # Name of the SPARSE_FLOAT_VECTOR field reserved to store generated embeddings
        function_type=FunctionType.BM25,  # Set to `BM25`
    )
    schema.add_function(bm25_function)
    index_params = client.prepare_index_params()

    index_params.add_index(
        field_name="sparse",
        index_name="sparse_inverted_index",
        index_type="SPARSE_INVERTED_INDEX",  # Inverted index type for sparse vectors
        metric_type="BM25",
        params={
            "inverted_index_algo": "DAAT_MAXSCORE",
            # Algorithm for building and querying the index. Valid values: DAAT_MAXSCORE, DAAT_WAND, TAAT_NAIVE.
            "bm25_k1": 1.2,
            "bm25_b": 0.75
        },
    )

    if 'demo' in client.list_collections():
        # 先释放， 再删除索引，再删除collection
        client.release_collection(collection_name='demo')
        client.drop_index(collection_name='demo', index_name='sparse_inverted_index')
        # client.drop_index(collection_name='demo', index_name='dense_inverted_index')
        client.drop_collection(collection_name='demo')

    client.create_collection(
        collection_name='demo',
        schema=schema,
        index_params=index_params
    )


def test3():
    """往collection中插入数据"""
    vector_store = Milvus(
        embedding_function=None,
        collection_name='demo',
        builtin_function=BM25BuiltInFunction(output_field_names='sparse'),
        vector_field=['sparse'],
        consistency_level="Strong",
        auto_id=True,
        connection_args={"uri": MILVUS_URI}
    )

    # 解析文件内容
    file_path = r'E:\my_project\RAG_PROJECT\datas\md\tech_report_0tfhhamx.md'
    parser = MarkdownParser()
    docs = parser.parse_markdown_to_documents(file_path)

    vector_store.add_documents(docs)


def test4():
    """全文搜索测试"""
    vector_store = Milvus(
        embedding_function=None,
        collection_name='demo',
        builtin_function=BM25BuiltInFunction(output_field_names='sparse'),
        vector_field=['sparse'],
        consistency_level="Strong",
        auto_id=True,
        connection_args={"uri": MILVUS_URI}
    )

    res = vector_store.similarity_search_with_score(
        query='活性氧原子',
        k=2
    )

    for doc in res:
        print(doc)


def test5():
    """采用PyMilvus的库来进行检索"""
    client = MilvusClient(uri=MILVUS_URI)
    res = client.search(
        collection_name='demo',
        data=['半导体表面特征改善'],
        anns_field='sparse',
        limit=3,
        output_fields=['text', 'id', 'category'],
        search_params={"params": {'drop_ratio_search': 0.2}} # 搜索时要忽略的低重要性词语的比例。
    )
    for item in res[0]:
        print(item)

def test6():
    client = MilvusClient(uri=MILVUS_URI)
    result = client.query(
        collection_name=COLLECTION_NAME,
        filter="category == 'Title'",  # 查询 category == 'Title' 的所有数据
        output_fields=['text', 'category', 'filename']  # 指定返回的字段
    )

    print('测试 过滤查询的结果是: ', result)


def test7():
    """pymilvus的混合检索"""
    client = MilvusClient(uri=MILVUS_URI)
    print(bge_embedding.embed_query('现在，最先进的纳米级清洗技术是什么？'))
    search_params_1 = {
        'data': [bge_embedding.embed_query('现在，最先进的纳米级清洗技术是什么？')],
        'anns_field': 'dense',
        "param": {
            "metric_type": "IP",
            "params": {"nprobe": 10}
        },
        "limit": 5
    }
    req1 = AnnSearchRequest(**search_params_1)  # 密集向量搜索请求对象

    search_params_2 = {
        'data': ['纳米级清洗技术是什么？'],
        'anns_field': 'sparse',
        "param": {
            "metric_type": "BM25"
        },
        "limit": 5
    }
    req2 = AnnSearchRequest(**search_params_2)  # 稀疏向量搜索请求对象

    res = client.hybrid_search(
        collection_name=COLLECTION_NAME,
        reqs=[req1, req2],
        ranker=RRFRanker(60),
        limit=5,
        output_fields=['text', 'title', 'category']
    )

    for hits in res:
        print('topN的 结果：')
        for item in hits:
            print(item)


def test8():
    """使用langchain对Milvus进行混合检索"""
    mv = MilvusVectorSave()
    mv.create_connection()
    res = mv.vector_store_saved.similarity_search(
        query='现在，最先进的纳米级清洗技术是什么？',
        k=3,
        ranker_type='rrf',  # ranker_type='weighted'
        ranker_params={"k": 100},
    )

    for item in res:
        print(item)


def test9():
    """使用langchain对Milvus进行混合检索"""
    mv = MilvusVectorSave()
    mv.create_connection()
    # res = mv.vector_store_saved.similarity_search_with_score(
    #     query='现在，最先进的纳米级清洗技术是什么？',
    #     k=3,
    #     ranker_type='rrf',  # ranker_type='weighted'
    #     ranker_params={"k": 100},
    # )

    retriever = mv.vector_store_saved.as_retriever(
        search_type='similarity',  # 仅返回相似度超过阈值的文档
        search_kwargs={
            "k": 3,
            "score_threshold": 0.1,
            "ranker_type": "rrf",
            "ranker_params": {"k": 100},
            'filter': {"category": "content"}
        }
    )

    res = retriever.invoke('介绍一下：光刻机有哪几种？')

    for item in res:
        print(item)

if __name__ == '__main__':
    # test2()  # 创建表结构
    # test3()  # 插入数据
    # test4()  # 测试全文检索
    # test5()  # 测试全文检索
    # test6()
    # test7()
    # test8()
    test9()