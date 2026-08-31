"""调用模型配置参数"""
from langchain.chat_models import init_chat_model
from langchain_core.callbacks import StdOutCallbackHandler, BaseCallbackHandler

from env_utils import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

class MyCustomCallbackHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        # **kwargs 中的参数有如下
        print("kwargs:", kwargs)

        # 从 kwargs 中提取配置信息
        run_name = kwargs.get("name")  # 对应 config 中的 'run_name'
        tags = kwargs.get("tags", [])
        metadata = kwargs.get("metadata", {})
        run_id = kwargs.get("run_id")

        print(f"[LLM开始] 运行名称: {run_name}")
        print(f"          标签: {tags}")
        print(f"          元数据: {metadata}")
        print(f"          运行ID: {run_id}")

        # 可以在这里执行更复杂的操作，比如：
        # 1. 将信息记录到日志系统或数据库
        # 2. 根据 metadata 中的 user_id 进行用户行为分析
        # 3. 根据 tags 对运行进行分类和监控
        # 4. 触发自定义事件，比如发送通知到监控系统

    def on_llm_end(self, response, **kwargs):
        # **kwargs 中的参数有如下
        print("kwargs:", kwargs)

        # 提取运行结束时的信息
        run_id = kwargs.get("run_id")
        print(f"[LLM结束] 运行ID: {run_id}")
        # 可以在这里记录运行结束的信息，比如消耗的令牌数等
        # 从response中提取模型消耗令牌数
        print("response:", response)

        # 消耗的令牌数
        num_tokens = response.llm_output["token_usage"]["total_tokens"]
        print(f"          消耗的令牌数: {num_tokens}")

# 使用您的自定义回调
custom_handler = MyCustomCallbackHandler()

# 1. 初始化模型
deepseek_llm = init_chat_model(
    model="deepseek-chat",
    model_provider="deepseek",
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
    # 指定可调整参数
    configurable_fields=("model", "model_provider", "temperature", "max_tokens"),
)

# 2. 准备 config 字典
config = {
    "run_name": "joke_generation",      # 在LangSmith中这次运行会显示为 "joke_generation"
    "tags": ["tag1", "tag2"],           # 打上标签便于分类查找
    "metadata": {"user_id": "123"},     # 记录用户ID
    "callbacks": [custom_handler],      # 启用自定义回调
    "configurable":{
        "model": "deepseek-reasoner",   # 配置模型参数
        "temperature": 0.7,             # 配置温度参数
        "max_tokens": 1000              # 配置最大令牌数
    }
}

# 3. 调用模型并传入 config
response = deepseek_llm.invoke(
    "给我讲个AI相关的笑话",
    config=config
)

print(response)

print(response.content)