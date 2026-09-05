
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from pymilvus import AnnSearchRequest, WeightedRanker

from graph.evaluate_node import rag_evaluator
from milvus_db.collections_operator import client, CONTEXT_COLLECTION_NAME

from my_llm import zhipuai_client
from utils.embeddings_utils import call_dashscope_once
from utils.log_utils import log


@tool('search_context', parse_docstring=True)
async def search_context(query: str=None, user_name: str=None) -> str:
    """
    根据用户的输入，检索与查询相关的历史上下文信息，然后给出正确的回答。

    Args:
        query: (可选)用户刚刚输入的文本内容。
        user_name: (可选)当前的用户名。

    Returns:
        从历史上下文中检索到的结果。

    """
    # 构建文本输入数据
    input_data = [{'text': query}]
    # 调用API获取嵌入向量
    ok, embedding, status, retry_after = call_dashscope_once(input_data)
    filter_expr = ''
    if user_name:
        filter_expr = f'user == "{user_name}"'   # 过滤搜索

    dense_search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
    dense_req = AnnSearchRequest(
        [embedding], "context_dense", dense_search_params, limit=3, expr=filter_expr
    )
    sparse_search_params = {"metric_type": "BM25", 'params': {'drop_ratio_search': 0.2}}
    sparse_req = AnnSearchRequest(
        [query], "context_sparse", sparse_search_params, limit=3, expr=filter_expr
    )

    #  由于稀疏向量检索：距离是没有归一化处理的，所以，distance 值无法标准化的评估，
    # 不需要混合检索，只要语义检索。

    rerank = WeightedRanker(1.0, 1.0)
    res = client.hybrid_search(
        collection_name=CONTEXT_COLLECTION_NAME,
        reqs=[sparse_req, dense_req],
        ranker=rerank,  # 重排算法
        limit=3,
        output_fields=["context_text"]
    )

    # 应用层过滤：只保留分数 >= min_score(0.75) 的结果
    log.info(f'上下文检索结果：{res[0]}')

    ''' 修改的代码 开始'''
    # 10月18日的代码基础上，修改了一下，启用了检索结果的相关性评估。
    # 应用层过滤：只保留分数 >= min_score(0.55) 的结果
    # filtered_results = [item for item in res[0] if item.distance >= 0.65]
    # 处理结果
    context_pieces = []
    for hit in res[0]:
        context_pieces.append(f"{hit.get('context_text')}")
    # 调用上下文相关性指标评估
    score = await rag_evaluator.evaluate_context(query, context_pieces)
    log.info(f"上下文检索后，评估分数为: {score}")
    if score < 1.0: # 评估分数小于1.0，则返回空
        context_pieces=[]
    ''' 修改的代码 结束'''

    return "\n".join(context_pieces) if context_pieces else "没有找到相关的历史上下文信息。"



class SearchInput(BaseModel):
    query: str = Field(description='需要搜索的内容或者关键词')


@tool('my_search', args_schema=SearchInput, description='专门搜索互联网中的公开内容')
def my_search(query: str) -> str:
    """搜索互联网上所有的公开内容"""
    try:
        response = zhipuai_client.web_search.web_search(
            search_engine="search_pro",
            search_query=query
        )
        # print(response)
        if response.search_result:
            return "\n\n".join([d.content for d in response.search_result])
        return '没有搜索到任何内容！'
    except Exception as e:
        print(e)
        return '没有搜索到任何内容！'



# ----------------- 辅助函数 -----------------
# def pretty_print_messages(update, last_message=False):
#     is_subgraph = False
#     if isinstance(update, tuple):
#         ns, update = update
#         # skip parent graph updates in the printouts
#         if len(ns) == 0:
#             return
#
#         graph_id = ns[-1].split(":")[0]
#         print(f"Update from subgraph {graph_id}:")
#         print("\n")
#         is_subgraph = True
#
#     for node_name, node_update in update.items():
#         update_label = f"Update from node {node_name}:"
#         if is_subgraph:
#             update_label = "\t" + update_label
#
#         print(update_label)
#         print("\n")
#
#         if not node_update:
#             continue
#         if 'messages' not in node_update:
#             if isinstance(node_update, Sequence) and isinstance(node_update[-1], BaseMessage):
#                 pretty_print_message(node_update[-1])
#             else:
#                 print(node_update)
#             print("--------------\n")
#             continue
#         messages = convert_to_messages(node_update["messages"])
#         if last_message:
#             messages = messages[-1:]
#
#         for m in messages:
#             pretty_print_message(m, indent=is_subgraph)
#         print("\n")
#
#
# def pretty_print_message(message, indent=False):
#     pretty_message = message.pretty_repr(html=True)
#     if not indent:
#         print(pretty_message)
#         return
#
#     indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
#     print(indented)

if __name__ == '__main__':
    # search_context.invoke()
    print(search_context("有界流和无界流的定义", 'text'))