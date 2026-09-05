import asyncio
import os
import uuid

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.store.memory import InMemoryStore
from graph.all_router import route_only_image, route_llm_or_retriever, route_evaluate_node, route_human_node, \
    route_human_approval_node
from graph.evaluate_node import evaluate_answer
from graph.my_state import MultiModalRAGState, InvalidInputError
from graph.print_messages import pretty_print_messages
from graph.save_context import get_milvus_writer
from graph.search_node import SearchContextToolNode, retriever_node
from graph.tools import search_context, my_search
from my_llm import multiModal_llm, llm
from utils.common_utils import draw_graph
from utils.embeddings_utils import image_to_base64
from utils.log_utils import log


# 上下文检索工具列表
tools = [search_context]

# 网络搜索工具列表
web_tools = [my_search]


# 工作流节点函数
def process_input(state: MultiModalRAGState, config: RunnableConfig):
    """处理用户输入"""
    user_name = config['configurable'].get('user_name', 'ZS')
    last_message = state["messages"][-1]
    log.info(f"用户 {user_name} 输入：{last_message}")
    input_type = 'has_text'
    text_content = None
    image_url = None
    # 检查输入类型
    if isinstance(last_message, HumanMessage):
        if isinstance(last_message.content, list): # 多模态的消息
            content = last_message.content
            for item in content:
                # 提取文本内容
                if item.get("type") == "text":
                    text_content = item.get("text", None)

                # 提取图片URL
                elif item.get("type") == "image_url":
                    url = item.get("image_url", "").get('url')
                    if url:  # 确保URL有效  （是图片的base64格式的字符串） （在线url）
                        image_url = url
    else:
        raise InvalidInputError(f"用户输入的消息错误！原始输入：{last_message}")

    if not text_content and image_url:
        input_type = 'only_image'

    # 返回结果： 如果想把什么样的数据保存（更新）到状态中，请返回一个字典，键为状态字段名称，值为数据。
    return {"input_type": input_type, 'user': user_name, 'input_text': text_content, 'input_image': image_url}





# 第一次生成回复或者决策（基于当前会话生成回复）
def first_chatbot(state: MultiModalRAGState):
    # llm_with_tools = llm.bind_tools(tools)
    llm_with_tools = multiModal_llm.bind_tools(tools)
    # # 修改后的系统提示词示例
    system_message = SystemMessage(content="""你是一名专精于 Apache Flink 的AI助手。你的核心任务是处理用户关于 Flink 的技术问题。

    # 核心指令（必须严格遵守）：
    1.  **首要规则**：当用户提问涉及 Apache Flink 的任何技术概念、配置、代码或实践时，你**必须且只能**调用 `search_context` 工具来获取信息。
    2.  **禁止行为**：你**严禁**凭借自身内部知识直接回答任何 Flink 技术问题。你的回答必须完全基于工具返回的知识库内容。
    3.  **兜底策略**：如果工具返回了相关信息，请基于这些信息组织答案。如果工具明确返回“未找到相关信息”，你应统一回复：“关于这个问题，我当前的知识库中没有找到确切的资料。”

    # 回答流程（不可更改）：
    用户提问 -> 调用 `search_context` 工具 -> 基于工具返回结果生成答案。
    """)
    # system_message = SystemMessage(
    #     content='你是一个Flink分布式计算引擎的专家，如果输入给你的信息中包含相关内容，直接回答。否则不要自己直接回答用户的问题，一定调用工具和知识库来补充，生成最终的答案。')

    return {"messages": [llm_with_tools.invoke([*state["messages"], system_message])]}


# 第二次生成回复（基于检索历史上下文 生成回复, 检索到的历史上下文在ToolMessage里面）
def second_chatbot(state: MultiModalRAGState):
    return {"messages": [multiModal_llm.invoke(state["messages"])]}


# 第三次 生成回复（基于检索知识库上下文 生成回复, 检索到的结果在状态里面）
def third_chatbot(state: MultiModalRAGState):
    """处理多模态请求并返回Markdown格式的结果"""
    context_retrieved = state.get('context_retrieved')
    images = state.get('images_retrieved')

    # 处理上下文列表
    count = 0
    context_pieces = []
    for hit in context_retrieved:
        count += 1
        context_pieces.append(f"检索后的内容{count}：\n {hit.get('text')} \n 资料来源：{hit.get('filename')}")

    context = "\n\n".join(context_pieces) if context_pieces else "没有检索到相关的上下文信息。"


    input_text = state.get('input_text')
    input_image = state.get('input_image')

    # 构建系统提示词
    system_prompt = f"""
        请根据用户输入和以下检索到的上下文内容生成响应，如果上下文内容中没有相关答案，请直接说明，不要自己直接输出答案。
        要求：
        1. 响应必须使用Markdown格式
        2. 在响应文字下方显示所有相关图片，图片的路径列表为{images}，使用Markdown图片语法：
        3. 在相关图片下面的最后一行显示上下文引用来源（来源文件名）
        4. 如果用户还输入了图片，请也结合上下文内容，生成文本响应内容。
        5. 如果用户还输入了文本，请结合上下文内容，生成文本响应内容。

        上下文内容：
        {context}
        """

    # 构建用户消息内容
    user_content = []
    if input_text:
        user_content.append({"type": "text", "text": input_text})
    if input_image:
        user_content.append({"type": "image_url", "image_url": {"url": input_image}})
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", user_content)
        ]
    )

    chain = prompt | multiModal_llm

    return {"messages": [chain.invoke({'context': context})]}


def human_approval(state: MultiModalRAGState):
    log.info('已经进入了人工审批节点')
    log.info(f'当前的状态中的人工审批信息：{state["human_answer"]}')


def fourth_chatbot(state: MultiModalRAGState):
    """网络搜索工具绑定的大模型，第四大模型调用"""
    llm_tools = multiModal_llm.bind_tools(web_tools)
    input_text = state.get('input_text')
    # result = interrupt({})  # 动态的人工介入， 中断后，人工开始填写人工回复。接下来开始恢复工作流（从开始节点到当前的interrupt点重复执行）
    system_message = SystemMessage(content='你是一个智能体助手，一定要优先调用互联网搜索工具，请根据用户输入和互联网搜索结果，生成回复。')
    message = HumanMessage(
        content=[
            {"type": "text", "text": input_text},
        ],
    )
    return {"messages": [llm_tools.invoke([system_message, message])]}


checkpointer = InMemorySaver()
store = InMemoryStore()



# 创建图
builder = StateGraph(MultiModalRAGState)

# 添加节点
builder.add_node("process_input", process_input)

builder.add_node("first_chatbot", first_chatbot)

search_context_node = SearchContextToolNode(tools=tools)
builder.add_node("search_context", search_context_node)
builder.add_node("retriever_node", retriever_node)
builder.add_node("second_chatbot", second_chatbot)
builder.add_node("third_chatbot", third_chatbot)
builder.add_node("evaluate_node", evaluate_answer)
builder.add_node("human_approval", human_approval)
builder.add_node("fourth_chatbot", fourth_chatbot)
builder.add_node("web_search_node", ToolNode(tools=web_tools))



# 添加边
builder.add_edge(START, 'process_input')
builder.add_conditional_edges('process_input', route_only_image,
                              {"retriever_node": "retriever_node", 'first_chatbot': 'first_chatbot'})

builder.add_conditional_edges('first_chatbot', tools_condition, {"tools": "search_context", END: END}, )

builder.add_conditional_edges('search_context', route_llm_or_retriever,
                              {"retriever_node": "retriever_node", 'second_chatbot': 'second_chatbot'})

builder.add_edge('retriever_node', 'third_chatbot')

# builder.add_edge('second_chatbot', 'evaluate_node')  # 任何结果，都要进行RAGAS的评估

builder.add_conditional_edges('third_chatbot', route_evaluate_node, {"evaluate_node": "evaluate_node", END: END},)
builder.add_conditional_edges('evaluate_node', route_human_node, {"human_approval": "human_approval", END: END},)
builder.add_conditional_edges('human_approval', route_human_approval_node, {"fourth_chatbot": "fourth_chatbot", END: END},)
builder.add_conditional_edges(
    "fourth_chatbot",
    tools_condition,
    {"tools": "web_search_node", END: END},
)
builder.add_edge('web_search_node', 'fourth_chatbot')

graph = builder.compile(
    checkpointer=checkpointer,
    store=store,
    interrupt_before=['human_approval']  # 添加中断点   静态的人工介入， 当恢复工作流时，会从中断点开始恢复工作流
)

# draw_graph(graph, 'graph_rag.png')

session_id = str(uuid.uuid4())

# 配置参数，包含乘客ID和线程ID
config = {
    "configurable": {
        "user_name": "ZS",
        # 检查点由session_id访问
        "thread_id": session_id,
    }
}


def update_state(user_answer, config):
    """在工作流外面的普通函数中，让人工介入"""
    if user_answer == 'approve':
        new_message = "approve"
    else:
        new_message = "rejected"
    # 把人为输入的，存入图的state中
    graph.update_state(
        config=config,
        values={'human_answer': new_message}
    )


async def execute_graph(user_input: str) -> str:
    """ 执行工作流的函数"""
    result = ''  # AI助手的最后一条消息
    current_state = graph.get_state(config)  # 得到实时的状态（短期上下文）
    if current_state.next:  # 出现了工作流的中断
        # 通过提供关于请求的更改/改变主意的指示来满足图的继续执行
        update_state(user_input, config)
        # 恢复执行工作流
        async for chunk in graph.astream(None, config, stream_mode='values'):
            pretty_print_messages(chunk, last_message=True)

        return result
    else:
        image_base64 = None
        text = None
        if '&' in user_input:
            text = user_input.split('&')[0]
            image = user_input.split('&')[1]
            if image and os.path.isfile(image):
                image_base64 = {
                    "type": "image_url",
                    "image_url": {"url": image_to_base64(image)[0]},
                }
        elif os.path.isfile(user_input):
            image_base64 = {
                "type": "image_url",
                "image_url": {"url": image_to_base64(user_input)[0]},
            }
        else:
            text = user_input

        message = HumanMessage(
            content=[
            ]
        )
        if text:
            message.content.append({"type": "text", "text": text})
        if image_base64:
            message.content.append(image_base64)
        async for chunk in graph.astream({'messages': [message]}, config, stream_mode='values'):
            pretty_print_messages(chunk, last_message=True)


    current_state = graph.get_state(config)
    if current_state.next:  # 出现了工作流的中断
        output = ("由于系统自我评估后，发现AI的回复不是非常准确，您是否 认可以下输出？\n "
                  "如果认可，请输入“approve”，否则请输入“rejected”，系统将会重新生成回复！")
        result = output
    else:
        # 异步写入响应到Milvus（把当前工作流执行后的最终结果，保存到上下文的向量数据库中）
        mess = current_state.values.get('messages', [])
        if mess:
            if isinstance(mess[-1], AIMessage):
                log.info(f"开始写入Milvus:")
                # 异步写入Milvus
                task = asyncio.create_task(  # 创建一个多线程异步任务
                    get_milvus_writer().async_insert(
                        context_text=mess[-1].content,
                        user=current_state.values.get('user', 'ZS'),
                        message_type="AIMessage"
                    )
                )

    return result


async def main():
    # 执行工作流
    while True:
        user_input = input('用户输入(文本和图片用&隔开)：')
        if user_input.lower() in ['exit', 'quit', '退出']:
            break

        res = await execute_graph(user_input)
        if res:
            print('AI: ', res)


if __name__ == '__main__':
    asyncio.run(main())
