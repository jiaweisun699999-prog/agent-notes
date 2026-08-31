from pymilvus import MilvusClient, DataType, Function, FunctionType

client = MilvusClient(uri='http://1.95.116.112:19530')

# 定义 Collections 模式  (三个字段)
schema = client.create_schema()
schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True, auto_id=True)
schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=2000, enable_analyzer=True)
schema.add_field(field_name="sparse", datatype=DataType.SPARSE_FLOAT_VECTOR)  # 存储稀疏嵌入后的值


# 进行稀疏嵌入的函数 ： 从一个字段中读取原始数据，通过bm25算法，转换为向量，再把稀疏向量存到输出字段
bm25_function = Function(
    name="text_bm25_emb", # Function name
    input_field_names=["text"], # Name of the VARCHAR field containing raw text data
    output_field_names=["sparse"], # Name of the SPARSE_FLOAT_VECTOR field reserved to store generated embeddings
    function_type=FunctionType.BM25, # Set to `BM25`
)

schema.add_function(bm25_function)

# 配置索引
index_params = client.prepare_index_params()

index_params.add_index(
    field_name="sparse",
    index_name="sparse_inverted_index",
    index_type="SPARSE_INVERTED_INDEX", # Inverted index type for sparse vectors
    metric_type="BM25",
    params={
        "inverted_index_algo": "DAAT_MAXSCORE", # Algorithm for building and querying the index. Valid values: DAAT_MAXSCORE, DAAT_WAND, TAAT_NAIVE.
        "bm25_k1": 1.6,  # 范围：[1.2 ~ 2.0]
        "bm25_b": 0.75
    },
)


# 创建一张表
client.create_collection(
    collection_name='t_demo2',
    schema=schema,
    index_params=index_params
)

# 插入测试数据
client.insert('t_demo2', [
    {'text': 'information retrieval is a field of study.'},
    {'text': 'information retrieval focuses on finding relevant information in large datasets.'},
    {'text': 'data mining and information retrieval overlap in research.'},
])


# 开始进行匹配搜索（全文搜索）
search_params = {
    'params': {'drop_ratio_search': 0.2},  # 搜索时要忽略的低重要性词语的比例： 查询向量中最小的 20% 值将在搜索过程中被忽略。
}

resp = client.search(
    collection_name='t_demo2',
    data=['whats the focus of information retrieval?'],
    anns_field='sparse',  # 匹配的稀疏向量字段
    limit=3,
    search_params=search_params,
    output_fields=["text"]
)

print(resp)







