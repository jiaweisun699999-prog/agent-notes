"""
MCP Server 导入文件服务
"""
from fastmcp import FastMCP, Context

mcp = FastMCP("import_server")


EXISTING_FILE=["data.zip"]



@mcp.tool()
def list_existing_files():
    return f"当前存在文件：{EXISTING_FILE}"


@mcp.tool()
async def import_file(file_name:str,ctx:Context):
   # 如果存在文件，那么向client确认操作
   if file_name in EXISTING_FILE:
       result = await ctx.elicit(
           message = f"文件{file_name} 已经存在，请确认操作？",
           response_type=["覆盖文件","跳过该文件","取消导入"]
       )

       print("result:",result)

       if result.action == "decline":
           return "用户拒绝导入"
       elif result.action == "cancel":
           return "用户取消导入"

       choice = result.data
       if choice == "覆盖文件":
           return f"文件{file_name}已经覆盖，已经成功导入"
       elif choice == "跳过该文件":
           return f"跳过文件 {file_name}"
       else:
           return f"用户取消导入文件{file_name}，因为文件已经存在，本次不导入"


if __name__ == '__main__':
    mcp.run(
        transport="http",
        port=8000,
        host="0.0.0.0"
    )
