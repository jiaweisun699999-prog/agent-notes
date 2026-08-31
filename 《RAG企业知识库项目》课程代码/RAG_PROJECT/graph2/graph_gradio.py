from pprint import pprint
from typing import List, Dict

import gradio as gr

from graph2.graph_2 import graph


def execute_graph(chat_bot: List[Dict]) -> List[Dict]:
    """ 执行工作流的函数"""
    user_input = chat_bot[-1]['content']
    result = ''  # AI助手的最后一条消息

    inputs = {
        "question": user_input
    }
    # 流式执行工作流
    for output in graph.stream(inputs):

        for key, value in output.items():
            # 打印当前节点名称
            pprint(f"Node '{key}':")  # 显示当前执行的节点名称
        pprint("\n---\n")  # 节点分隔线

    # 打印最终生成结果
    pprint(value["generation"])  # 输出最终生成的回答内容
    result = value["generation"]

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
with gr.Blocks(title='混合检索+自评估RAG', css=css) as instance:
    gr.Label('混合检索+自评估RAG', container=False)

    chatbot = gr.Chatbot(type='messages', height=350, label='AI客服')  # 聊天记录组件

    input_textbox = gr.Textbox(label='请输入你的问题📝', value='')  # 输入框组件

    input_textbox.submit(do_graph, [input_textbox, chatbot], [input_textbox, chatbot]).then(execute_graph, chatbot,
                                                                                            chatbot)

if __name__ == '__main__':
    # 启动Gradio的应用
    instance.launch(debug=True)
