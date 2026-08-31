"""
通知服务
"""
from fastmcp import FastMCP, Context

mcp = FastMCP("通知服务")

@mcp.tool()
async def send_sms(phone: str, message: str,caller_id: str,ctx:Context):
    """
    发送短信通知
    Args:
        phone (str): 手机号
        message (str): 短信内容
        caller_id (str): 操作人id
    Returns:
        str: 短信通知发送成功
    """
    await ctx.info(f"正在发送短信通知到{phone}，内容：{message}")

    return f"短信通知发送成功，手机号：{phone}，内容：{message}，操作人id：{caller_id}"


# ==== resource 资源： 公司退换货政策 ====
@mcp.resource("company://policies/return",mime_type="text/markdown",description="公司退换货政策")
async def get_return_policy()->str:
    return """
            ## 退换货政策
            1. 签收后 7 天内可无理由退货（商品不影响二次销售）
            2. 质量问题 30 天内可换货，运费商家承担
            3. 退货时赠品需一并退回
            4. 退款将在收货确认后 3 个工作日内退回原支付方式
            """

# === prompt ：提示词模版=========
@mcp.prompt
def refund_response_prompt(order_id:str,amount:str)->str:
    return (
        f"好的，已为您处理订单 {order_id} 的退款。\n"
        f"退款金额：{amount} 元\n"
        f"预计 3 个工作日内退回原支付方式。\n"
        f"如有疑问可随时联系我们。"
    )


if __name__ == '__main__':
    mcp.run(
        transport="http",
        port=8020,
        host="0.0.0.0"
    )