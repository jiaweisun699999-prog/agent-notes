"""推理模型"""
from langchain.chat_models import init_chat_model

from env_utils import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

# deepseek_llm = init_chat_model(
#     model="deepseek-chat",
#     model_provider="deepseek",
#     api_key=DEEPSEEK_API_KEY,
#     base_url=DEEPSEEK_BASE_URL,
# )

deepseek_llm = init_chat_model(
    model="deepseek-reasoner",
    model_provider="deepseek",
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)

# resp = deepseek_llm.invoke("我有5个苹果，吃了1个，还剩几个？")
# print(resp)

response = deepseek_llm.invoke("10个字解释为什么天空是蓝色的？")
# print(response.content_blocks)
reasoning_steps = [b for b in response.content_blocks if b["type"] == "reasoning"]
print(" ".join(step["reasoning"] for step in reasoning_steps))
