from typing import Any, Type

from langchain_core.tools import BaseTool, tool
from langgraph.types import interrupt
from pydantic import BaseModel, Field
from zhipuai import ZhipuAI

from graph_chat.env_utils import ZHIPU_API_KEY

zhipuai_client = ZhipuAI(api_key=ZHIPU_API_KEY)


class SearchArgs(BaseModel):
    query: str = Field(description="需要进行网络搜索的信息。")


# 网络搜索的工具
class MySearchTool(BaseTool):
    # 工具名字
    name: str = "search_tool"

    description: str = '搜索互联网上公开内容的工具'

    return_direct: bool = False

    args_schema: Type[BaseModel] = SearchArgs

    def _run(self, query) -> str:

        print('AI大模型尝试调用工具 `search_tool`来完成数据搜索')
        response = interrupt(
            f"AI大模型尝试调用工具 `search_tool`来完成数据搜索，\n"
            "请审核并选择：批准（y）或直接给我工具执行的答案。"
        )
        # response(字典): 由人工输入的：批准(y),工具执行的答案或者拒绝执行工具的理由
        # 根据人工响应类型处理
        if response["answer"] == "y":
            pass  # 直接使用原参数继续执行
        else:
            return f"人工终止了该工具的调用，给出的理由或者答案是:{response['answer']}",

        response = zhipuai_client.web_search.web_search(
            # search_engine="search_pro",
            search_engine="search_std",
            search_query=query
        )
        # print(response)
        if response.search_result:
            return "\n\n".join([d.content for d in response.search_result])
        return '没有搜索到任何内容！'

# my_tool = MySearchTool()
# print(my_tool.name)
# print(my_tool.description)
# print(my_tool.args_schema.model_json_schema())