"""
MCP Server端，股票分析服务
"""
import json

from fastmcp import FastMCP

mcp = FastMCP("股票分析服务")

#============== 股票相关工具 ==============
STOCK_DATA = {
    "AAPL": {"name": "苹果", "price": 198.5},
    "TSLA": {"name": "特斯拉", "price": 245.8},
    "000001": {"name": "平安银行", "price": 12.35},
}

@mcp.tool()
def search_stock(keyword: str) -> str:
    """搜索股票，支持股票代码或名称模糊匹配"""
    results = []
    for code, info in STOCK_DATA.items():
        if keyword.upper() in code.upper() or keyword in info["name"]:
            results.append(f"{code}（{info['name']}）")
    if not results:
        return f"未找到与 '{keyword}' 相关的股票"
    return "找到以下股票：" + "、".join(results)


@mcp.tool()
def get_quote(symbol: str) -> str:
    """获取指定股票的实时行情"""
    stock = STOCK_DATA.get(symbol.upper())
    if not stock:
        return json.dumps({"error": f"未找到 {symbol}"}, ensure_ascii=False)
    return json.dumps(stock, ensure_ascii=False)



#============== 股票相关资源 ==============
@mcp.resource("research://methodology",mime_type="text/markdown",description="公司标准的股票分析方法论")
def get_methodology():
    """获取公司标准的股票分析方法论"""
    return """
    股票分析框架：
    1.基本面分析：查看公司营收、利润、资产负债表等
    2.技术分析：查看股票价格趋势、成交量等
    3.行业分析：查看所属行业、行业趋势等
    """


@mcp.resource("market://overview",mime_type="application/json",description="当前股票市场概览")
def get_market_overview():
    """获取当前股票市场概览"""

    return json.dumps([
        {"sector": "人工智能", "change": "+3.2%", "hot_stocks": ["NVDA", "AMD"]},
        {"sector": "新能源汽车", "change": "+1.8%", "hot_stocks": ["TSLA", "BYD"]},
        {"sector": "金融", "change": "+0.5%", "hot_stocks": ["000001", "601398"]},
    ],ensure_ascii=False)


##============== 股票相关prompt ==============
@mcp.prompt
def analyze_report(stock_name: str) -> str:
    """为指定股票生成分析报告"""

    return f"""
    请为股票 {stock_name} 生成分析报告，包括基本面分析、技术分析、行业分析等。
    """


if __name__ == '__main__':
    mcp.run(
        transport="http",
        port=8000,
        host="0.0.0.0",
    )

