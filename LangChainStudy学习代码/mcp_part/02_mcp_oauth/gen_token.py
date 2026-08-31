"""
运行该代码会生成：RSA 密钥对 - 公钥和私钥
 公钥后续要交给MCP Server，私钥要交给MCP Client。

"""
from fastmcp.server.auth.providers.jwt import RSAKeyPair

key_pair = RSAKeyPair.generate()

# 1. 生成公钥和私钥
# 公钥
public_key = key_pair.public_key

# 私钥
private_key = key_pair.private_key.get_secret_value()




# 2. 生成JWT Token
jwt_token = key_pair.create_token(
    # Token的主体(Agent 名称)
    subject="my_agent",
    # 签发方的标识,Server验证token的时候会验证
    issuer="my_company_auth_server",
    # 接收方的标识,Server验证token的时候会验证
    audience = "internal_mcp_server",
    # token过期时间
    expires_in_seconds=3600
)

# 3.输出 JWT Token
print("公钥：public_key:", public_key)
print("-----------------")
print("私钥：private_key:", private_key)
print("-----------------")
print("JWT Token:", jwt_token)




