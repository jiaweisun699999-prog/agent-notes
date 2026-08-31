"""
模型调用
1. Invoke

2. Stream Invoke

3. Batch Invoke
"""

from init_llm import deepseek_llm

# 3. Batch Invoke

resp = deepseek_llm.batch([
    "请介绍一下你自己",
    "飞机为什么会飞",
    "什么是大模型",
])
#
# for item in resp:
#     print(item.content)

resp = deepseek_llm.batch_as_completed([
    "请介绍一下你自己",
    "飞机为什么会飞",
    "什么是大模型",
],
    config={
        "max_concurrency": 3,
    }
)

for item in resp:
    print(item)



# 2. Stream Invoke
# response = deepseek_llm.stream("请介绍一下你自己")
# for chunk in response:
#     print(chunk.content, end="|", flush=True)















# 1. Invoke
#单条消息调用模型
# resp = deepseek_llm.invoke("请介绍一下你自己")
# print(type(resp))
# print(resp.content)

# 字典格式的消息列表
# conversations = [
#     {"role": "system", "content": "你是一个翻译助手，可以将汉语翻译成英语"},
#     {"role": "user", "content": "翻译：我喜欢编程"},
#     {"role": "assistant", "content": "I like programming."},
#     {"role": "user", "content": "翻译：我喜欢大模型"},
# ]

# resp = deepseek_llm.invoke(conversations)
# print(type(resp))
# print(resp)
# print(resp.content)


# 消息对象格式的消息列表
# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
#
# conversations = [
#     SystemMessage(content="你是一个翻译助手，可以将汉语翻译成英语"),
#     HumanMessage(content="翻译：我喜欢编程"),
#     AIMessage(content="I like programming."),
#     HumanMessage(content="翻译：我喜欢大模型"),
# ]
#
# resp = deepseek_llm.invoke(conversations)
# print(type(resp))
# print(resp)
# print(resp.content)
