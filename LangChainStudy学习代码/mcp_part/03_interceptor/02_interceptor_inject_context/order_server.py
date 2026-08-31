from fastmcp import FastMCP

mcp = FastMCP("OrderServer")

ORDERS = {
    "ORD-001": {"product": "无线耳机", "status": "已签收", "amount": 299.0},
    "ORD-002": {"product": "机械键盘", "status": "待发货", "amount": 599.0},
    "ORD-003": {"product": "显示器", "status": "已完成", "amount": 1299.0},
}


@mcp.tool
def query_order(order_id:str,caller_id:str = "") -> str:
    "查询指定的订单详细信息，包括执行人"
    order = ORDERS.get(order_id)
    if not order:
        return f"订单 {order_id} 不存在"
    return (
        f"订单 {order_id} "
            f"商品： {order['product']} "
            f"状态： {order['status']} "
            f"金额： {order['amount']}，"
            f"操作人： {caller_id}"
    )

@mcp.tool
def submit_refund(order_id:str, reason: str, caller_id:str = "") -> str:
    "提交退款申请"
    order = ORDERS.get(order_id)
    if not order:
        return f"订单 {order_id} 不存在,无法提交退款申请"
    if order["status"] == "已签收":
        return f"订单 {order_id} 已签收,无法提交退款申请"

    return (
        f"订单 {order_id} 已提交退款申请,退款原因: {reason}，退款金额: {order['amount']}"
        f"退款人：{caller_id}"
    )

if __name__ == '__main__':
    mcp.run(transport="http",
            host="127.0.0.1",
            port=8000)


