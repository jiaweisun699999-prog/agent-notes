from typing import List, Dict

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from llm_models.all_llm import llm

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

import gradio as gr

# 2. 定义远程 MCP 服务器
mcp_server_config = {
    "url": "http://localhost:8000/sse",
    "transport": "sse"
}


prompt = ChatPromptTemplate.from_messages([
    ('system', '你是一个智能助手，尽可能的调用工具回答用户的问题'),
    MessagesPlaceholder(variable_name='chat_history', optional=True),
    ('human', '{input}'),
    MessagesPlaceholder(variable_name='agent_scratchpad', optional=True),
])



async def execute_graph(chat_bot: List[Dict]) -> List[Dict]:
    """ 执行工作流的函数"""
    user_input = chat_bot[-1]['content']
    result = ''  # AI助手的最后一条消息

    inputs = {
        "input": user_input
    }
    async with MultiServerMCPClient({
        "weather": mcp_server_config
    }) as client:
        tools = client.get_tools()
        print(tools)
        # agent = create_react_agent(llm, client.get_tools())
        agent = create_tool_calling_agent(llm, tools, prompt)
        executor = AgentExecutor(agent=agent, tools=tools)
        response = await executor.ainvoke(input=inputs)
        result = response["output"]

    chat_bot.append({'role': 'assistant', 'content': result})
    return chat_bot


def do_graph(user_input, chat_bot):
    """输入框提交后，执行的函数"""
    if user_input:
        chat_bot.append({'role': 'user', 'content': user_input})
    return '', chat_bot


css = '''
#bgc {background-color: #7FFFD4}
.feedback textarea {font-size: 24px !important}
'''
with gr.Blocks(title='调用MCP服务的Agent项目', css=css) as instance:
    gr.Label('调用MCP服务的Agent项目', container=False)

    chatbot = gr.Chatbot(type='messages', height=450, label='AI客服')  # 聊天记录组件

    input_textbox = gr.Textbox(label='请输入你的问题📝', value='')  # 输入框组件

    input_textbox.submit(do_graph, [input_textbox, chatbot], [input_textbox, chatbot]).then(execute_graph, chatbot,
                                                                                            chatbot)

if __name__ == '__main__':
    # 启动Gradio的应用
    instance.launch(debug=True)
