from langchain_openai import ChatOpenAI

from graph_chat.env_utils import ALIBABA_API_KEY, ALIBABA_BASE_URL, K2_API_KEY, K2_BASE_URL

# openai的大模型
# llm = ChatOpenAI(
#     model='gpt-4o-mini',
#     temperature=0.8,
#     api_key=OPENAI_API_KEY,
#     base_url=OPENAI_BASE_URL,
# )

#  claude 的大模型调用
# llm = ChatOpenAI(
#     model='claude-3-7-sonnet-20250219',
#     temperature=0.8,
#     api_key=OPENAI_API_KEY,
#     base_url=OPENAI_BASE_URL,
# )

# 官方的deepseek
# llm = ChatOpenAI(
#     model='deepseek-reasoner',
#     # model='deepseek-chat',
#     temperature=0.8,
#     api_key=DEEPSEEK_API_KEY,
#     base_url=DEEPSEEK_BASE_URL,
#     # model_kwargs={ "response_format": { "type": "json_object" } },
# )

# 本地vllm 私有化部署的大模型: 采用--tool-call-parser == hermes
# 流式输出的时候，会有错误
# llm = ChatOpenAI(
#     model='qwen3-8b',
#     temperature=0.8,
#     api_key='xx',
#     base_url=LOCAL_BASE_URL,
#     extra_body={'chat_template_kwargs': {'enable_thinking': True}},
# )

# 本地sglang 本地私有化部署的大模型： 采用--tool-call-parser == qwen25
# llm = ChatOpenAI(
#     model='qwen3-8b',
#     temperature=0.8,
#     api_key='xx',
#     base_url='http://i-2.gpushare.com:42124/v1',
#     extra_body={'chat_template_kwargs': {'enable_thinking': True}},
# )

# llm = ChatOpenAI(
#     model='ds-qwen3-8b',
#     temperature=0.5,
#     api_key='',
#     base_url=LOCAL_BASE_URL,
#     # extra_body={'chat_template_kwargs': {'enable_thinking': True}},
# )

# multiModal_llm = ChatOpenAI(  # 多模态大模型
#     model='qwen-omni-3b',
#     api_key='xx',
#     base_url=LOCAL_BASE_URL,
# )


llm = ChatOpenAI(
    model='qwen-plus',
    # model='qwen3-235b-a22b-thinking-2507',
    temperature=0.6,
    api_key=ALIBABA_API_KEY,
    base_url=ALIBABA_BASE_URL,
    # extra_body={'enable_thinking': True},
)

# llm = ChatOpenAI(
#     model='kimi-k2-0711-preview',
#     temperature=0.6,
#     api_key=K2_API_KEY,
#     base_url=K2_BASE_URL,
#     # extra_body={'enable_thinking': True},
# )

# llm.invoke(input=[{"role": "user", "content": "今天，北京的天气怎么样？"}])