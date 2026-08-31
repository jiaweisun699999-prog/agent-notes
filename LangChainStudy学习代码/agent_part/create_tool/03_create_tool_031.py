from langchain.agents import create_agent
from langchain_core.tools import tool
import json
from init_llm import deepseek_llm

# 1. 直接使用JSON Schema字典定义复杂的查询参数
book_query_schema = {
    "type": "object",
    "properties": {
        "title_keyword": {
            "type": "string",
            "description": "图书标题关键词，支持模糊匹配"
        },
        "author": {
            "type": "string",
            "description": "图书作者姓名"
        },
        "category": {
            "type": "string",
            "enum": ["技术", "文学", "历史", "科学", "经济学", "传记"],
            "description": "图书分类"
        }
    },
    "required": [], # 至少需要提供标题关键词、作者或分类中的一个条件，所以这里为空
}

# 2. 使用@tool装饰器定义工具，并通过args_schema指定JSON Schema
@tool(args_schema=book_query_schema)
def query_books(title_keyword: str = None,
                author: str = None,
                category: str = None) -> str:
    """
    根据多种条件查询企业图书库中的图书信息。

    此工具用于从企业图书管理系统中检索图书。
    至少需要提供标题关键词、作者或分类中的一个条件。
    """
    try:
        # 模拟一个简单的图书数据库
        mock_books_db = [
            {"book_id": "BK1001", "title": "人工智能导论", "author": "张明", "category": "技术"},
            {"book_id": "BK1002", "title": "机器学习实战", "author": "李华", "category": "技术"},
            {"book_id": "BK1003", "title": "中国近代史", "author": "王伟", "category": "历史"},
            {"book_id": "BK1004", "title": "红楼梦", "author": "曹雪芹", "category": "文学"},
            {"book_id": "BK1005", "title": "经济学原理", "author": "刘强", "category": "经济学"},
            {"book_id": "BK1006", "title": "文学导论", "author": "张明", "category": "文学"},
            {"book_id": "BK1007", "title": "Python编程基础", "author": "王丽", "category": "技术"}
        ]

        filtered_books = mock_books_db

        # 根据条件过滤图书
        if title_keyword:
            filtered_books = [book for book in filtered_books if title_keyword.lower() in book["title"].lower()]
        if author:
            filtered_books = [book for book in filtered_books if book["author"] == author]
        if category:
            filtered_books = [book for book in filtered_books if book["category"] == category]

        if not filtered_books:
            return "未找到符合条件的图书。"

        # 格式化返回结果
        result = {
            "total_count": len(filtered_books),
            "books": filtered_books
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        return f"查询图书时发生错误: {str(e)}"


# 3. 创建智能体
agent = create_agent(
    model=deepseek_llm,
    tools=[query_books],
    system_prompt="你是一个企业图书管理员，可以帮助员工查询图书信息。",
)

# 4. 测试智能体
# 测试1：按图书种类精确查询
response1 = agent.invoke({"messages": [{"role": "user", "content": "请帮我查一下历史类图书"}]})
print("=== 测试1：按图书种类精确查询 ===")
print(response1["messages"][-1].content)

# # 测试2：多条件组合查询
# response2 = agent.invoke({"messages": [{"role": "user", "content": "我想找张明写的技术类图书"}]})
# print(response2)
# print("\n=== 测试2：多条件组合查询 ===")
# print(response2["messages"][-1].content)
#
# # 测试3：关键词模糊查询
# response3 = agent.invoke({"messages": [{"role": "user", "content": "搜索包含'Python'关键词的图书"}]})
# print("\n=== 测试3：关键词模糊查询 ===")
# print(response3["messages"][-1].content)