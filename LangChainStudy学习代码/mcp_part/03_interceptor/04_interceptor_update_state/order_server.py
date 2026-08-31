"""订单 MCP Server —— 提供查询和退款两个工具"""
from fastmcp import FastMCP

mcp = FastMCP("OrderService")

ORDERS = {
    "ORD-001": {"product": "无线耳机", "status": "已签收", "amount": 299.0},
    "ORD-002": {"product": "机械键盘", "status": "配送中", "amount": 599.0},
}


@mcp.tool()
async def check_order(order_id: str) -> str:
    """查询订单状态，返回订单的商品、状态和金额"""
    order = ORDERS.get(order_id)
    if not order:
        return f"未找到订单 {order_id}"
    return f"订单 {order_id}：{order['product']}，{order['status']}，{order['amount']}元"


@mcp.tool()
async def process_refund(order_id: str) -> str:
    """执行退款操作。仅状态为'已签收'的订单可退款。"""
    order = ORDERS.get(order_id)
    if not order:
        return f"退款失败：未找到订单 {order_id}"
    if order["status"] != "已签收":
        return f"退款失败：订单当前状态为'{order['status']}'，仅已签收的订单可退款"
    ORDERS[order_id]["status"] = "已退款"
    return f"退款成功：{order_id}（{order['product']}），退款金额 {order['amount']}元"


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )