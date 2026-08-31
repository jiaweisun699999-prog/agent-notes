import time

from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.config import get_stream_writer
from init_llm import deepseek_llm, tongyi_llm


@tool
def generate_sales_report()-> str:
    """
    生成销售报告
    """
    writer = get_stream_writer()
    writer({"type":"生成销售报告","message":"开始生成销售报告"})
    time.sleep(1)
    writer({"type":"生成销售报告","message":"销售报告生成了 25%"})
    time.sleep(1)
    writer({"type":"生成销售报告","message":"销售报告生成了 50%"})
    time.sleep(1)
    writer({"type":"生成销售报告","message":"销售报告生成了 75%"})
    time.sleep(1)
    writer({"type":"生成销售报告","message":"销售报告生成了 100%"})


@tool
def generate_inventory_report()-> str:
    """
    生成库存报告
    """
    writer = get_stream_writer()
    writer("开始生成库存报告")
    time.sleep(1)
    writer("库存报告生成了 25%")
    time.sleep(1)
    writer("库存报告生成了 50%")
    time.sleep(1)
    writer("库存报告生成了 75%")
    time.sleep(1)
    writer("库存报告生成了 100%")


agent = create_agent(
    model=deepseek_llm,
    system_prompt="你是一个客户助手，负责回答用户问题。",
    tools=[generate_sales_report,generate_inventory_report]
)


for chunk in agent.stream(
        {"messages": [{"role": "user", "content": "生成销售报告和库存报告"}]},
        stream_mode=["custom","updates"]
):
    print(chunk)
    print("-"*50)