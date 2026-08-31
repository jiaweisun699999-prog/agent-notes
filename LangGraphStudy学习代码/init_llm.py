"""
init_chat_model 初始化聊天模型
"""
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel


from env_utils import DEEPSEEK_API_KEY


deepseek_llm: BaseChatModel = init_chat_model(
    model="deepseek-v4-pro",
    model_provider="deepseek",
    api_key=DEEPSEEK_API_KEY,
    extra_body={
        "thinking": {"type": "disabled"}  # 关闭思考模式
    }
)

deepseek_llm_flash: BaseChatModel = init_chat_model(
    model="deepseek-v4-flash",
    model_provider="deepseek",
    api_key=DEEPSEEK_API_KEY,
    extra_body={
        "thinking": {"type": "disabled"}  # 关闭思考模式
    }
)
