# 导入必要的库
from pymilvus import MilvusClient  # Milvus 客户端，用于操作嵌入式向量数据库
import numpy as np  # NumPy 库，用于生成随机数和处理数组

# 初始化 Milvus 客户端
# 参数 "./milvus_demo.db" 指定了本地数据库文件的路径
# client = MilvusClient("./milvus_demo.db")
client = MilvusClient(uri='http://1.95.116.112:19530')

client.drop_collection(collection_name='demo_collection')

# 创建集合（Collection）
# 集合类似于关系型数据库中的表，用于存储向量和其他字段
client.create_collection(
    collection_name="demo_collection",  # 集合名称为 "demo_collection"
    dimension=384  # 向量的维度为 384，表示每个向量是一个长度为 384 的浮点数数组
)

# 准备数据：文档、向量和其他字段
docs = [
    "Artificial intelligence was founded as an academic discipline in 1956.",  # 文档 1
    "Alan Turing was the first person to conduct substantial research in AI.",  # 文档 2
    "Born in Maida Vale, London, Turing was raised in southern England.",       # 文档 3
]

# 为每段文本生成一个随机的 384 维向量
# 使用 NumPy 的 `np.random.uniform` 生成范围在 -1 到 1 之间的随机数
vectors = [[np.random.uniform(-1, 1) for _ in range(384)] for _ in range(len(docs))]

# 将文档、向量、ID 和主题打包成字典格式
# 每个字典包含以下字段：
# - id: 唯一标识符
# - vector: 向量数据
# - text: 文本内容
# - subject: 主题标签（这里是 "history"）
data = [
    {"id": i, "vector": vectors[i], "text": docs[i], "subject": "history"}
    for i in range(len(vectors))
]

# 将数据插入到集合中
res = client.insert(
    collection_name="demo_collection",  # 指定目标集合
    data=data  # 要插入的数据列表
)
# 输出插入结果（通常返回成功状态或插入的记录数）
print("Insert result:", res)

# client.release_collection(collection_name='demo_collection')
# Milvus 会将索引文件和所有字段的原始数据加载到内存中，以便快速响应搜索和查询。
# client.load_collection(collection_name='demo_collection')

# 执行相似性搜索
# 在集合中查找与查询向量最相似的记录
res = client.search(
    collection_name="demo_collection",  # 指定目标集合
    data=[vectors[0]],  # 查询向量（这里使用了第一个文档的向量）
    filter="subject == 'history'",  # 筛选条件：只返回主题为 "history" 的记录
    limit=2,  # 返回的最大结果数量（这里是 2 条）
    output_fields=["text", "subject"],  # 指定返回的字段（这里返回 "text" 和 "subject"）
)
# 输出搜索结果
print("Search result:", res)

# 执行查询操作
# 根据条件筛选记录（类似于 SQL 查询）
res = client.query(
    collection_name="demo_collection",  # 指定目标集合
    filter="subject == 'history'",  # 筛选条件：只返回主题为 "history" 的记录
    output_fields=["text", "subject"],  # 指定返回的字段（这里返回 "text" 和 "subject"）
)
# 输出查询结果
print("Query result:", res)

# 删除记录
# 根据条件删除记录
res = client.delete(
    collection_name="demo_collection",  # 指定目标集合
    filter="subject == 'history'",  # 删除条件：删除主题为 "history" 的记录
)
# 输出删除结果
print("Delete result:", res)
