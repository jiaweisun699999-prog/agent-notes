from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from zhipuai import ZhipuAI

from llm_models.all_llm import llm
from utils.env_utils import ZHIPU_API_KEY

zhipu_client = ZhipuAI(api_key=ZHIPU_API_KEY, base_url='https://open.bigmodel.cn/api/paas/v4/')

class SearchInput(BaseModel):
    query: str = Field(description='需要搜索的内容或者关键词')


# 定义一个工具 函数
@tool('my_search_tool', args_schema=SearchInput)
def my_search(query: str) -> str:
    """搜索互联网上的内容"""
    response = zhipu_client.web_search.web_search(
        # search_engine="search-pro",
        search_engine="search-std",
        search_query=query
    )
    if response.search_result:
        return "\n\n".join([d.content for d in response.search_result])
    return '没有搜索到任何内容！'


prompt = ChatPromptTemplate.from_messages([
    ('system', '你是一个智能助手，尽可能的调用工具回答用户的问题'),
    MessagesPlaceholder(variable_name='chat_history', optional=True),
    ('human', '{input}'),
    MessagesPlaceholder(variable_name='agent_scratchpad', optional=True),
])

agent = create_tool_calling_agent(llm, [my_search], prompt)

executor = AgentExecutor(agent=agent, tools=[my_search])

resp1 = executor.invoke({'input': '什么是EUV光刻机？'})

print(resp1)

store = {}


#
# def get_session_history(session_id: str) -> BaseChatMessageHistory:
#     if session_id not in store:
#         store[session_id] = ChatMessageHistory()
#     return store[session_id]
#
#
# agent_with_history = RunnableWithMessageHistory(
#     executor,
#     get_session_history,
#     input_messages_key='input',
#     history_messages_key='chat_history'
# )
#
# resp2 = agent_with_history.invoke(
#     {'input': '什么是EUV光刻机？'},
#     config={'configurable': {"session_id": 'zs123'}}
# )
#
# print(resp2)