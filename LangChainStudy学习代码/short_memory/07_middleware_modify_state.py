from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import after_model
from langchain.agents.structured_output import ToolStrategy
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolRuntime
from langgraph.runtime import Runtime
from langgraph.types import Command
from pydantic import BaseModel, Field
from typing import Dict, Any, Union

from init_llm import deepseek_llm


# 1. 定义Agent格式化返回结构
class OrderQueryResult(BaseModel):
    """订单查询响应结构"""
    order_id: str  # 订单ID
    product_name: str  # 订单中商品名称
    price: float  # 订单金额
    status: str  # 订单状态


class InventoryQueryResult(BaseModel):
    """库存查询响应结构"""
    product_name: str  # 商品名称
    stock_quantity: int  # 库存数量

# 2. 模拟数据库数据
MOCK_DATABASE = {
    "orders": {
        "order_001": OrderQueryResult(order_id="order_001", product_name="华为手机", price=1999.00, status="已发货"),
        "order_002": OrderQueryResult(order_id="order_002", product_name="苹果电脑", price=2999.00, status="待发货"),
        "order_003": OrderQueryResult(order_id="order_003", product_name="三星显示器", price=3999.00, status="已签收"),

    },
    "inventory": {
        "华为手机": InventoryQueryResult(product_name="华为手机",stock_quantity=50),
        "苹果电脑": InventoryQueryResult(product_name="苹果电脑",stock_quantity=20),
        "三星显示器": InventoryQueryResult(product_name="三星显示器",stock_quantity=30)
    }
}


# 3. 自定义状态类
class OrderState(AgentState):
    """自定义状态"""
    product_name: str  # 订单中商品名称


# 4. 定义工具函数
@tool
def get_order_info(order_id: str, runtime: ToolRuntime) -> Command:
    """获取订单详情
    Args:
        order_id (str): 订单ID
        runtime: 工具运行时，可以访问和更新状态
    Returns:
        Command: 包含订单详情和状态更新的命令对象
    """
    order_data = MOCK_DATABASE["orders"].get(order_id)

    if order_data:
        # 创建一个Command对象，包含订单数据和状态更新
        return Command(
            update={
                "product_name": order_data.product_name,
                "messages": [
                    ToolMessage(
                        content=f"订单查询成功: {order_data.order_id} - {order_data.product_name}",
                        tool_call_id=runtime.tool_call_id
                    )
                ],
                "structured_response": order_data
            }
        )
    else:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"错误：订单 {order_id} 不存在",
                        tool_call_id=runtime.tool_call_id
                    )
                ]
            }
        )


@tool
def get_product_inventory(runtime: ToolRuntime) -> InventoryQueryResult:
    """查询商品库存
    """
    print("runtime:", runtime)
    # 从 runtime中获取商品名称
    product_name = runtime.state["product_name"]

    inventory_data = MOCK_DATABASE["inventory"].get(product_name)
    if inventory_data:
        return inventory_data
    else:
        raise ValueError("商品不存在")


# 5. 中间件，模型调用完成后，从结构化输出中提取商品名称设置到状态中
@after_model
def manage_order_state(state: AgentState,runtime: Runtime) -> Dict[str, Any] | None:
    print("state:", state)

    # 如果state中没有结构化响应，直接返回None
    if "structured_response" not in state:
        return None

    # 获取AI大模型结构化输出结果
    structured_response = state["structured_response"]

    # 解析模型输出，如果是订单查询结果，返回商品名称，否则返回None
    if isinstance(structured_response, OrderQueryResult):
        product_name = structured_response.product_name
        return {"product_name": product_name}
    else:
        return None


# 6. 创建 Agent
agent = create_agent(
    model=deepseek_llm,
    tools=[get_order_info, get_product_inventory],
    response_format=ToolStrategy(Union[OrderQueryResult, InventoryQueryResult]),
    middleware=[manage_order_state],
    state_schema=OrderState,
    checkpointer=InMemorySaver()
)

# 7. 测试调用
config = {"configurable": {"thread_id": "user_001"}}

# 创建订单测试
response1 = agent.invoke({"messages": [{"role": "user", "content": "查询订单order_001信息"}]},config=config)
print("response1:", response1["structured_response"])
print("***" * 20)

# 查询订单测试
response2 = agent.invoke({"messages": [{"role": "user", "content": "这个订单中商品库存是多少"}]},config=config)
print("response2:", response2["structured_response"])
print("***" * 20)

response3 = agent.invoke({"messages": [{"role": "user", "content": "查询订单order_002信息"}]},config=config)
print("response3:", response3["structured_response"])
print("***" * 20)

response4 = agent.invoke({"messages": [{"role": "user", "content": "商品库存是多少"}]},config=config)
print("response4:", response4["structured_response"])
print("***" * 20)

# 查看最终状态
final_state = agent.get_state(config=config)
print("最终 product_name 状态:", final_state.values["product_name"])