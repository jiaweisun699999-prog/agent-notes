"""
Model Class 方式初始化模型
创建各类LLM模型
"""
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatHunyuan, ChatTongyi, ChatZhipuAI
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from env_utils import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, OPENAI_API_KEY, OPENAI_BASE_URL, ANTHROPIC_API_KEY, \
    ANTHROPIC_BASE_URL, HUNYUAN_APP_ID, HUNYUAN_SECRET_ID, HUNYUAN_SECRET_KEY, DASHSCOPE_API_KEY, ZHIPUAI_API_KEY, \
    ZHIPUAI_BASE_URL

# deepseek_llm = ChatDeepSeek(
#     api_key=DEEPSEEK_API_KEY,
#     api_base=DEEPSEEK_BASE_URL,
#     model="deepseek-chat",
# )
#
# deepseek_llm2 = ChatOpenAI(
#     api_key=DEEPSEEK_API_KEY,
#     base_url=DEEPSEEK_BASE_URL,
#     model="deepseek-chat",
# )

openai_llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
    model="gpt-4",
)

anthropic_llm = ChatAnthropic(
    api_key=ANTHROPIC_API_KEY,
    base_url=ANTHROPIC_BASE_URL,
    # model="claude-3-5-haiku-latest",
    model="claude-3-5-haiku-20241022",
)


ollama_llm = ChatOllama(
    base_url="http://192.168.1.106:11434",
    model="deepseek-r1:1.5b",
)

hunyuan_llm = ChatHunyuan(
    hunyuan_app_id = HUNYUAN_APP_ID,
    hunyuan_secret_id = HUNYUAN_SECRET_ID,
    hunyuan_secret_key = HUNYUAN_SECRET_KEY,
    model="hunyuan-lite",
)

tongyi_llm = ChatTongyi(
    api_key=DASHSCOPE_API_KEY,
    model="qwen-plus",
)


zhipu_llm = ChatZhipuAI(
    api_key=ZHIPUAI_API_KEY,
    model="glm-4",
)

zhipu_llm2 = ChatOpenAI(
    api_key=ZHIPUAI_API_KEY,
    base_url=ZHIPUAI_BASE_URL,
    model="glm-4",
)
