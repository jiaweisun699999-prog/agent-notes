"""
订单MCP 服务端
"""
import asyncio

from fastmcp import FastMCP, Context

mcp = FastMCP("订单服务")

ORDERS = {
    "ORD-001": {"product": "无线耳机", "status": "已签收", "amount": 299.0},
    "ORD-002": {"product": "机械键盘", "status": "已签收", "amount": 400.0},
    "ORD-003": {"product": "4K显示器", "status": "已签收", "amount": 2499.0},
    "ORD-004": {"product": "鼠标垫", "status": "配送中", "amount": 29.0},
}

# 查询订单服务
@mcp.tool()
async def query_order(order_id: str,caller_id:str,ctx:Context):
    """
    根据传入的 订单id 查询订单信息
    Args:
        order_id:传入的订单id
        caller_id:操作人id
        ctx: mcp 上下文
    Returns:
        返回订单的信息
    """

    await ctx.info(f"开始查询订单信息，订单id:{order_id}")

    order = ORDERS.get(order_id)

    if order:
        return (
            f"订单id:{order_id} 信息如下："
            f"商品名称:{order['product']}"
            f"订单状态:{order['status']}"
            f"订单金额:{order['amount']}"
            f"操作人id:{caller_id}"
        )
    else:
        return f"订单id:{order_id} 不存在，操作人id:{caller_id}"


# 订单退款
@mcp.tool()
async def process_refund(order_id: str,reason:str,caller_id:str,ctx:Context):
    """
    处理订单退款
    Args:
        order_id:传入的订单id
        reason:退款原因
        caller_id:操作人id
        ctx: mcp 上下文
    Returns:
        返回退款结果
    """
    await ctx.info(f"开始处理订单退款请求，订单id:{order_id}")

    order = ORDERS.get(order_id)

    if not order:
        return f"订单id:{order_id} 不存在，操作人id:{caller_id}"

    # 订单金额
    amount = order["amount"]

    # 订单金额大于等于500，通过elicitation 二次确认退款
    if amount >=500:
        result = await ctx.elicit(
            message=f"订单金额:{amount}，退款原因:{reason}，是否确认退款？",
            response_type=["确认退款","取消退款"]
        )

        if result.action == "decline":
            ctx.info(f"订单{order_id},用户拒绝退款")
            return "用户拒绝退款"
        elif result.action == "cancel":
            ctx.info(f"订单{order_id},用户取消退款")
            return "用户取消退款"
        else:
            ORDERS[order_id]["status"]="已退款"
            ctx.info(f"订单{order_id},用户确认退款")
            return f"用户确认退款，退款金额:{amount}，退款原因:{reason},已经成功退款，订单状态已更新为已退款，操作人id:{caller_id}"
    else:
        ORDERS[order_id]["status"] = "已退款"
        # 订单金额小于500，直接退款
        return f"订单id:{order_id} 退款成功，操作人id:{caller_id}"

# 批量退款订单
@mcp.tool()
async def batch_refund(order_ids: str,reason:str,caller_id:str,ctx:Context):
    """
    批量处理订单退款
    Args:
        order_ids:传入的订单id列表，每个订单id用逗号隔开
        reason:退款原因
        caller_id:操作人id
        ctx: mcp 上下文
    Returns:
        返回退款结果
    """
    await ctx.info(f"开始批量处理订单退款请求，订单id列表:{order_ids}")

    # 解析订单id列表
    ids = [order_id.strip() for order_id in order_ids.split(",")]

    #总共退款的订单数
    total_count = len(ids)
    success_count=0

    for i,order_id in enumerate(ids,1):
        await asyncio.sleep(1) #模拟等待1秒，模拟退款过程的耗时

        order = ORDERS.get(order_id)
        if order and order["status"] == "已签收" and order["amount"] < 500:
            ORDERS[order_id]["status"]="已退款"
            await ctx.info(f"订单{order_id}已经退款，操作人id:{caller_id}")
            success_count+=1
        else:
            await ctx.info(f"订单{order_id}退款失败（订单状态不是已签收而是{order['status']} 或者 订单金额{order['amount']} 大于等于500，不能退款），操作人id:{caller_id}")

        await ctx.report_progress(i,total_count,f"退款进度{i}/{total_count},退款处理中...")

    await ctx.info(f"批量退款处理完成，{success_count}/{total_count} 成功")
    return f"批量处理订单退款完成，退款订单id列表:{order_ids}，退款成功个数:{success_count}，退款失败个数:{total_count-success_count},操作人id:{caller_id}"


if __name__ == '__main__':
    mcp.run(
        transport="http",
        port=8010,
        host="0.0.0.0"
    )