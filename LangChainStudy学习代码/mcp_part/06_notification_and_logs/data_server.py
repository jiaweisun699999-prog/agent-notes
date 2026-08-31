"""
MCP Server 端
"""
import asyncio

from fastmcp import Context
from fastmcp import FastMCP

#导入数据的步骤
IMPORT_STAGE=["解压文件","校验字段","写入数据库"]

mcp = FastMCP("数据服务")

@mcp.tool()

async def import_data(filename:str,ctx:Context) -> str:
    """导入数据到数据库中
    Args:
        filename (str): 数据文件名
        ctx (Context): 上下文对象

    Returns:
        str: 导入结果
    """

    total = 100

    # 将日志发送到Client
    await ctx.debug(f"这是debug日志，开始导入数据 {filename}")
    await ctx.info(f"这是info日志，开始导入数据 {filename}")
    await ctx.warning(f"这是warning日志，开始导入数据 {filename}")
    await ctx.error(f"这是error日志，开始导入数据 {filename}")

    # 将进度发送到Client
    await ctx.report_progress(0,total,"开始导入数据")

    cnt = 0
    for stage_name in IMPORT_STAGE:
        await ctx.info(f"正在导入数据，当前阶段：{stage_name}")
        # 每个阶段模拟3秒的耗时时间
        await asyncio.sleep(3)
        cnt += 25
        await ctx.report_progress(cnt,total,f"导入数据 {filename} 正在进行 {stage_name}")

    await ctx.report_progress(100, total, f"导入数据成功！")

    return "全部数据已经导入成功！"


if __name__ == '__main__':
    mcp.run(
        transport="http",
        port=8000,
        host="0.0.0.0",
    )
