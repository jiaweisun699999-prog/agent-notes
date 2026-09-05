import asyncio

from langchain_core.messages import ToolMessage

from graph.my_state import MultiModalRAGState
from milvus_db.collections_operator import COLLECTION_NAME, client
from milvus_db.db_retriever import MilvusRetriever
from utils.embeddings_utils import call_dashscope_once
from utils.log_utils import log

m_re = MilvusRetriever(COLLECTION_NAME, client)

#  自定义是为了替代：由LangGraph框架自带的ToolNode（有大模型动态传参 来调用工具）
class SearchContextToolNode:
    """自定义类，来执行搜索上下文工具"""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    # def __call__(self, inputs: dict):
    #     if messages := inputs.get("messages", []):
    #         message = messages[-1]
    #     else:
    #         raise ValueError("No message found in input")
    #     outputs = []
    #     for tool_call in message.tool_calls:
    #         if tool_call["args"] and 'query' in tool_call["args"]:
    #             query = tool_call["args"]["query"]
    #             log.info(f"开始从上下文中检索：{query}")
    #         else:
    #             query = inputs.get('input_text')
    #         tool_result = self.tools_by_name[tool_call["name"]].invoke(
    #             {'query': query}
    #             # {'query': query, 'user_name': inputs.get('user')}
    #         )
    #         outputs.append(
    #             ToolMessage(
    #                 content=tool_result,
    #                 name=tool_call["name"],
    #                 tool_call_id=tool_call["id"],
    #             )
    #         )
    #     return {"messages": outputs}

    ''' 修改的代码 开始'''

    # 10月18日的代码基础上，修改了一下 因为Tool为异步的，所以调用也必须是异步。

    async def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")

        outputs = []

        # 并行执行所有工具调用
        tasks = []
        for tool_call in message.tool_calls:
            if tool_call.get("args") and 'query' in tool_call["args"]:
                query = tool_call["args"]["query"]
                log.info(f"开始从上下文中检索：{query}")
            else:
                query = inputs.get('input_text')

            # 使用异步调用
            task = self.tools_by_name[tool_call["name"]].ainvoke(
                {'query': query, 'user_name': inputs.get('user')}
            )
            tasks.append((tool_call, task))

        # 等待所有异步调用完成
        tool_results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)

        for (tool_call, _), tool_result in zip(tasks, tool_results):
            if isinstance(tool_result, Exception):
                # 错误处理
                tool_result = f"工具执行错误: {str(tool_result)}"

            outputs.append(
                ToolMessage(
                    content=str(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )

        return {"messages": outputs}


def retriever_node(state: MultiModalRAGState):
    """检索 知识库并返回"""
    if state.get('input_type') == 'only_image':
        log.info(f"开始从知识库中检索图片：{state.get('input_image')}")
        # 构建图像输入数据
        input_data = [{'image': state.get('input_image')}]
        # 调用API获取图像嵌入向量
        ok, embedding, status, retry_after = call_dashscope_once(input_data)
        results = m_re.dense_search(embedding, limit=3)

    else:
        # 构建文本输入数据
        input_data = [{'text': state.get('input_text')}]
        # 调用API获取嵌入向量
        ok, embedding, status, retry_after = call_dashscope_once(input_data)
        results = m_re.hybrid_search(embedding, state.get('input_text'), limit=3)
    log.info(f"从知识库中检索到的结果：{results}")

    # 返回文档内容
    images = []  # 图片路径列表
    docs = []
    print(results)
    for hit in results:
        if hit.get('category')== 'image':
            images.append(hit.get('image_path'))
        docs.append({"text": hit.get("text"), "category": hit.get("category"), "image_path": hit.get("image_path"),
                     "filename": hit.get("filename"), })

    # 返回并更改状态
    return {'context_retrieved': docs, 'images_retrieved': images}

