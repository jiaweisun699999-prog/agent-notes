"""
商品搜索 MCP Server
提供产品搜索工具，支持 language 和 region 参数
"""
from fastmcp import FastMCP

mcp = FastMCP("ProductSearch")

PRODUCTS = {
    "耳机": {"zh": "无线蓝牙耳机，降噪款 ¥299", "en": "Wireless Bluetooth Earbuds, ANC $49"},
    "键盘": {"zh": "机械键盘，青轴 ¥599", "en": "Mechanical Keyboard, Blue Switch $89"},
    "显示器": {"zh": "4K显示器 27寸 ¥2499", "en": "4K Monitor 27-inch $349"},
}


@mcp.tool()
async def search_product(
    keyword: str,
    language: str = "zh",
    region: str = "CN",
    limit: int = 10,
) -> str:
    """根据关键词搜索商品，返回匹配结果"""
    results = []
    for name, texts in PRODUCTS.items():
        if keyword in name:
            desc = texts.get(language)
            results.append(f"  - {desc}（{region}区）")

    if not results:
        return f"未找到与'{keyword}'相关的商品"

    result_text = "\n".join(results[:limit])
    return f"找到 {len(results)} 个商品（显示前 {limit} 个）：\n{result_text}"


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )