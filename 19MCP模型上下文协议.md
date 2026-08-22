# 9\. **Model Context Protocol (MCP)模型上下文协议**

## 9.1. **MCP介绍**

### **9.1.1. 什么是MCP？**

Model Context Protocol（MCP）是一套开放协议，规定了LLM应用与外部工具、数据源之间的标准化通信方式。它为"模型如何发现工具有哪些能力、怎么调用工具、工具怎么返回结果"这个问题，提供了一套通用规范。MCP由 Anthropic于2024年11月发布并开源，至今已获得几乎所有主流 AI 平台的支持。

![image.png](./images/19MCP模型上下文协议_efad19a4bca848a290f0407a6049805f_126038.jpg)

没有MCP之前，开发者每接入一个外部服务，就要写一套适配代码：定义工具 Schema、处理认证、解析返回值、写工具描述让LLM理解怎么用。100个工具 × 3个Agent = 300次重复劳动，这个场景被称为 "N×M 问题"。

MCP把复杂度从N×M降到了N+M。每个服务只实现一次MCP服务器，所有支持MCP的客户端都能直接使用。换个角度说：写一次工具，到处可用。

LangChain Agent场景下，这直接解决了两个痛点：

1) 工具复用：一个MCP服务器写好之后，可以被多个Agent共享，不需要在每个项目里重新定义工具。
2) 工具与Agent解耦：工具提供方（比如后端团队）只维护MCP服务器，Agent开发者只负责组装和使用——职责边界清楚

### **9.1.2. MCP架构角色**

![image.png](./images/19MCP模型上下文协议_511389443d824eebb01a954bf8720f80_b291ea.jpg)

可以将 MCP 理解为 AI 世界里的“USB-C标准”，为模型接入各种数据源和工具提供了统一接口，确保连接便捷且安全。

MCP 采用经典的客户端-服务器架构，包含三个核心角色：

* MCP Host：用户直接交互的 AI 应用（如 Claude Desktop、LangChain Agent）。
* MCP Client：与 MCP Server 建立一对一连接的客户端，负责解析模型请求并转发到对应的 MCP Server。
* MCP Server：实际运行外部工具（如访问文件系统、发送邮件、查询日历）的服务端，负责处理请求并将结果返回给 Client。

MCP Client与MCP Server之间有两种通信机制：Stdio（标准输入/输出）和Streamable HTTP(服务器发送事件)，两种机制介绍如下：

* Stdio（标准输入/输出）：当服务器和客户端同时运行在本机时，可以使用Stdio机制。
* Streamable HTTP：当服务器部署在远程服务器上，客户端通过HTTP 请求发送消息使用这种方式。

## 9.2. **LangChain Agent集成MCP**

LangChain Agent集成MCP核心组件就两个：MCP Server（提供工具的一方）和 MultiServerMCPClient（消费工具的一方）。

* 创建MCP Server可以使用FastMCP 库（需要安装fastmcp），该库是目前最流行的python MCP Server框架。
* MultiServerMCPClient 是 LangChain 接入 MCP 的入口，它管理一个或多个 MCP Server 的连接，并将 Server 暴露的工具注册到 LangChain 中供 Agent 使用。

LangChain 通过 langchain-mcp-adapters 库将 MCP Tool 转换为 LangChain 的 BaseTool 实例,从 Agent 的角度看，使用 MCP Tool 和使用普通 LangChain Tool 没有任何区别，可以像使用本地工具一样使用远程 MCP 服务——因为 MCP Tool 已经被"适配"成了 LangChain Tool。

LangChain集成MCP 必须安装如下依赖：

```python
pip install fastmcp==3.4.2
pip install langchain-mcp-adapters==0.3.0
```

MCP 在LangChain中的使用示意图如下：

![image.png](./images/19MCP模型上下文协议_faa425252e2c4c439fc3d029593a967c_f2a7af.jpg)

### **9.2.1. 传输方式**

Langchain集成mcp同样支持两种传输方式来承载客户端与服务器之间的通信：stdio和HTTP。

#### **9.2.1.1. stdio传输**

stdio 传输让客户端以子进程的方式启动 MCP 服务器，通过标准输入/标准输出通信。适合本地工具和简单场景——不需要网络配置，开箱即用。

langchain中使用stdio传输配置示例如下：

```python
... ...
client = MultiServerMCPClient(
    {
        "my_server": {
            "transport": "stdio",
            "command": "python",                     # 启动命令
            "args": ["/path/to/server.py"],           # 命令参数
        }
    }
)
tools = await client.get_tools()
... ...
```

以上参数解释如下：

* my\_server:自定义Server名称。
* transport:传输模式，固定为 "stdio"。
* command：启动命令（如 "python" 或 "node"）。
* args:命令参数列表，第一个通常是Server脚本的绝对路径。

关于Stdio更多可配参数参考：[https://reference.langchain.com/python/langchain-mcp-adapters/sessions/StdioConnection](https://reference.langchain.com/python/langchain-mcp-adapters/sessions/StdioConnection)

#### **9.2.1.2. Streamable HTTP 传输**

HTTP 传输（官方称为 streamable-http）是远程 MCP 服务器的标准选择。服务器作为一个独立的 HTTP 服务运行在某台机器上，客户端通过 HTTP 请求与它通信。适用场景： 生产环境、多客户端共享、远程部署、需要认证鉴权的场景。

关于 SSE 的历史： 早期 MCP 协议版本（2024-11-05）使用独立的 HTTP+SSE 传输——客户端通过 HTTP POST 发送请求，通过 SSE 连接接收服务端推送。在 2025-03-26 版本中被 Streamable HTTP 替代，统一使用同一个 HTTP 端点处理所有请求和流式响应。新版本兼容旧版，但推荐所有新项目使用 Streamable HTTP。Streamable HTTP相比之前的HTTP+SSE方式可以更灵活处理请求，并不需要长连接，可以根据需要进行流式传输或者一次请求。

langchain中使用http传输配置示例如下：

```python
... ...
client = MultiServerMCPClient(
    {
        "my_server": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
            "headers": {
                "Authorization": "Bearer YOUR_TOKEN",
            },
        }
    }
)
tools = await client.get_tools()
... ...
```

以上参数解释如下：

* my\_server:自定义Server名称。
* transport:传输模式，固定为 "http"。
* url：MCP服务器的HTTP端点。
* headers:可选，自定义HTTP请求头（认证Token等）

关于HTTP模式更多可配参数参考：[https://reference.langchain.com/python/langchain-mcp-adapters/sessions/StreamableHttpConnection](https://reference.langchain.com/python/langchain-mcp-adapters/sessions/StreamableHttpConnection)

#### **9.2.1.3. 传输方式对比**

| **特性**         | **Stdio**          | **Streamable HTTP** |
| ---------------------- | ------------------------ | ------------------------- |
| **通信方式**     | 标准输入/输出（子进程）  | HTTP POST/GET             |
| **部署位置**     | 本地（客户端启动子进程） | 独立部署的Web 服务        |
| **多客户端共享** | 不支持（一对一）         | 支持（一对多）            |
| **认证支持**     | 不适用（本地进程）       | Header 认证 / OAuth2      |
| **适用场景**     | 本地开发、单机工具       | 生产环境、共享服务        |

### **9.2.2. 创建MCP服务器**

如下代码是创建stdio传输版本——本地工具服务（math\_[server.py](http://server.py)）：

```python
"""
客户端以子进程方式启动此脚本，通过标准输入/输出通信
"""
from fastmcp import FastMCP

# 创建一个 MCP Server 实例，名为 "Math"
mcp = FastMCP("Math")


@mcp.tool()
def add(a: int, b: int) -> int:
    """将两个数字相加"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """将两个数字相乘"""
    return a * b

if __name__ == "__main__":
    # 以 stdio 模式启动
    mcp.run(transport="stdio")
```

如下代码是创建HTTP传输版本——远程天气服务(weather_server.py)：

```python
"""
在 localhost:8000/mcp 启动一个 Web 服务
"""
from fastmcp import FastMCP

# 创建一个 MCP 服务, 服务名称为 "Weather"
mcp = FastMCP("Weather")


@mcp.tool()
async def get_weather(location: str) -> str:
    """获取指定城市的天气信息"""
    # 实际项目中应调用外部天气 API
    weather_data = {
        "北京": "晴，22~28°C，北风3级",
        "上海": "多云，25~30°C，东南风2级",
        "深圳": "阵雨，26~31°C，南风4级",
    }
    return weather_data.get(location, f"暂未找到 {location} 的天气数据")


if __name__ == "__main__":
    # 以 streamable-http 模式启动，监听 8000 端口
    mcp.run(transport="streamable-http")
```

以上stdio、http两种方式创建MCP服务器注意点如下：

* @mcp.tool() 装饰器将普通 Python 函数注册为 MCP 工具。函数的类型注解（a: int, b: int -> int）自动转化为 MCP 工具的 JSON Schema，客户端可以据此进行参数校验。“@mcp.tool()”中的“mcp”名称要和“mcp = FastMCP("Weather")”变量名称一样。
* 函数的 docstring 会被用作工具的描述信息。LLM 根据这段描述理解工具的用途并决定何时调用。所以工具描述要写得清晰、准确——这是影响 Agent 行为质量的关键因素。
* FastMCP 不需要额外的手动配置即可将类型注解映射为 JSON Schema。int 映射为  number ， str 映射为 string ，复杂的 Pydantic 模型也能自动识别。
* 这里使用了 async def get\_weather ——FastMCP 同时支持同步和异步函数。
* [mcp.run](http://mcp.run)中除了transport参数外，还支持如下常见参数

| **参数** | **类型** | **说明**                                                                     |
| -------------- | -------------- | ---------------------------------------------------------------------------------- |
| transport      | str            | mcp传输协议，默认“stdio”，支持“stdio”、“http”、“sse”、“streamable-http”  |
| host           | str/None       | HTTP模式专属参数，表示监听地址，默认值为“127.0.0.1”，生产环境可以改为“0.0.0.0” |
| port           | int/ None      | HTTP模式专属参数，表示监听端口，默认8000                                           |
| path           | str/ None      | HTTP模式专属参数，表示MCP端点路径，默认为“/mcp”                                  |
| show_banner    | bool           | 是否在启动时打印FastMCP 横幅 Logo。默认值True                                      |
| log_level      | str/ None      | 默认值None，日志级别，如 "DEBUG"、"INFO"、"WARNING"                                |

### **9.2.3. Agent配置MCP工具**

有了MCP Server，下一步是用 MultiServerMCPClient 连接它、加载工具、传给 Agent。核心模式三步走：

1) 创建 MultiServerMCPClient ，配置服务器的 transport 和连接参数
2) await client.get\_tools() 加载所有服务器上的工具，转换为 LangChain BaseTool 列表
3) 把工具列表传给 create\_agent() ，Agent 就能自主发现和调用这些工具。

如下代码是使用以上stdio、http两种方式MCP Server端的工具：

```python
"""
LangChain Agent 集成 MCP
同时连接数学工具和天气工具两个 MCP Server

"""
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

from init_llm import deepseek_llm


async def main():
    # 1. 创建 MCP 客户端——通过字典配置多个 Server 的连接信息
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "stdio",          # stdio 本地子进程通信
                "command": "D:/ProgramData/miniconda3/envs/langchain_v1.2/python.exe",  # 指定所使用的 Python 解释器路径
                "args": ["D:/PyCharmSpace/LangChainV1.2Project/08_mcp/quick_start/math_server.py"],  # MCP Server 脚本的绝对路径
                "env": {                       # 传给子进程的环境变量，确保 UTF-8 编码
                    "PYTHONIOENCODING": "utf-8",
                },
            },
            "weather": {
                "transport": "http",           # HTTP 远程通信
                "url": "http://localhost:8000/mcp",
            },
        }
    )

    # 2. 从所有已配置的 Server 中加载工具，转换成 LangChain BaseTool 列表
    tools = await client.get_tools()

    print(f"加载到的工具: {tools}")

    # 3. 像使用普通 LangChain Tool 一样传入 Agent
    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
    )

    # 4. Agent 调用时，MCP 工具和普通 LangChain 工具无区别
    math_response = await agent.ainvoke({"messages": [{"role": "user", "content": "计算 (3 + 5) × 12 的结果"}]})
    weather_response = await agent.ainvoke({"messages": [{"role": "user", "content": "上海今天的天气怎么样？"}]})

    print("math_response",math_response)
    print("weather_response",weather_response)

    print(f"数学结果: {math_response['messages'][-1].content}")
    print(f"天气结果: {weather_response['messages'][-1].content}")




if __name__ == "__main__":
    asyncio.run(main())

```

运行以上代码需要提前将“weather\_[server.py](http://server.py)”代码启动，“math\_[server.py](http://server.py)”不必启动。以上运行后结果如下：

![image.png](./images/19MCP模型上下文协议_1a14029b679042a698c1a9d98e0f4bcb_4d59d5.jpg)

![image.png](./images/19MCP模型上下文协议_7c5084a47ead4d9e8caa84c03168b827_808114.jpg)

以上代码需要注意如下几点：

* MultiServerMCPClient 接收一个字典，key 是 Server 的自定义名称，value 是连接配置，你可以只连接一个 Server，也可以同时连接数十个。字典中的每个 Server 都有独立的传输配置——stdio 用于本地子进程，http 用于远程服务。
* await client.get\_tools() 会遍历所有已配置的 Server，发起 MCP 协议的 tools/list 请求，获取每个 Server 的完整工具列表，然后将它们全部转换为 LangChain 的 BaseTool。get\_tools() 的底层行为本身就是异步 I/O，无论是 stdio（进程间通信）还是 HTTP（网络请求），都需要等待外部进程/服务响应，所以这里需要使用await。
* “"PYTHONIOENCODING": "utf-8"”参数设置在“env”中，表示启动子进程所使用的环境变量，这里设置为utf-8编码，否则会出现乱码。

### **9.2.4. LangChain Agent Tools与MCP Tools 区别**

LangChain Tool 是一个框架内的工具定义方式，MCP Tool 是一个跨框架的工具标准协议，两者对比如下：

| **维度**     | **LangChain Tool**      | **MCP Tool**                                      |
| ------------------ | ----------------------------- | ------------------------------------------------------- |
| **本质**     | 框架级别的抽象（Python 对象） | 协议级别的定义                                          |
| **定义方式** | @tool 装饰器或 BaseTool子类   | FastMCP @mcp.tool() 装饰器                              |
| **运行位置** | Agent 同一进程内              | 独立的MCP Server 进程                                   |
| **通信方式** | 直接函数调用                  | stdio 或 HTTP 远程调用                                  |
| **跨框架**   | 仅限LangChain/LangGraph       | 所有MCP 客户端（Claude、ChatGPT、LangChain、Cursor 等） |
| **复用性**   | 每换一个框架需重写            | 一次编写，随处使用                                      |

使用LangChain Tool场景：工具逻辑简单，与 Agent 运行在同一进程即可；工具只有在本项目中用，不需要被其他 AI 应用消费。

使用MCP Tool场景：工具需要被多个 AI 应用共享（如公司统一的订单查询服务）；工具有独立的认证、权限、限流要求。

在实际项目中，两者往往不是非此即彼的关系。一个常见的模式是：

* 将通用业务能力封装为 MCP Server（订单服务、库存服务、通知服务）
* 将特定 Agent 逻辑保留为普通 LangChain Tool（格式化输出、Prompt 构建、内部状态读写）

这样既获得了 MCP 的标准化和跨平台能力，又保留了 LangChain 框架的开发灵活性。

## 9.3. **MCP认证与安全**

MCP（Model Context Protocol）的认证机制主要用于 HTTP 传输层的安全保护。当 MCP 服务器通过 HTTP/SSE 对外暴露时，必须确保只有经过授权的客户端才能调用其中的工具和资源。FastMCP 和 MCP Python SDK 共同提供了一套基于 OAuth 2.0 和 JWT（JSON Web Token）标准的认证体系，支持从简单的 Bearer Token 验证到完整的 OAuth 2.0 授权服务器等多种认证模式。

注意：认证仅对 HTTP 传输（http、sse、streamable\_http）生效，stdio 传输依赖本地进程隔离来保证安全，不需要额外的认证层。

### **9.3.1. 什么是OAuth&JWT(了解)**

OAuth 2.0是一个"授权委托"协议，解决的核心问题是：如何让第三方应用在不知道用户密码的情况下，以用户的身份访问受保护资源。OAuth2.0定义了四个角色：

| **角色**                             | **在MCP中的对应**           |
| ------------------------------------------ | --------------------------------- |
| **Resource Owner（使用资源者）**     | 当前使用Agent的用户               |
| **Client(客户端)**                   | AI Agent / MCP 客户端             |
| **Authorization Server(授权服务器)** | Auth0 / 自建Token服务             |
| **Resource Server（资源服务器）**    | MCP Server（验证Token后提供工具） |

Owner登录Client后想要访问Resource Server中的资源，**核心流程为：Client 首先去找 Authorization Server 拿 Token，然后带着 Token 访问 Resource Server，Resource Server 验证 Token 后放行**。

JWT（JSON Web Token）是一种紧凑、自包含的 Token 格式，即Token 的“身份证”格式。它的结构是三段 Base64 编码的字符串，用 . 分隔：

```python
Header.Payload.Signature
eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhZ2VudC0wMDEi.签名内容
```

* Header：描述签名算法（如 RS256）。
* Payload：存放"声明"（Claims），即 Token 里写了什么信息，例如谁签发的（iss）、给谁用的（aud）、谁持有的（sub）、有什么权限（scope）、什么时候过期（exp）。
* Signature：用私钥对前两部分做的数字签名，只能用对应的公钥来验证。签名保证了 Token 内容没有被篡改过。

JWT 的关键特性是无状态——服务器不需要存任何 Session，拿到 Token 后用公钥验证签名即可知道它是否合法。

### **9.3.2. MCP 认证架构**

下图清晰地展示了MCP认证全流程，该图包含完整的 MCP 认证序列图，展示了 Client、MCP Server、Authorization Server三者之间的交互流程。

官网：[https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)

![image.png](./images/19MCP模型上下文协议_e4664178502e4608ae6797bb5fec3999_37217d.jpg)

以上各个角色的职责如下：

1\. Authorization Server（授权服务器 / Token 签发者）

* 持有私钥（Private Key），用来给 JWT 签名。
* 决定给谁发 Token、Token 里写什么权限（scopes）、Token 有效期多长。
* 在企业中通常是自建认证服务，也可以是一个简单的自建签发脚本。

2\. MCP Server（资源服务器）

* 持有公钥（Public Key），用来验证 JWT 的数字签名，MCP Server 从不接触私钥，它只负责验证。
* 配置 JWTVerifier（或更高级的 OAuthProvider），对每个请求自动执行认证。
* 验证 Token 的签名、签发方（issuer）、接收方（audience）、过期时间（exp）、权限范围（scopes）。
* 认证通过后，将用户身份信息注入到请求上下文中，供工具函数使用。

3\. MCP Client（AI Agent）

* 从授权服务器获取 JWT Token。
* 在建立 HTTP 连接时，通过 headers 参数将 Token 作为 Authorization: Bearer &#x3c;token> 传入。
* 无需理解 Token 的内部结构，只需持有并传递即可。

**MCP 认证流程分为三个核心阶段：**

阶段一：认证发现（步骤 ①~④）——Client 第一次访问 MCP Server 时，Server 返回 401 并告知"你应该去找哪个授权服务器拿 Token"。Client 通过标准化的 .well-known 路径自动发现授权服务器的端点。

阶段二：获取 Token（步骤 ⑤~⑥）——Client 向授权服务器发起 OAuth 的授权码流程，拿到一个有时限的 JWT Access Token。

阶段三：携带 Token 访问（步骤 ⑦~⑨）——Client 把 Token 放在 HTTP 请求头 Authorization: Bearer &#x3c;token> 中发给 MCP Server，Server 用公钥验证 Token 合法后提供工具服务。

特别提示：以上是 MCP 规范的完整 OAuth 流程，适合多用户、需要动态授权的场景。在实际企业内部的机器对机器（M2M）场景中，流程可以大大简化——授权服务器直接为 Agent 签发 Token，Client 拿到 Token 后直接访问 MCP Server 即可（跳过步骤 ①~④）。后续的实战案例就是这种简化模式。

### **9.3.3. MCP认证案例**

某公司有一个内部 MCP 服务器，对外提供员工信息查询和部门预算查询两个工具。公司已经有一个统一的认证中心（这里简化为一个 Token 生成脚本），Agent 需要先从认证中心获取 JWT Token，然后携带 Token 访问 MCP 服务器。

我们将代码分为三个文件：

| **文件**          | **角色**                 | **职责**                                                              |
| ----------------------- | ------------------------------ | --------------------------------------------------------------------------- |
| **gen_token.py**  | Authorization Server（简化版） | 生成RSA 密钥对，用私钥签发 JWT Token，输出公钥和 Token 供另外两个文件使用。 |
| **mcp_server.py** | MCP Server（Resource Server）  | 配置 JWTVerifier 用公钥验证 Token，对外暴露受保护的工具。                   |
| **mcp_client.py** | MCP Client（AI Agent）         | 将Token 放入 HTTP 请求头，连接 MCP Server 并调用工具。                      |

**第一步，生成公钥和Token。**

gen\_[token.py](http://token.py)，运行如下代码将生成：RSA 密钥对；一份公钥（后续复制到 mcp\_[server.py](http://server.py) 中）；一个 JWT Token（后续复制到 mcp\_[client.py](http://client.py) 中）。

```python
from fastmcp.server.auth.providers.jwt import RSAKeyPair

# 1.生成 RSA 密钥对
key_pair = RSAKeyPair.generate()

private_key = key_pair.private_key.get_secret_value()  # 私钥，用于签发 Token（保密）
public_key = key_pair.public_key                        # 公钥，用于验证 Token（可公开）

# 2.用私钥签发 JWT Token （create_token方法内已包含私钥的使用）
jwt_token = key_pair.create_token(
    subject="agent-011",                # sub: Token 代表的主体（这里是 Agent 的 ID）
    issuer="my-company-auth-server",    # iss: 签发方标识，Server 会校验此值
    audience="internal-mcp-server",     # aud: 接收方标识，表明 Token 是专门给这个 MCP Server 用的
    expires_in_seconds=3600,            # exp: Token 1 小时后过期
)

# 3.输出结果
print("=" * 70)
print("公钥：后续复制到 mcp_server.py 的 PUBLIC_KEY 变量中")
print("=" * 70)
print(public_key)
print()
print("=" * 70)
print("JWT Token：后续复制到 mcp_client.py 的 JWT_TOKEN 变量中")
print("=" * 70)
print(jwt_token)
print()
```

以上代码注意如下几点：

1) 模拟企业认证中心签发 JWT Token，在实际企业中，这一步通常由自建认证服务完成，Agent 通过登录接口获取 Token。
2) subject（sub）：Token 代表的主体身份，通常是用户 ID 或 Agent ID。MCP Server 验证通过后可以通过 AccessToken.client\_id 获取这个值，实现"知道是谁在调用工具"。
3) issuer（iss）：签发方标识，是一个你自己定义的字符串或 URL。Server 端的 JWTVerifier 会严格比对，只有 iss 匹配的 Token 才被接受。这防止了"拿一个由其他认证中心签发的 Token 来冒充"。
4) audience（aud）：接收方标识，表示这个 Token 是签发给谁用的。Server 端会检查 Token 的 aud 中是否包含自己配置的值。这是防止 Token 跨服务滥用的关键机制：即使攻击者拿到了一个合法 Token，如果它不是签发给这个 MCP Server 的，也无法使用。

**第二步:服务端配置认证，使用公钥认证Token。**

mcp\_[server.py](http://server.py):

```python
"""
MCP Server 服务端：
    所有请求必须携带有效的 JWT Token，否则返回 401。
"""
from fastmcp import FastMCP
from fastmcp.server.auth import JWTVerifier

# 1. 配置：将 gen_token.py 输出的公钥内容完整粘贴到这里（包含 BEGIN/END 行）
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs/WavxnBoIX/sclvsdv3
IFrz09nDCWgnWQUZ581/tgYt4uE7zrFM0qzhwEZvuApRtG/jdI+7fm6pk+FMUzDy
QilXk1zoiMe8LKSSIFWVYZ82HNsIreii4WSjeLfjtbNSSoUUOPWNUFtFUCj+yd3c
DvSadOIH3UcQYvaFvLn0Np5kljPmVMcn82FaCOudXDoKtn/z0Gqca1Yc6RCb8Zzz
seE0or+8AjYsLeBWWhJEa2vRvXAvGVt2AEzwbvvbVQYnKs/kOh+ZIt/01ROfzeqS
zKrQXSVjizwp5dPY7IwnBeEEMFUrfEPsBKaCOO4ed8z79PlNihdADjIbpOTUjMtA
KwIDAQAB
-----END PUBLIC KEY-----"""

# 2. 创建 JWTVerifier 认证提供方
auth = JWTVerifier(
    public_key=PUBLIC_KEY,              # 用这个公钥验证 JWT 签名
    issuer="my-company-auth-server",    # 只接受由此签发方签发的 Token，这里要与 gen_token.py 中的 issuer 一致
    audience="internal-mcp-server",     # 只接受签发给本服务的 Token，这里要与 gen_token.py 中的 audience 一致
    algorithm="RS256",                  # 签名算法，需与签发时一致
)

# 3. 创建带认证的 MCP 服务器
mcp = FastMCP("Internal Tools Server", auth=auth)

# 模拟的企业数据
EMPLOYEE_DB = {
    "E001": {"name": "张三", "department": "技术部", "position": "高级工程师"},
    "E002": {"name": "李四", "department": "财务部", "position": "财务经理"},
    "E003": {"name": "王五", "department": "市场部", "position": "市场总监"},
}

BUDGET_DB = {
    "技术部": {"total": 5000000, "used": 3200000, "remaining": 1800000},
    "财务部": {"total": 1500000, "used": 900000,  "remaining": 600000},
    "市场部": {"total": 3000000, "used": 2100000, "remaining": 900000},
}


# 4. 定义受保护的工具
@mcp.tool()
async def query_employee(employee_id: str) -> str:
    """查询员工基本信息。

    参数:
        employee_id: 员工编号，例如 E001
    """
    employee = EMPLOYEE_DB.get(employee_id)
    if employee is None:
        return f"未找到员工编号为 {employee_id} 的记录"
    return (
        f"员工信息：姓名={employee['name']}，"
        f"部门={employee['department']}，"
        f"职位={employee['position']}"
    )


@mcp.tool()
async def query_department_budget(department: str) -> str:
    """查询部门预算信息。

    参数:
        department: 部门名称，例如 "技术部"
    """
    budget = BUDGET_DB.get(department)
    if budget is None:
        return f"未找到部门 '{department}' 的预算记录"
    return (
        f"部门预算：总额={budget['total']/10000}万，"
        f"已用={budget['used']/10000}万，"
        f"剩余={budget['remaining']/10000}万"
    )


# 5. 启动服务器
if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )

```

以上代码注意：

1) PUBLIC\_KEY就是将 gen\_[token.py](http://token.py) 输出的公钥内容完整粘贴到这里（包含 BEGIN/END 行）
2) JWTVerifier中的issuer、audience要与 gen\_[token.py](http://token.py) 中的 issuer要与 gen\_[token.py](http://token.py) 中的 issuer 一致，否则后续认证报错。

**第三步：客户端携带Token连接访问MCP Server。**

mcp\_[client.py](http://client.py)：

```python
"""
客户端只需将 Token 放入 headers 即可完成认证，无需理解 JWT 内部结构。
"""
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

from init_llm import deepseek_llm

# 1. 将从 gen_token.py 输出的 JWT Token 粘贴到这里
JWT_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhZ2VudC0wMTEiLCJpc3MiOiJteS1jb21wYW55LWF1dGgtc2VydmVyIiwiaWF0IjoxNzgzOTUzNDYzLCJleHAiOjE3ODM5NTcwNjMsImF1ZCI6ImludGVybmFsLW1jcC1zZXJ2ZXIifQ.iGqolffc1OGVCqDQKGAVhdHW5VPCQW-TCRbAY6_haN0K3peuRRB0jsOXSa9wpj-2jzCIii9hq6xYTDvVMd4Fw4sAKQFKeTzGr-g0cYw0kJZcTaVxhHzwE48pQAYJAZHkGJtUo2cT0-qm87ol4uZTpz5JtXahZsOjbSQaZLctKhn3jmdguY_l1WfxRhdz5AUibx461tZ4s6l7xqMy4LmAsRxG15f_jtjXF5CL6UxJMAARQujQrG-jloPlv3HyyV5EgWagT1TxzLbqZPVNfCnxu1uK8SIFLu2H0IFko3osd597QZkUQ62ONuC-WmCVcobzuZZu_dIBvYxOPYI6Q9jWwA"


# 2. 创建 MCP 客户端，通过 headers 携带 Bearer Token
async def main():
    client = MultiServerMCPClient(
        {
            "internal_tools": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
                # 将 Token 放入 Authorization 请求头
                "headers": {
                    "Authorization": f"Bearer {JWT_TOKEN}",
                },
            }
        }
    )

    # 获取工具列表并创建 Agent
    tools = await client.get_tools()

    agent = create_agent(
        deepseek_llm,
        tools
    )

    # 场景 1：查询员工信息
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "帮我查一下员工 E001 的信息"}]}
    )
    print(f"Agent 回复: {response['messages'][-1].content}")

    print("="*50)

    # 场景 2：查询部门预算
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "技术部的预算使用情况如何？"}]}
    )
    print(f"Agent 回复: {response['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())
```

以上三个代码，先运行 gen\_[token.py](http://token.py) 生成公钥和Token，将公钥复制到mcp\_[server.py](http://server.py) 中，将Token复制到mcp\_[client.py](http://client.py)中，然后依次启动mcp\_[server.py](http://server.py)和mcp\_[client.py](http://client.py)即可。

## 9.4. **工具拦截器（Tool Interceptor）**

理解拦截器之前，先看清 MCP 的架构限制：MCP Server 以独立的子进程或远程服务运行，与 Agent 所在的进程完全隔离。这意味着：

* Server 不知道当前用户是谁，如：查询订单时无法判断"谁在查"
* Server 不知道 Agent 的状态，无法根据对话上下文决定是否执行操作
* Server 无法访问 LangChain中Store，不能读取跨会话的用户偏好数据

一种直接的做法是：把认证、权限、日志这些逻辑写在每个 Tool 函数内部，但这会导致：

1) Server 代码膨胀：工具函数被认证、限流、审计等"横切逻辑"填满，业务代码淹没在基础设施代码中
2) 逻辑重复：每写一个新的 MCP Server，都要重新实现一遍认证和日志
3) 职责混乱：Server 应该关心"做什么"，不应该关心"谁来做"和"有没有权限做"

拦截器（Interceptor）在适配器层解决了这个问题，它位于"Agent 发出工具调用请求"和"MCP Server 收到请求"之间，在不修改 Server 代码的前提下完成运行时上下文的注入和横切逻辑的统一处理。

![image.png](./images/19MCP模型上下文协议_8c1b6ebb89014645aae19ef14fe38227_addbf0.jpg)

拦截器的核心能力如下：

| **能力**             | **说明**                                 |
| -------------------------- | ---------------------------------------------- |
| **注入运行时上下文** | 如将用户ID、API Key、会话信息等传递给 MCP 工具 |
| **横切逻辑统一管理** | 如认证、权限、限流、日志集中在拦截器中实现     |
| **修改请求与响应**   | 在调用工具前后加工参数、头部或返回值           |
| **流程控制**         | 短路拦截（直接返回结果而不调用工具）、路由跳转 |

特别提示：拦截器是 langchain-mcp-adapters 提供的扩展能力，不属于 MCP 协议本身。

### **9.4.1. 拦截器使用案例**

工具拦截器是一个异步函数，在LangChain 应用（MCP Client端）中实现，接收 MCPToolCallRequest 和 handler，在调用工具前后做自定义操作，使用示例如下：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest

... ...
async def logging_interceptor(request: MCPToolCallRequest, handler):
    """记录每次工具调用的入参和返回结果"""
    print(f"[MCP] 调用工具: {request.name}, 参数: {request.args}")
    result = await handler(request)       # 调用下一个拦截器或实际工具
    print(f"[MCP] 工具返回: {result}")
    return result


client = MultiServerMCPClient(
    {"math": {"transport": "stdio", "command": "python", "args": ["server.py"]}},
    tool_interceptors=[logging_interceptor],  # 传入拦截器列表
)
... ...
```

如下案例构建MCP Server端和Client端，调用工具前，通过工具拦截器进行日志输出，使用方式。

match\_[server.py](http://server.py):

```python
from fastmcp import FastMCP

mcp = FastMCP("MathService")


@mcp.tool()
def add(a: int, b: int) -> int:
    """计算两个整数的和"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """计算两个整数的积"""
    return a * b


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )
```

interceptor\_[demo1.py](http://demo1.py):

```python
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain.agents import create_agent

from init_llm import deepseek_llm


# ============ 定义一个日志拦截器 ============
async def logging_interceptor(request: MCPToolCallRequest, handler):
    """在每次 MCP 工具调用前后打印日志"""
    print("request:", request)
    print(f"[拦截器] 调用前 —— 工具: {request.name}, 参数: {request.args}")
    result = await handler(request)   # 调用下一个拦截器（或实际工具）
    print(f"[拦截器] 调用后 —— 工具: {request.name}, 返回: {result}")
    return result


async def main():
    # 创建 MCP 客户端，通过 tool_interceptors 参数传入拦截器
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            },
        },
        tool_interceptors=[logging_interceptor],   # 传入拦截器列表
    )

    tools = await client.get_tools()

    print(f"已加载工具: {[t.name for t in tools]}")

    agent = create_agent(
        model=deepseek_llm,
        tools=tools
    )

    response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "请计算 8 乘以 5 的结果"}]
    })
    print(f"Agent 最终回复: {response['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())
```

首先运行Server端代码，然后运行Client端代码，可以看到如下日志：

![image.png](./images/19MCP模型上下文协议_fbd29009ad4643a0b8258d916219aa19_eb5c85.jpg)

以上就是拦截器的基本形态：一个异步函数，接收请求和处理器，在调用 handler(request) 前后执行自定义逻辑。

当在“tool\_interceptors”参数中传入多个拦截器时，它们按传入顺序依次执行且是洋葱式嵌套方式执行——第一个拦截器是"最外层"，最后一个是最内层：

```python
async def outer(request, handler):
    print("外层: before")
    result = await handler(request)
    print("外层: after")
    return result

async def inner(request, handler):
    print("内层: before")
    result = await handler(request)
    print("内层: after")
    return result

# tool_interceptors=[outer, inner] 的执行顺序：
# 外层: before → 内层: before → 工具执行 → 内层: after → 外层: after
```

![image.png](./images/19MCP模型上下文协议_310a11bbfd6a467aa5893b90bc5f1e31_378ca9.jpg)

如下，构建 interceptor\_[demo2.py](http://demo2.py) 代码，该代码中嵌入多个工具拦截器，可以看到执行拦截器过程是洋葱式嵌套方式执行：

```python
"""
 多个工具拦截器执行顺序
"""
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

from init_llm import deepseek_llm


# ============ 定义一个日志拦截器 ============
async def outer(request, handler):
    print("外层: before")
    result = await handler(request)
    print("外层: after")
    return result

async def inner(request, handler):
    print("内层: before")
    result = await handler(request)
    print("内层: after")
    return result


async def main():
    # 创建 MCP 客户端，通过 tool_interceptors 参数传入拦截器
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            },
        },
        tool_interceptors=[outer, inner],   # 传入拦截器列表 , 执行顺序为 outer → inner
    )

    tools = await client.get_tools()
    print(f"已加载工具: {[t.name for t in tools]}\n")

    agent = create_agent(
        model=deepseek_llm,
        tools=tools
    )

    response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "请计算 3 加 5 的结果"}]
    })
    print(f"Agent 最终回复: {response['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())
```

运行Server端后，运行以上Client端，可以看到如下日志，多个工具拦截器执行是嵌套执行：

![image.png](./images/19MCP模型上下文协议_acbba208014e4414af58dc320d4db433_a6a83f.jpg)

### **9.4.2. 拦截器访问runtime**

当 MCP 工具在 create\_agent 中使用时，拦截器可以通过 request.runtime 访问四种运行时信息，这些信息来自 LangChain Agent 进程内部——MCP Server 本身是拿不到的。

| **属性**                 | **说明**                               |
| ------------------------------ | -------------------------------------------- |
| **runtime.context**      | 每次**ainvoke**调用时传入的上下文对象  |
| **runtime.state**        | Agent 的当前会话状态，含消息历史及自定义字段 |
| **runtime.store**        | LangChain 的长期持久化存储，跨会话共享       |
| **runtime.tool_call_id** | 当前工具调用的唯一ID                         |

**案例一：注入用户上下文（Context）**

场景： 客服系统需要记录"谁在执行操作"，MCP Server 不知道用户身份，通过拦截器在每次工具调用时自动将用户 ID 注入参数。

Server端（order\_[server.py](http://server.py)）：

```python
"""
订单服务 MCP Server
提供订单查询和退款工具，工具接受 caller_id 参数（由客户端拦截器自动注入）
"""
from fastmcp import FastMCP

mcp = FastMCP("OrderService")

ORDERS = {
    "ORD-001": {"product": "无线耳机", "status": "已签收", "amount": 299.0},
    "ORD-002": {"product": "机械键盘", "status": "待发货", "amount": 599.0},
    "ORD-003": {"product": "显示器", "status": "已完成", "amount": 1299.0},
}


@mcp.tool()
async def query_order(order_id: str, caller_id: str = "") -> str:
    """查询指定订单的详细信息。caller_id 由系统自动注入。"""
    order = ORDERS.get(order_id)
    if not order:
        return f"错误：未找到订单 {order_id}"
    return (
        f"订单 {order_id}：商品={order['product']}，"
        f"状态={order['status']}，金额={order['amount']}元"
        f"（操作人: {caller_id}）"
    )


@mcp.tool()
async def submit_refund(order_id: str, reason: str, caller_id: str = "") -> str:
    """提交退款申请。caller_id 由系统自动注入。"""
    order = ORDERS.get(order_id)
    if not order:
        return f"错误：未找到订单 {order_id}"
    if order["status"] == "已签收":
        return f"错误：订单 {order_id} 当前状态为'{order['status']}'，无法退款"
    return (
        f"退款申请已提交：{order_id}（{order['product']}），"
        f"原因：{reason}，退款金额：{order['amount']}元"
        f"（操作人: {caller_id}）"
    )


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )
```

Client端（inject\_context\_[demo.py](http://demo.py)）:

```python
"""
拦截器注入运行时上下文 —— 将用户身份自动传递给 MCP 工具
"""
import asyncio
from dataclasses import dataclass

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain.agents import create_agent

from init_llm import deepseek_llm


# ============ 定义上下文类型 ============
@dataclass
class CustomerContext:
    """每次 Agent 调用时传入的用户上下文信息"""
    user_id: str
    user_name: str
    api_key: str


# ============ 定义拦截器 ============
async def auth_inject_interceptor(request: MCPToolCallRequest, handler):
    """将上下文中的用户 ID 注入到每个 MCP 工具调用参数中"""
    runtime = request.runtime
    ctx: CustomerContext = runtime.context     # 读取运行时上下文

    # override() 修改请求参数和头信息，“**request.args” 表示保留原参数，添加 caller_id 参数
    modified_request = request.override(
        args={**request.args, "caller_id": ctx.user_id},
        headers={"Authorization": f"Bearer {ctx.api_key}"},
    )
    return await handler(modified_request)


async def main():
    client = MultiServerMCPClient(
        {
            "order": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            },
        },
        tool_interceptors=[auth_inject_interceptor],
    )

    tools = await client.get_tools()

    print(f"已加载工具: {[t.name for t in tools]}")

    # 创建 Agent，声明上下文类型
    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        context_schema=CustomerContext,
        system_prompt="你是电商客服助手。用户查询订单时调用 query_order，要求退款时调用 submit_refund，每次输出记得包含操作人。",
    )

    # 场景 1：张三查询订单
    print("=" * 60)
    r1 = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "帮我查一下订单 ORD-001"}]},
        context=CustomerContext(user_id="zhangsan", user_name="张三", api_key="sk-zhangsan"),
    )
    print(f"回复: {r1['messages'][-1].content}\n")

    # 场景 2：李四查询同一订单 —— 同一个工具，不同的用户身份
    print("=" * 60)
    r2 = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "ORD-002 给我退款"}]},
        context=CustomerContext(user_id="lisi", user_name="李四", api_key="sk-lisi"),
    )
    print(f"回复: {r2['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())

```

该案例中首先运行Server端，然后再运行Client端，可以看到如下输出：

![image.png](./images/19MCP模型上下文协议_b5fc3884247247c5be0457a718db6331_35b3ef.jpg)

以上代码注意如下几点：

* 两个场景使用同一组工具，但通过不同的 context 传入了不同的用户身份，MCP Server 完全不需要知道"认证"这件事——它只是在参数中接收 caller\_id。
* Client端headers“Authorization: Bearer sk-xxx”内容用于Nginx / API Gateway接收进行校验身份后转发给MCP Server，本案例中Server中没有任何中间件去读 header，这里把 headers 写进去是为了演示"拦截器可以改 header"这个能力，实际生效需要 Server 那边配合验证。

**案例二：读取State/Store中的用户偏好**

场景： 用户搜索商品时，希望 Agent 根据用户的偏好语言和地域自动调整搜索行为。这些偏好存在 LangChain Store 中（跨会话持久化），拦截器在工具调用前从 Store 读取并注入到请求参数。

Server端（search\_[server.py](http://server.py)）：

```python
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
            desc = texts.get(language, "zh")
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

```

Client端（read\_store\_[demo.py](http://demo.py)）

```python
"""
拦截器读取 Store —— 根据用户偏好自动调整 MCP 搜索参数
"""
import asyncio
from dataclasses import dataclass

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore

from init_llm import deepseek_llm


@dataclass
class UserContext:
    user_id: str


async def personalize_interceptor(request: MCPToolCallRequest, handler):
    """从 Store 读取用户偏好，注入到搜索请求参数中"""
    runtime = request.runtime
    store = runtime.store
    user_id = runtime.context.user_id

    # 从 Store 读取该用户的偏好设置
    prefs = store.get(("user_prefs",), user_id)

    if prefs and request.name == "search_product":
        modified_args = {
            **request.args,
            "language": prefs.value.get("language", "zh"),
            "region": prefs.value.get("region", "CN"),
            "limit": prefs.value.get("result_limit", 10),
        }
        print(f"  [拦截器] 为用户 {user_id} 应用偏好: {prefs.value}")
        return await handler(request.override(args=modified_args))

    return await handler(request)


async def main():
    # 创建 Store 并预填充用户偏好
    store = InMemoryStore()
    store.put(("user_prefs",), "u_001", {"language": "en", "region": "US", "result_limit": 2})
    store.put(("user_prefs",), "u_002", {"language": "zh", "region": "CN", "result_limit": 10})

    client = MultiServerMCPClient(
        {
            "search": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            },
        },
        tool_interceptors=[personalize_interceptor],
    )

    tools = await client.get_tools()

    # store 不仅传给 create_agent，也用于拦截器中的 runtime.store
    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        context_schema=UserContext,
        store=store,
        system_prompt="你是商品搜索助手，用户想搜什么就调用 search_product。",
    )

    print("=" * 60)
    print(f"美国用户 - Store 数据: language=en, region=US, limit=2")
    r1 = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "搜一下耳机"}]},
        context=UserContext(user_id="u_001"),
    )
    print(f"回复:{r1['messages'][-1].content}")

    print("=" * 60)
    print(f"中国用户 - Store 数据: language=zh, region=CN, limit=10")
    r2 = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "搜一下显示器"}]},
        context=UserContext(user_id="u_002"),
    )
    print(f"回复:{r2['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())

```

先运行Server然后运行client，可以看到如下结果， 同一个工具 search\_product，同一个关键词，但 u\_001（美国用户）返回英文描述和 US 定价，u\_002（中文用户）返回中文描述和人民币定价。

![image.png](./images/19MCP模型上下文协议_8619a1652d3c4f42b87c5e314fbc6989_d6909b.jpg)

### **9.4.3. 拦截器进行状态更新**

拦截器不仅可以读取状态，还可以写入状态和控制执行流，这通过返回 Command 对象实现。

Command 的核心用法：

| **用法**           | **语法**                              | **效果**                   |
| ------------------------ | ------------------------------------------- | -------------------------------- |
| **更新Agent 状态** | Command(update={"key": value})              | 往Agent 状态字典中写入自定义字段 |
| **提前终止**       | Command(update={...}, goto="__end__") | 立即结束Agent 执行               |
| **路由跳转**       | Command(update={...}, goto="node_name")     | 跳转到图中指定节点（需自定义图） |

注意：goto="node\_name" 需要图中存在对应节点，create\_agent 构建的标准图只有 model 和 tools 两个节点，所以非 **end** 的跳转仅在自定义图中有意义。日常最常用的是 update 更新状态和 goto="\_\_end\_\_" 提前终止。

**案例：售后客服 —— 退款后立即终止**

业务场景： AI 客服处理用户的退款请求，先查订单确认是否可退，可退则执行退款，退款成功后 Agent 应立即停止（用户只想要退款，不需要 AI 再问"还有什么可以帮您？"或做多余的说明）。同时，操作记录到 Agent State 中，方便后续使用。

Server端代码（order\_[server.py](http://server.py)）：

```python
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

```

Client端代码（command\_[demo.py](http://demo.py)）：

```python
"""
拦截器使用 Command 更新状态与流程控制
"""
import asyncio
import time

from langchain.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain.agents import create_agent, AgentState
from langgraph.types import Command

from init_llm import deepseek_llm


class CustomState(AgentState):
    last_op_time: str = "" # 最后操作时间


async def refund_control_interceptor(request: MCPToolCallRequest, handler):
    """
    拦截器的两个职责：
    1. 每次工具调用后，记录操作时间到 State
    2. 如果是退款操作，标记退款状态并立即终止 Agent
    """
    runtime = request.runtime

    # 执行工具调用
    result = await handler(request)
    text = result.content[0].text

    # 从 CallToolResult 提取文本，构造 LangChain 能识别的 ToolMessage
    tool_msg = ToolMessage(
        content=text,
        tool_call_id=runtime.tool_call_id
    )

    if request.name == "process_refund":
        # 退款操作: 写状态 + 立即终止
        return Command(
            update={
                "messages": [tool_msg],
                "last_op_time": time.strftime('%H:%M:%S'),
            },
            goto="__end__",   # 立即终止，AI 不再继续推理
        )

    # 普通查询: 只记录操作时间，继续正常流程
    return Command(
        update={
            "messages": [tool_msg],
            "last_op_time": time.strftime('%H:%M:%S'),
        },
    )


async def main():
    client = MultiServerMCPClient(
        {
            "my_order_service": {
                "transport": "http",
                "url": "http://localhost:8000/mcp"
            }
        },
        tool_interceptors=[refund_control_interceptor],
    )

    tools = await client.get_tools()

    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        state_schema=CustomState,
        system_prompt=(
            "你是电商售后客服。用户要求退款时："
            "1. 先调用 check_order 确认订单状态"
            "2. 如果订单已签收，调用 process_refund 执行退款"
            "3. 如果订单状态不允许退款，告知用户原因"
        ),
    )

    # ==========================================================
    # 场景 A：简单查询 —— 不触发终止
    # ==========================================================
    print("=" * 60)
    print("【场景 A】用户查询订单 —— 只记录操作时间，正常回复")
    r_a = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "帮我查一下 ORD-001 这个订单"}]},
    )
    print(f"回复: {r_a['messages'][-1].content}")
    print(f"State 中的操作时间: {r_a.get('last_op_time')}")

    # ==========================================================
    # 场景 B：退款成功 —— 触发终止
    # ==========================================================
    print("=" * 60)
    print("【场景 B】用户退款 —— 退款后立即终止")
    r_b = await agent.ainvoke(
        {"messages": [{
            "role": "user",
            "content": "ORD-001 的耳机有质量问题，帮我退货退款"
        }]}
    )
    print("r_b:", r_b)
    print(f"回复: {r_b['messages'][-1].content}")
    print(f"State 中的操作时间: {r_b.get('last_op_time')}")


if __name__ == "__main__":
    asyncio.run(main())

```

先运行Server然后运行Client，结果如下：

![image.png](./images/19MCP模型上下文协议_22f1fce507da458486e1f1be18c6477e_c9439a.jpg)

## 9.5. **MCP 核心特性**

### **9.5.1. 调用工具错误处理**

client.get\_tools() 从所有已配置的 Server 加载工具，默认情况下，当 MCP 工具执行失败时，langchain-mcp-adapters不抛出异常，而是将错误信息包装为 status="error" 的 ToolMessage 返回给模型，这样 Agent 能读到错误内容，自行判断是否需要重试。

工具调用报错返回的ToolMessage 示例如下：

```python
ToolMessage(content=[工具调用返回的错误信息], name='工具名称', id='ToolMessage唯一id', tool_call_id='工具调用请求id', status='error')
```

如下示例中，Agent调用MCP 工具出现错误时，自主决定是否重试：

* **error\_**[**server.py**](http://server.py)

```python
"""
MCP Server —— 演示工具报错重试与不重试

"""
import random

from fastmcp import FastMCP

mcp = FastMCP("我的MCP服务")

# 模拟数据库
USERS = {"u001": "张三", "u002": "李四", "u003": "王五"}


@mcp.tool()
def get_user(user_id: str) -> str:
    """根据用户ID查询用户信息"""
    if user_id not in USERS:
        raise ValueError(f"用户 {user_id} 不存在，请确认ID是否正确")
    return f"用户信息: ID={user_id}, 姓名={USERS[user_id]}"


# 临时性故障工具，模拟数据库查询失败，随机报错
@mcp.tool()
def search_database(keyword: str) -> str:
    """数据库查询工具
    """
    if random.random() < 0.3:
        return f"查询成功，找到与'{keyword}'相关的10条记录"
    else:
        raise RuntimeError("网络波动了，数据库连接超时，重试一下即可")

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8001
    )
```

* **retry\_**[**demo.py**](http://demo.py)**:**

```python
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

from init_llm import deepseek_llm

async def test_no_retry():

    client = MultiServerMCPClient({
        "remote_server": {
            "transport": "http",
            "url": "http://localhost:8001/mcp",
        },
    })

    tools = await client.get_tools()

    agent = create_agent(
        model=deepseek_llm,
        tools=tools
    )

    response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "帮我查一下用户 u999 的信息"}]
    })

    print("response:", response)
    print(f"Agent 回答: {response['messages'][-1].content}")


async def test_retry():

    client = MultiServerMCPClient( {
            "remote_server": {
                "transport": "http",
                "url": "http://localhost:8001/mcp",
            },
        })
    tools = await client.get_tools()

    agent = create_agent(
        model=deepseek_llm,
        tools=tools
    )

    response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "帮我查一下数据库中关于'空调'的信息"}]
    })

    print("response:", response)
    print(f"Agent 回答: {response['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(test_no_retry())
    asyncio.run(test_retry())

```

首先运行“error\_[server.py](http://server.py)”代码，然后再运行“retry\_[demo.py](http://demo.py)”代码，可以看到如下结果：

用户查询不到工具报错（不重试）情况：

![image.png](./images/19MCP模型上下文协议_5a3cb7c084ec4de7920026d2be10b12e_817cdd.jpg)

数据库连接超时工具报错（重试）情况：

![image.png](./images/19MCP模型上下文协议_a1545537c485467a8653f6656297dc9c_104720.jpg)

以上代码注意点如下：

1) 大多数情况对于永久性错误（缺少必填字段、权限不足）Agent不重试，对于临时性错误（连接超时、系统繁忙）Agent会进行重试，判断逻辑由LLM自主决定，也有可能对于临时性错误也不重试。
2) 如果想要在调用工具时直接抛出异常可以在MultiServerMCPClient中加入“handle\_tool\_errors=False”，当工具执行出现异常时，程序直接报错。

```python
... ...
client = MultiServerMCPClient(
    {
        "远程工具名称": {
            "transport": "http",
            "url": "http://localhost:8001/mcp",
        },
    },
    handle_tool_errors=False
)
... ...
```

### **9.5.2. Resource&Prompt**

MCP 协议定义了三种核心抽象，Tools（工具）、Resources（资源）、Prompts（提示模板）。Tools 是 MCP 中最核心、最常用的抽象，它允许 Server 将能力以"函数"的形式暴露给 Agent，Agent 在推理过程中根据需要自主决定是否调用，之前Agent集成MCP部分重点讲解了Tool，下面重点演示Mcp Resource 和Prompt的使用和案例。

#### **9.5.2.1. Resources（资源）**

Resource 是 MCP Server 向外暴露只读数据的机制，可以把它理解为"Server 端托管的数据文件"——每个 Resource 由一个唯一的 URI 标识，客户端通过该 URI 读取内容。与 Tools 最大的区别在于：Resources 不是给 LLM 调用的，而是给客户端（我们编写的代码）主动读取的，可以将 配置文件、公司政策文档、数据库 schema 说明、帮助文档、静态数据等内容设置在MCP Server端，供各个客户端使用。

在创建MCP Server时，可以通过“@mcp.resource(uri)”装饰器注册Resource，常见有如下两种写法。

**1) 静态资源（固定URI，固定内容）**

```python
@mcp.resource("config://tags", mime_type="application/json")
def get_tags() -> str:
    """获取关注列表标签"""
    return json.dumps(["科技", "金融", "新能源"])
```

注意：“URI:config://tags”客户端通过这个地址读取；mime\_type 是返回内容类型，客户端根据此类型决定如何渲染，`mimeType` 没有预定义的可选值列表，任意标准 MIME type 字符串均可，常见用法如 `text/plain`、`text/markdown`、`application/json`、`image/png`。

**2) 模版资源（URI中包含参数）**

```python
@mcp.resource("stock://{symbol}")
def stock_quote(symbol: str) -> str:
    """获取指定股票行情"""
    return json.dumps({"symbol": symbol, "price": 198.5})
```

注意：URI stock://{symbol} 中的 {symbol} 是占位符，函数参数 symbol: str 与之对应，客户端读取时传入实际值，可同时有多个参数：order://{user\_id}/{order\_id}/detail。

关于以上URI Schema内容（stock://、config://、file://、company://）是用户自定义的，MCP协议没有强制权限，scheme 的作用是命名空间隔离，方便客户端分类展示，但不是随便乱写——要符合 scheme://path 的 URI 格式规范。常见约定如下：

| **Schema**   | **含义** | **示例**                 |
| ------------------ | -------------- | ------------------------------ |
| **file://**  | 文件系统资源   | file:///etc/config.json        |
| **https://** | Web资源        | https://api.example.com/doc    |
| **自定义**   | 业务领域划分   | stock://、order://、company:// |

在LangChain中可以直接通过“client.get\_resources...”或者指定的Resource URI来使用Resource，示例如下：

```python
# 1. 从 Server 读取 Resource
blobs = await client.get_resources("server_name")

# 2. 也可以按 URI 筛选
blobs = await client.get_resources("server_name", uris=["stock://AAPL", "config://tags"])

# 3. 读取结果是 Blob 对象列表
for blob in blobs:
    text = blob.as_string()           # 文本内容
    uri = blob.metadata["uri"]        # 资源 URI
    mime = blob.mimetype              # MIME 类型

# 4. 最常见的做法：把内容注入 System Prompt
context = "\n".join(b.as_string() for b in blobs)
agent = create_agent(
model=llm, 
tools=tools, 
system_prompt=f"背景知识：\n{context}"
)
```

总结：Resource 不是给 Agent 自动用的，是给你的代码用的，你读完之后怎么用，完全由你决定。

#### **9.5.2.2. Prompts(提示词模版）**

Prompt 是 MCP Server 暴露的可复用提示模板，它预先定义了提示的结构和内容，客户端加载后可以直接作为消息发送给 LLM。适用于管理提示词模版（代码审查模板、翻译模板、Bug 报告模板、周报生成模板），这样可以在不同的客户端中使用。

为什么需要 Prompt，而不是直接写在代码里？如下三点原因：

1) 统一管理：所有客户端使用同一个提示模板，修改一处即可
2) 版本管理：提示模板可以在 Server 端更新，客户端不需要重新部署
3) 跨平台共享：同一个模板在 LangChain、Claude Desktop、VS Code 中都能用。

Mcp Server端Prompt的写法如下：

```python
# 无参数模板
@mcp.prompt
def analysis_framework() -> str:
    """标准分析框架"""
    return f"请按以下框架分析：\n1. 基本面\n2. 技术面\n3. 综合评级"

# 带参数模板
@mcp.prompt
def analysis_report(stock_name: str) -> str:
    """为指定股票生成分析报告模板"""
    return (
        f"请对 {stock_name} 进行投资分析，包括：\n"
        "1. 基本面分析（估值水平）\n"
        "2. 技术面分析（近期走势）\n"
        "3. 行业对比\n"
        "4. 综合评级（买入/持有/卖出），附理由"
    )
```

在LangChain构建的MCP Client中，按照如下方式使用MCP Server端的Prompt:

```python
# 加载 Prompt
msgs = await client.get_prompt("server_name", "analysis_report",
                                arguments={"stock_name": "特斯拉(TSLA)"})

# 返回结果是 LangChain Message 列表
prompt_text = msgs[0].content  # 取第一条消息的内容

# 用法一：注入 System Prompt（让 Agent 按模板格式输出）
agent = create_agent(model=llm, tools=tools,
                     system_prompt=f"请按以下格式输出：\n{prompt_text}")

# 用法二：作为用户消息的一部分
response = await agent.ainvoke({
    "messages": [
        {"role": "user", "content": f"分析特斯拉。请严格按以下格式：\n{prompt_text}"}
    ]
})
```

#### **9.5.2.3. 综合案例**

下面通过一个完整的案例，展示 Resources、Prompts、Tools 三者如何在同一个业务场景中各司其职。

需求场景： 构建一个金融股票分析助手，用户询问某只股票时，Agent 能基于公司标准的分析方法论进行分析，并按照固定模板输出报告。

* Resources 提供"背景知识"（方法论 + 热门板块行情），将client读取这些信息后注入 System Prompt，让 Agent 知道怎么分析。
* Prompts 提供"输出格式"（报告模板），client读取后也加载到System Prompt中作为格式要求，让 Agent 统一输出。
* Tools 提供"操作能力"（搜索、查价），Agent 自主调用

Server 端代码（stock\_[server.py](http://server.py)）：

```python
import json
from fastmcp import FastMCP
from mcp.server.fastmcp import Context

mcp = FastMCP("股票分析系统")

STOCK_DATA = {
    "AAPL": {"name": "苹果", "price": 198.5},
    "TSLA": {"name": "特斯拉", "price": 245.8},
    "000001": {"name": "平安银行", "price": 12.35},
}

# ===================== Tools =====================

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


# ===================== Resources =====================
# 作用：提供给 Agent 的背景知识，注入 System Prompt
@mcp.resource("research://methodology", mime_type="text/markdown",description="公司标准的股票分析方法论")
def get_methodology() -> str:
    """公司标准的股票分析方法论文档"""
    return """
        ## 股票分析框架
        1. **基本面分析**：查看公司营收、利润，判断估值是否合理
        2. **技术面分析**：查看近期价格走势和涨跌幅
        3. **行业对比**：与同行业竞争对手比较估值水平
        4. **综合评级**：给出买入/持有/卖出评级，附理由
        """


@mcp.resource("market://overview", mime_type="application/json",description="当前市场热门板块概况")
def get_market_overview() -> str:
    """当前市场热门板块数据"""
    return json.dumps([
        {"sector": "人工智能", "change": "+3.2%", "hot_stocks": ["NVDA", "AMD"]},
        {"sector": "新能源汽车", "change": "+1.8%", "hot_stocks": ["TSLA", "BYD"]},
        {"sector": "金融", "change": "+0.5%", "hot_stocks": ["000001", "601398"]},
    ], ensure_ascii=False)


# ===================== Prompts =====================
# 作用：Agent 输出报告时的格式模板
@mcp.prompt
def analysis_report(stock_name: str) -> str:
    """为指定股票生成分析报告模板"""
    return (
        f"请对 {stock_name} 进行投资分析，输出格式如下：\n"
        "---------------\n"
        f"【{stock_name} 投资分析报告】\n"
        "一、基本面分析\n"
        "二、技术面分析\n"
        "三、行业对比\n"
        "四、综合评级\n"
        "---------------\n"
    )


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )
```

Client端（socket\_agent\_[demo.py](http://demo.py)）：

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from init_llm import deepseek_llm


async def main():
    client = MultiServerMCPClient({
        "my_stock_server": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
        },
    })

    # ============================================================
    # 第 1 步：加载 Resources → 注入 System Prompt
    # Resources 提供"背景知识"，Agent 从 System Prompt 中直接获取
    # ============================================================
    blobs = await client.get_resources(
        "my_stock_server",
        uris=["research://methodology", "market://overview"]
    )

    context = ""
    for blob in blobs:
        print("blob:", blob)
        print("blob.metadata:", blob.metadata)
        print("blob.mimetype:", blob.mimetype)
        print("URI:", blob.metadata['uri'])
        print("内容：", blob.as_string())

        context += blob.as_string() + "\n"

    print("已加载资源：")
    for b in blobs:
        print(f"  {b.metadata['uri']} ({b.mimetype})")

    # ============================================================
    # 第 2 步：加载 Prompt → 作为输出格式要求
    # Prompt 提供"格式规范"，Agent 按模板输出分析报告
    # ============================================================
    msgs = await client.get_prompt("my_stock_server", "analysis_report",arguments={"stock_name": "目标股票"})
    print("msgs:", msgs)

    output_template = msgs[0].content

    print("\n已加载提示模板")

    # ============================================================
    # 第 3 步：加载 Tools → Agent 自主调用
    # ============================================================
    tools = await client.get_tools()
    print(f"已加载工具: {[t.name for t in tools]}")

    # ============================================================
    # 第 4 步：创建 Agent
    # Resources 和 Prompt 都被注入 System Prompt
    # ============================================================
    system_prompt = f"""你是一位专业的股票分析师。

                    请遵循以下分析方法论进行股票分析：
                    {context}
  
                    输出分析报告时，请严格按照以下格式：
                    {output_template}
                    """

    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        system_prompt=system_prompt
    )

    # ============================================================
    # 第 5 步：用户提问，Agent 自动使用 Tools 并按要求格式输出
    # ============================================================
    response = await agent.ainvoke({"messages": [{"role": "user","content": "帮我搜索特斯拉的股票代码，然后做一个详细分析"}]})

    print("response:", response)
    print("【分析结果】")
    print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
```

以上代码注意：

* Resources 使用方式：client.get\_resources("server\_name", uris=\[...\]) 按 URI 读取指定资源。[blob.as](http://blob.as)\_string() 获取文本内容，blob.metadata\["uri"\] 获取资源 URI。
* Prompts 使用方式：client.get\_prompt("server\_name", "prompt\_name", arguments={...}) 加载模板并传入参数。返回的 Message 列表通过 msgs\[0\].content 获取模板文本。同样可以注入 System Prompt，让 Agent 的输出统一格式。

### **9.5.3. 进度通知与日志**

#### **9.5.3.1. 进度通知**

MCP 协议允许 Server 在执行耗时工具时向客户端发送进度通知，客户端通过自定义的回调函数接收这些通知，用于渲染进度条、展示当前阶段等。

使用进度通知时，可以在MCP Server端定义工具函数中声明 ctx: Context 参数，用 [ctx.report](http://ctx.report)\_progress() 发布进度：

```python
from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP("ReportService")

@mcp.tool()
async def export_report(date: str, ctx: Context) -> str:
    """导出报表（模拟耗时操作）"""
    await ctx.report_progress(0, 100, "开始导出...")

    # 阶段一
    await asyncio.sleep(1)
    await ctx.report_progress(30, 100, "查询数据中")

    # 阶段二
    await asyncio.sleep(1)
    await ctx.report_progress(60, 100, "生成图表中")

    # 阶段三
    await asyncio.sleep(1)
    await ctx.report_progress(100, 100, "导出完成")

    return "报表已导出"
```

然后MCP Client端定义on\_progress回调函数，通过Callbacks传入MultiServerMCPClient：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext

async def on_progress(
    progress: float,          # 当前进度值
    total: float | None,      # 总进度值（可能为 None）
    message: str | None,      # 当前步骤描述
    context: CallbackContext,  # 上下文信息（server_name、tool_name）
):
    if total:
        print(f"进度: {progress}/{total} ({progress/total*100:.0f}%) - {message}")
    else:
        print(f"进度: {progress} - {message}")

client = MultiServerMCPClient(
    {...},
    callbacks=Callbacks(on_progress=on_progress),
)
```

使用进度通知时需要注意如下几点：

1) 在MCP Server端通过“[ctx.report](http://ctx.report)\_progress()”将信息发送到Client端，该方法是一个异步方法，必须“await [ctx.report](http://ctx.report)\_progress()”方式使用。
2) “report\_progress()”方法有固定的三个参数：progress(Server 传来的当前进度值)、total(Server 传来的总进度值)、message(Server 传来的步骤描述)。
3) MCPClient端通过“langchain-mcp-adapters” 通过 Callbacks.on\_progress 回调来接收这些通知。“on\_progress”方法中除了接收以上三个参数外，还可以插入一个context:CallbackContext类型，该类型包含 server\_name（MCP Server 名称）和 tool\_name（正在执行的工具名）

#### **9.5.3.2. 日志回调**

MCP 协议支持 Server 向客户端发送分级日志消息，这些日志不是 Server 自己的 stdout/stderr 打印，而是通过 MCP 协议传输给客户端的结构化消息。

使用日志回调时，可以在MCP Server端定义工具函数中声明 ctx: Context 参数，用 ctx.debug(...) / [ctx.info](http://ctx.info)(...)/ ctx.warning(...)/ ctx.error(...)发送不同级别的日志：

```python
@mcp.tool()
async def process_data(ctx: Context) -> str:
    await ctx.debug("开始读取配置...")      # 调试信息，默认不发送给客户端
    await ctx.info("开始处理数据")          # 一般信息
    await ctx.warning("数据源响应较慢")      # 警告
    await ctx.error("数据库连接失败")        # 错误
    return "处理完成"
```

client端通过 Callbacks.on_logging_message 回调接收，方便调试和监控服务器端行为:

```python
from mcp.types import LoggingMessageNotificationParams

async def on_logging_message(
    params: LoggingMessageNotificationParams,
    context: CallbackContext,
):
    print(f"[{context.server_name}] {params.level}: {params.data}")

client = MultiServerMCPClient(
    {...},
    callbacks=Callbacks(on_logging_message=on_logging_message),
)
```

以上代码注意：params.level是获取服务端日志级别，如 "info"、"warning"、"error"、"debug"；[params.data](http://params.data)是获取日志内容。

#### **9.5.3.3. 进度和日志使用案例**

案例场景： 运营人员需要从zip文件批量导入订单数据到系统，导入数据分三个阶段：解压文件 → 校验字段 → 写入数据库，每个阶段耗时不同，通过进度通知和日志让MCP Cleint端实时展示导入状态。

Server端代码（import\_[server.py](http://server.py)）：

```python
"""
批量导入 MCP Server —— 模拟数据导入的耗时操作，发送进度和日志通知
"""
import asyncio
from fastmcp import FastMCP, Context

mcp = FastMCP("数据导入服务")

# 导入流程分为 4 个阶段
IMPORT_STAGES = ["解压文件","校验字段", "写入数据库"]

@mcp.tool()
async def import_orders(filename: str, ctx: Context) -> str:
    """导入订单数据文件,导入过程较长，通过 progress 通知客户端实时进度。
    Args:
        filename: 订单数据文件名，例如 "orders_2026Q3.csv"
        ctx: MCP 上下文对象，用于发送进度和日志通知
    Returns:
        导入完成的统计信息，例如 "成功导入 10000 条记录，失败 23 条"
    """
    total = 100

    await ctx.info(f"开始导入文件: {filename}") # 发送日志通知到客户端，也会打印到服务端控制台
    await ctx.debug(f"开始导入文件: {filename}")
    await ctx.warning(f"开始导入文件: {filename}")
    await ctx.error(f"开始导入文件: {filename}")

    await ctx.report_progress(0, total, f"准备处理 {filename}")

    accumulated = 0

    for stage_name in IMPORT_STAGES:
        accumulated += 25 #共3个阶段，每个阶段25%进度
        await ctx.info(f"Server端正在执行阶段: {stage_name}")
        await asyncio.sleep(3) # 模拟阶段执行时间
        await ctx.report_progress(accumulated, total, f"正在执行阶段：{stage_name}") # 发送进度通知到客户端

    await ctx.report_progress(100, total, "导入完成")

    return "文件导入完成"


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )
```

Client端代码（import\_[demo.py](http://demo.py)）：

```python
"""
批量数据导入 —— 进度通知演示
"""
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext, LoggingMessageNotificationParams
from langchain.agents import create_agent

from init_llm import deepseek_llm


async def on_progress(
    progress: float,
    total: float | None,
    message: str | None,
    context: CallbackContext,
):
    """收到 Server 发来的进度通知时，打印进度条"""
    # print("progress:", progress)
    # print("total:", total)
    # print("message:", message)
    # print("context:", context)

    tool_info = f" ({context.tool_name})" if context.tool_name else ""

    percent = progress / total * 100

    print(f"【进度】：MCP 服务名称：{context.server_name}，调用工具：{tool_info} 进度: {percent}% - 消息：{message}")



async def on_logging_message(params: LoggingMessageNotificationParams, context):
    """处理 Server 端发来的日志"""
    print(f"【日志】：MCP服务名称：{context.server_name}  [日志级别：{params.level}]  [日志内容：{params.data}]")


async def main():
    client = MultiServerMCPClient(
        {
            "import_svc": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            },
        },
        callbacks=Callbacks(
            on_progress=on_progress,
            on_logging_message=on_logging_message
        ),
    )

    tools = await client.get_tools()
    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        system_prompt=(
            "你是数据管理助手。用户要进行数据导入时，调用 import_orders 工具。"
        ),
    )

    response = await agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": "帮我把 orders.zip 这个文件导入到系统里"
        }]
    })
    print(f"Agent 回复: {response['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())
```

先运行Server端，后运行Client端，可以看到MCP Client端输出进度和Server端日志：

![image.png](./images/19MCP模型上下文协议_497f5b72b101422f9c68bcc24f325ca8_bd0272.jpg)

以上代码注意：

1) MCP Server端定义工具中“[ctx.info](http://ctx.info)”...和“[ctx.report](http://ctx.report)\_progress”必须加上await，因为这些方法底层实现是异步的。
2) MCP Client端 Callbacks 指定的两个方法“on\_progress”和“on\_logging\_message”也需要指定为异步方法，底层调用这些方法时也是异步调用，否则报错。

### **9.5.4. 交互式信息收集（Elicitation）**

Elicitation 是 MCP 协议 2025-11-25 版本引入的能力——允许 MCP 服务器在工具执行过程中，主动向用户请求额外信息。传统工具调用是单向的：Agent 给参数，服务器返回结果。如果服务器发现自己缺少某些信息，只能返回错误、让 Agent 重新调用——来回好几轮。

Elicitation 把这个问题从"多轮对话"变成了"单次调用内的交互"。服务器可以通过 ctx.elicit() 向客户端发出一个带 Schema 的请求，客户端（或用户）响应后，工具继续执行。

**Elicitation用法如下：**

Server端创建的工具逻辑中通过ctx.elicit()向Client端发送询问：

```python
from fastmcp import FastMCP, Context

mcp = FastMCP("Demo")

@mcp.tool()
async def create_profile(name: str, ctx: Context) -> str:
    result = await ctx.elicit(
        message=f"请填写 {name} 的以下信息：",
        response_type=UserDetails,   # Pydantic 模型，定义需要哪些字段
    )
    if result.action == "accept" and result.data:
        return f"已创建 {name} 的档案"
    if result.action == "decline":
        return f"已创建最简档案（用户拒绝提供信息）"
    return "操作已取消"
```

Client端通过在Callbacks中指定on\_elicitation回调处理询问：

```python
from mcp.types import ElicitRequestParams, ElicitResult

async def on_elicitation(mcp_context, params, context) -> ElicitResult:
    # 真实场景：弹窗让用户填写，返回用户输入
    return ElicitResult(action="accept", content={"email": "...", "age": 25})

client = MultiServerMCPClient({...}, callbacks=Callbacks(on_elicitation=on_elicitation))
```

Server端ctx.elicit(参数...) 常见参数说明如下：

| **参数**          | **类型**                | **说明**                                                 |
| ----------------------- | ----------------------------- | -------------------------------------------------------------- |
| **message**       | str                           | 向用户展示的提示消息，告诉用户需要提供什么                     |
| **response_type** | BaseModel / list[str]/str/int | 定义期望的响应格式,list[str]用于单选、BaseModel 用于多字段表单 |

Client端回调函数中必须返回ElicitResult对象，该对象中包含两个字段：action（用户相应给Server端的动作）、content（提交给Server的数据）。

action可以填写的值如下：

| **值**          | **含义** | **Server端收到的结果**                    |
| --------------------- | -------------- | ----------------------------------------------- |
| **“accept”**  | 用户提交了数据 | result.action == "accept"，result.data 有值     |
| **“decline”** | 用户拒绝       | result.action == "decline"，result.data 为 None |
| **“cancel”**  | 用户取消       | result.action == "cancel"                       |

只有当action=“accept”时，content才需要返回用户填写的内容，内容格式取决于Server端response\_type的类型：

| **Server端response_type** | **content的格式**       | **示例**                  |
| ------------------------------- | ----------------------------- | ------------------------------- |
| **list[str]单选列表**     | {"value": "选中的字符串"}     | {"value": "覆盖已有文件"}       |
| **BaseModel 多字段表单**  | {"字段1": 值1, "字段2": 值2}  | {"email": "a@b.com", "age": 25} |
| **str 单值**              | {"value": "用户输入的字符串"} | {"value": "同意"}               |
| **int 单值**              | {"value": 42}                 | {"value": 42}                   |

注意： 不管 response\_type 是什么，FastMCP 都帮你包装，Server 端工具里直接 [result.data](http://result.data) 拿到解包后的值，在 on\_elicitation 回调里构造 ElicitResult 时，必须按对应格式塞 content。

案例：文件导入冲突确认，导入文件时检测到同名文件，通过 Elicitation 在控制台让用户选择"覆盖"还是"跳过"。

Server端代码（import\_[server.py](http://server.py)）:

```python
"""
文件导入 MCP Server —— Elicitation 交互式冲突确认
"""
from fastmcp import FastMCP, Context

mcp = FastMCP("文件导入服务")

EXISTING_FILES = ["orders.zip"]

@mcp.tool()
async def list_files() -> str:
    """列出所有已导入的文件"""
    return f"已导入文件: {EXISTING_FILES}"

@mcp.tool()
async def import_file(filename: str, ctx: Context) -> str:
    """导入数据文件。遇到同名文件时通过 Elicitation 请求用户确认。"""

    # 检测到同名文件，询问用户如何处理
    if filename in EXISTING_FILES:

        result = await ctx.elicit(
            message=f"文件 {filename} 已经存在，请选择处理方式：",
            response_type=["覆盖已有文件", "跳过该文件", "取消导入"],
        )

        if result.action == "cancel":
            return "导入已取消"

        if result.action == "decline":
            return f"文件 {filename} 已跳过（用户未做选择）"

        # accept：拿到了用户选择
        choice = result.data
        print(f"用户选择: {choice}")

        if choice == "覆盖已有文件":
            return f"文件 {filename} 导入成功"
        elif choice == "跳过该文件":
            return f"文件 {filename} 已跳过"
        elif choice == "取消导入":
            return "导入已取消"

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )

```

Client端代码（elicitation\_[demo.py](http://demo.py)）:

```python
"""
Elicitation 交互式信息收集 —— 控制台真实输入
"""
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext
from langchain.agents import create_agent
from mcp.shared.context import RequestContext
from mcp.types import ElicitRequestParams, ElicitResult

from init_llm import deepseek_llm


async def on_elicitation(
    mcp_context: RequestContext,
    params: ElicitRequestParams,
    context: CallbackContext,
) -> ElicitResult:
    """处理 Server 发来的询问 —— 用户在控制台中输入选择"""
    print(f"{'=' * 50}")
    print("mcp_context:", mcp_context)
    print("params:", params)
    print("context:", context)

    print(f"  [系统询问] {params.message}")

    # 从 Schema 中提取用户选择的选项列表
    schema = params.requestedSchema
    options = schema["properties"]["value"]["enum"]

    if options:
        # 打印选项列表
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")

        # 让用户输入选项编号，输入无效则反复提示
        while True:
            choice = input(f"  请输入选项编号 (1-{len(options)}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    selected = options[idx]
                    break
            except ValueError:
                pass
            print(f"  输入无效，请输入 1 到 {len(options)} 之间的数字")

        print(f"  你选择了: {selected}")
    else:
        # 没有枚举选项时，自由输入
        selected = input(f"  请输入: ").strip()

    print(f"{'=' * 50}")

    # 这里的action可以是
    # accept：用户选择了选项
    # cancel：用户取消了询问
    # decline：用户拒绝了询问
    return ElicitResult(
        action="accept",
        content={"value": selected}
    )


async def main():
    client = MultiServerMCPClient(
        {
            "import_svc": {
                "transport": "http",
                "url": "http://localhost:8000/mcp"
            }
        },
        callbacks=Callbacks(
            on_elicitation=on_elicitation
        ),
    )

    tools = await client.get_tools()
    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        system_prompt="你是数据管理助手。用户要导入文件时调用 import_file 工具。文件名从用户消息中提取。",
    )

    print("开始导入文件...")
    response1 = await agent.ainvoke({
        "messages": [{"role": "user", "content": "帮我把 orders.zip 文件导入到系统里"}]
    })
    print(f"Agent 回复: {response1['messages'][-1].content}")

    print("开始列出已导入文件...")
    response2 = await agent.ainvoke({
        "messages": [{"role": "user", "content": "帮我列出所有已导入的文件"}]
    })
    print(f"Agent 回复: {response2['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())
```

运行代码时，先运行Server，然后运行Client端，运行后根据用户输入的数字返回对应内容。

![image.png](./images/19MCP模型上下文协议_4f512297ffe942b78990605de4b8d796_3368d2.jpg)

以上代码关于定义的“on\_elicitation”方法的参数解释如下：

1) “mcp\_context: RequestContext”:MCP SDK原始请求上下文，这是 MCP 协议层的底层对象，绝大多数情况下用不到它。 它包含当前 MCP 连接的底层信息（session、request\_id 等），仅在需要直接操作 MCP session 时才用到，比如发送额外的协议消息。
2) “params: ElicitRequestParams”：Server端发来的询问内容，包含 Server 端 ctx.elicit() 发来的所有信息。
3) “context: CallbackContext”:LangChain 适配器的回调上下文，包含 server\_name（MCP Server 名称）和 tool\_name（正在执行的工具名）。

## 9.6. **综合案例-电商智能售后客服系统**

本案例构建了一个电商平台智能售后客服系统。用户通过自然语言对话即可完成订单查询、退款申请、批量退款等操作。系统根据退款金额自动分级处理：退款经由HITL人工介入确认处理，如果退款金额大于500，进行二次人工确认。整个案例涵盖了 MCP 多服务聚合、本地与远程工具混用、工具拦截器、Resource 与 Prompt、进度通知与日志、Elicitation 交互确认、HITL 人工审批等核心知识点。

涉及到的工具及组件如下:

| **组件**                      | **来源**       | **说明**                 |
| ----------------------------------- | -------------------- | ------------------------------ |
| **query_order**               | MCP Server(订单服务) | 查询订单详情，不存在时抛异常   |
| **process_refund**            | MCP Server(订单服务) | 单笔退款，含Elicitation + HITL |
| **batch_refund**              | MCP Server(订单服务) | 批量退款，含进度通知+ 日志     |
| **send_sms**                  | MCP Server(通知服务) | 发送短信通知                   |
| **validate_phone**            | 本地工具             | 校验手机号格式                 |
| **company://policies/return** | MCP Resource         | 公司退换货政策文档             |
| **refund_response**           | MCP Prompt           | 退款回复模板                   |
| **auth_inject**               | 拦截器               | 将用户身份注入MCP 工具参数     |
| **audit_log**                 | 拦截器               | 记录每次工具调用的审计日志     |
| **HumanInTheLoopMiddleware**  | 中间件               | 退款操作人工审批               |
| **on_progress**               | 回调                 | 接收批量退款的进度通知         |
| **on_logging**                | 回调                 | 接收Server 端的日志消息        |
| **on_elicitation**            | 回调                 | 处理中额退款的确认交互         |

整体交互流程如下：

1) 控制台输入自然语言指令。
2) Agent 调用 query\_order（经拦截器链 auth\_inject → audit\_log）查询订单 → 订单不存在时返回永久性错误，LLM 不重试。
3) Agent 调用 process\_refund 退款 → HITL 中间件先拦截（approve/reject）→ 放行后走拦截器链 → 金额 >= 500 元时 ctx.elicit() 二次确认。
4) Agent 调用 batch\_refund 批量退款（不经 HITL，不经 Elicitation）→ [ctx.report](http://ctx.report)\_progress + ctx.info/warning 实时推送进度和日志。
5) 退款成功后 Agent 询问是否发短信 → 先调 validate\_phone（本地工具，不经拦截器）校验 → 再调 send\_sms（经拦截器链）发送。
6) Agent 输出回复及审计日志，等待下一轮输入，输入 quit/exit/退出 结束。

![image.png](./images/19MCP模型上下文协议_2aafda33e124491d90057fc5e0bf2e34_b52026.jpg)

order\_[server.py](http://server.py)代码：

```python
"""
订单服务 MCP Server
提供订单查询、单笔退款、批量退款三个工具
批量退款带有进度通知和日志
"""
import asyncio
from fastmcp import FastMCP, Context

mcp = FastMCP("订单服务")

ORDERS = {
    "ORD-001": {"product": "无线耳机", "status": "已签收", "amount": 299.0},
    "ORD-002": {"product": "机械键盘", "status": "已签收", "amount": 500.0},
    "ORD-003": {"product": "4K显示器", "status": "已签收", "amount": 2499.0},
    "ORD-004": {"product": "鼠标垫", "status": "配送中", "amount": 29.0},
}


@mcp.tool()
async def query_order(order_id: str, caller_id: str = "") -> str:
    """
        查询指定订单的详细信息。caller_id 由系统自动注入。
        如果订单不存在，会抛出 ValueError 异常。
    Args:
        order_id: 订单号
        caller_id: 操作人ID，默认为空字符串
    Returns:
        订单详细信息字符串
    """
    order = ORDERS.get(order_id)
    if not order:
        raise ValueError(f"订单 {order_id} 不存在，请确认订单号是否正确")
    return (
        f"订单 {order_id}：商品={order['product']}，"
        f"状态={order['status']}，金额={order['amount']}元"
        f"（操作人: {caller_id}）"
    )


@mcp.tool()
async def process_refund(order_id: str, reason: str,
                         ctx: Context, caller_id: str = "") -> str:
    """
        对指定订单发起退款。退款金额记录在订单中。
        金额500~2000元时会弹出确认框让用户二次确认。
        如果订单不存在，会抛出 ValueError 异常。
        Args:
            order_id: 订单号
            reason: 退款原因
            ctx: MCP 上下文对象
            caller_id: 操作人ID，默认为空字符串
        Returns:
            退款结果字符串
    """
    order = ORDERS.get(order_id)
    if not order:
        raise ValueError(f"订单 {order_id} 不存在")
    if order["status"] != "已签收":
        raise ValueError(f"订单状态为'{order['status']}'，不可退款")

    amount = order["amount"]

    # 中额退款（500~2000元）：通过 Elicitation 让用户二次确认
    if 500 <= amount :
        result = await ctx.elicit(
            message=(
                f"订单 {order_id}（{order['product']}）退款金额 {amount} 元，"
                f"退款原因：{reason}。请确认是否继续退款？"
            ),
            response_type=["确认退款", "取消退款"],
        )
        if result.action == "cancel":
            return "退款已取消"
        if result.action == "decline":
            return f"退款已取消：用户未确认订单 {order_id} 的退款操作"
        if result.data == "取消退款":
            return f"退款已取消：用户取消了订单 {order_id} 的退款操作"
        await ctx.info(f"用户已确认退款: {order_id}")

    ORDERS[order_id]["status"] = "已退款"
    return (
        f"退款成功：{order_id}（{order['product']}），"
        f"金额={amount}元，原因={reason}"
        f"（操作人: {caller_id}）"
    )


@mcp.tool()
async def batch_refund(order_ids: str, reason: str,
                       ctx: Context, caller_id: str = "") -> str:
    """批量退款，order_ids 用逗号分隔。处理过程通过进度通知推送。
       Args:
            order_ids: 订单号列表，逗号分隔
            reason: 退款原因
            ctx: MCP 上下文对象
            caller_id: 操作人ID，默认为空字符串
        Returns:
            批量退款结果字符串
    """
    ids = [i.strip() for i in order_ids.split(",") if i.strip()]
    total = len(ids)
    await ctx.info(f"开始批量退款，共 {total} 笔")

    success = 0
    for i, oid in enumerate(ids):
        await asyncio.sleep(0.5)  # 模拟每笔退款的处理耗时
        order = ORDERS.get(oid)
        if order and order["status"] == "已签收" and order["amount"] <= 500:
            ORDERS[oid]["status"] = "已退款"
            success += 1
            await ctx.info(f"  {oid} 退款成功")
        else:
            await ctx.warning(f"  {oid} 退款跳过（状态不允许或金额超过500元）")

        await ctx.report_progress(
            progress=i + 1, total=total,
            message=f"已处理 {i + 1}/{total}"
        )

    await ctx.info(f"批量退款完成: {success}/{total} 成功")
    return f"批量退款完成：{success}/{total} 笔成功（操作人: {caller_id}）"


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8030
    )

```

notify\_[server.py](http://server.py)代码：

```python
"""通知服务 MCP Server —— 发送短信通知"""
from fastmcp import FastMCP

mcp = FastMCP("通知服务")


@mcp.tool()
async def send_sms(phone: str, content: str, caller_id: str = "") -> str:
    """
    向指定手机号发送短信通知。caller_id 由系统自动注入。
    Args:
        phone: 手机号
        content: 短信内容
        caller_id: 操作人ID，默认为空字符串
    Returns:
        短信发送结果字符串
    """
    # 实际项目中调用短信网关 API
    return (
        f"短信已发送：号码={phone}，内容='{content}'"
        f"（操作人: {caller_id}）"
    )


# ========== Resource：短信模板说明 ==========
@mcp.resource("company://policies/return",mime_type="text/markdown",description="公司退换货政策")
def get_return_policy() -> str:
    """退换货政策文档"""
    return """
            ## 退换货政策
            1. 签收后 7 天内可无理由退货（商品不影响二次销售）
            2. 质量问题 30 天内可换货，运费商家承担
            3. 退货时赠品需一并退回
            4. 退款将在收货确认后 3 个工作日内退回原支付方式
            """


# ========== Prompt：退款回复模板 ==========
@mcp.prompt
def refund_response(order_id: str, amount: str) -> str:
    """退款回复模板"""
    return (
        f"好的，已为您处理订单 {order_id} 的退款。\n"
        f"退款金额：{amount} 元\n"
        f"预计 3 个工作日内退回原支付方式。\n"
        f"如有疑问可随时联系我们。"
    )


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8031
    )

```

after\_sale\_agent\_[stream.py](http://stream.py)代码：

```python
"""
电商智能售后系统 —— MCP 综合案例（交互式对话）

"""
import asyncio
import operator
import time
from dataclasses import dataclass
from typing import Annotated

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.messages import ToolMessage
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from mcp.types import ElicitRequestParams, ElicitResult, LoggingMessageNotificationParams
from mcp.shared.context import RequestContext

from init_llm import deepseek_llm


# ==================== 1. 上下文定义 ====================
@dataclass
class CustomerContext:
    user_id: str
    user_name: str


class CustomState(AgentState):
    audit_log: Annotated[list[str], operator.add]


# ==================== 2. 本地工具 ====================
@tool
def validate_phone(phone: str) -> str:
    """校验手机号格式（中国大陆 11 位手机号）"""
    if len(phone) == 11 and phone.isdigit() and phone.startswith("1"):
        return f"手机号 {phone} 格式正确"
    return f"手机号 {phone} 格式错误，应为 11 位数字且以 1 开头"


# ==================== 3. 工具拦截器：认证注入 ====================
async def auth_inject(request: MCPToolCallRequest, handler):
    """将用户身份注入 MCP 工具参数"""
    ctx: CustomerContext = request.runtime.context
    return await handler(
        request.override(
            args={**request.args, "caller_id": f"{ctx.user_id}({ctx.user_name})"},
        )
    )


# ==================== 4. 工具拦截器：审计日志 ====================
async def audit_log(request: MCPToolCallRequest, handler):
    """每次 MCP 工具调用后记录审计日志到 Agent State"""
    runtime = request.runtime
    result = await handler(request)

    # 从结果中提取文本内容
    text = result.content[0].text if result.content else ""

    tool_msg = ToolMessage(
        content=text,
        tool_call_id=runtime.tool_call_id
    )

    # request.name 是工具名称，request.args 是工具参数，这里记录调用日志
    log_entry = (
        f"[{time.strftime('%H:%M:%S')}] {runtime.context.user_name} "
        f"-> {request.name}: {str(request.args)}"
    )

    return Command(
        update={
            "messages": [tool_msg],
            "audit_log": [log_entry],
        }
    )


# ==================== 5. 进度回调 ====================
async def on_progress(progress, total, message, context: CallbackContext):
    if total:
        pct = progress / total * 100
        print(f"  [进度] {progress}/{total} ({pct:.0f}%) - {message or ''}")


# ==================== 6. 日志回调，输出在Client端 ====================
async def on_logging(params: LoggingMessageNotificationParams, context):
    # 这里是Server端传递过来的日志，直接输出
    msg = params.data.get("msg")
    print(f"  [{context.server_name}] [{params.level}] {msg}")


# ==================== 7. Elicitation 回调 ====================
async def on_elicitation(
    mcp_context: RequestContext,
    params: ElicitRequestParams,
    context: CallbackContext,
) -> ElicitResult:
    """大额退款时，让用户在控制台确认"""
    print(f"{'=' * 50}")
    print(f"  [系统询问] {params.message}")

    # 从 Schema 中提取用户选择的选项列表
    schema = params.requestedSchema
    options = schema["properties"]["value"]["enum"]

    if options:
        # 打印选项列表
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")

        # 让用户输入选项编号，输入无效则反复提示
        while True:
            choice = input(f"  请输入选项编号 (1-{len(options)}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    selected = options[idx]
                    break
            except ValueError:
                pass
            print(f"  输入无效，请输入 1 到 {len(options)} 之间的数字")

        print(f"  你选择了: {selected}")
    else:
        # 没有枚举选项时，自由输入
        selected = input(f"  请输入: ").strip()

    print(f"{'=' * 50}")

    return ElicitResult(action="accept", content={"value": selected})


# ==================== 8. HITL 中断处理 ====================
async def handle_interrupts(result, agent, config, context):
    """处理一轮或多轮中断，直到 Agent 不再触发中断为止"""
    while result.interrupts:
        interrupt_data = result.interrupts[0].value
        action_requests = interrupt_data["action_requests"]
        review_configs = interrupt_data["review_configs"]

        print(f"\n{'─' * 60}")
        print(f" Agent 中断 —— {len(action_requests)} 个操作需要人工介入")
        print(f"{'─' * 60}")

        for i, req in enumerate(action_requests):
            cfg = review_configs[i]
            print(f"\n  [{i}] 工具名称 : {req['name']}")
            print(f"      参数     : {req['args']}")
            print(f"      允许决策 : {cfg['allowed_decisions']}")

        decisions = []

        print(f"\n{'·' * 40}")
        print("请按顺序对以上操作做出决策：")
        print(f"{'·' * 40}")

        for i, req in enumerate(action_requests):
            allowed = review_configs[i]["allowed_decisions"]

            print(f"\n 操作 [{i}] {req['name']}")
            if req.get("args"):
                for k, v in req["args"].items():
                    print(f"     参数: {k} = {v}")

            hint_map = {
                "approve": "批准，按原参数执行工具",
                "edit":    "修改参数后执行工具",
                "reject":  "拒绝执行，附带反馈说明",
                "respond": "跳过工具执行，直接返回人工回复",
            }
            print("     可选操作：")
            for a in allowed:
                print(f"       > {a} — {hint_map.get(a)}")

            while True:
                decision = input(f"      >>> 输入操作 ({'/'.join(allowed)}): ").strip().lower()
                if decision in allowed:
                    break
                print(f"      无效输入，该操作只允许: {allowed}")

            if decision == "approve":
                decisions.append({"type": "approve"})
                print(f"      已批准 —— 工具将按原参数执行")

            elif decision == "edit":
                print(f"      请输入修改后的参数（直接回车保留原值）：")
                new_args = {}
                for k, v in req["args"].items():
                    new_val = input(f"         {k} [原值: {str(v)}]: ").strip()
                    if new_val == "":
                        new_args[k] = v
                    else:
                        new_args[k] = new_val
                decisions.append({
                    "type": "edit",
                    "edited_action": {"name": req["name"], "args": new_args},
                })
                print(f"      已修改参数: {new_args}")

            elif decision == "reject":
                reason = input(f"      请输入拒绝原因: ").strip()
                if not reason:
                    reason = "操作被人工拒绝"
                decisions.append({"type": "reject", "message": reason})
                print(f"      已拒绝: {reason}")

            elif decision == "respond":
                reply = input(f"      请输入回复内容: ").strip()
                if not reply:
                    reply = "已确认，没有补充信息。"
                decisions.append({"type": "respond", "message": reply})
                print(f"      已回复: {reply}")

        print(f"\n{'─' * 60}")
        print(f"提交决策列表: {decisions}")
        print(f"{'─' * 60}")

        result = await agent.ainvoke(
            Command(resume={"decisions": decisions}),
            config=config,
            context=context,
            version="v2",
        )

    return result


# ==================== 9. 主流程 ====================
async def main():
    # 1. 创建 MCP 客户端（连接两个 Server）
    client = MultiServerMCPClient(
        {
            "order": {"transport": "http", "url": "http://localhost:8030/mcp"},
            "notify": {"transport": "http", "url": "http://localhost:8031/mcp"},
        },
        tool_interceptors=[auth_inject, audit_log],
        callbacks=Callbacks(
            on_progress=on_progress,
            on_logging_message=on_logging,
            on_elicitation=on_elicitation,
        ),
    )


    mcp_tools = await client.get_tools()

    # 2. 加载 Resource 和 Prompt
    blobs = await client.get_resources("notify", uris=["company://policies/return"])
    policy_text = "\n".join(b.as_string() for b in blobs)

    msgs = await client.get_prompt("notify", "refund_response",
                                    arguments={"order_id": "{订单号}", "amount": "{金额}"})
    prompt_template = msgs[0].content if msgs else ""

    # 3. 合并 MCP 工具 + 本地工具
    all_tools = mcp_tools + [validate_phone]

    # 4. 创建 Agent（HITL + 状态持久化）
    checkpointer = MemorySaver()
    agent = create_agent(
        model=deepseek_llm,
        tools=all_tools,
        context_schema=CustomerContext,
        state_schema=CustomState,
        checkpointer=checkpointer,
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "process_refund": {
                        "allowed_decisions": ["approve", "reject"],
                        "description": "退款操作需要人工审批，请确认是否执行退款",
                    },
                },
            ),
        ],
        system_prompt=f"""你是电商售后客服助手。
            工作流程：
            1. 查询订单时调用 query_order。如果订单不存在，直接告知用户不要重试。
            2. 退款时先查询订单确认状态和金额。
            3. 退款成功后询问用户是否需要短信通知。如果要通知，先调用 validate_phone 校验手机号，再用 send_sms 发送。
            4. 涉及退换货政策问题时，参考以下政策：
            {policy_text}
            5. 回复退款结果时，参考以下模板：
            {prompt_template}
            """
    )

    ctx = CustomerContext(user_id="user_zhangsan", user_name="张三")

    config = {"configurable": {"thread_id": "session_001"}}

    print("=" * 60)
    print("  电商智能售后系统")
    print("  输入 'quit' / 'exit' / '退出' 结束对话")
    print("=" * 60)

    while True:
        try:
            user_input = input("[你]: ").strip()

            if user_input.lower() in ("quit", "exit", "退出", "q"):
                print("已退出，再见！")
                break

            if not user_input:
                continue

            result = await agent.ainvoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
                context=ctx,
                version="v2",
            )

            # 处理中断（可能多轮）
            result = await handle_interrupts(result, agent, config, ctx)

            # 输出最终回复
            final_msg = result.value["messages"][-1]
            print(f"[助手]: {final_msg.content}")

            # 输出审计日志
            audit = result.value.get("audit_log", [])
            if audit:
                print(f"审计日志:")
                for entry in audit:
                    print(f"  {entry}")

        except Exception as e:
            print(f"调用出错: {e}")


if __name__ == "__main__":
    asyncio.run(main())

```

首先运行两个Server，然后再运行Client，进行如下实时对话：

```python
查询订单ORD-001

# 如下提问触发HITL且按照退款模版进行回复
该订单耳机质量有问题，请帮我退款需要

发送短信，内容：ORD-001 已经退款，手机号：18812345678

# 如下提问触发HITL，通过HITL后还需要二次人工确认
ORD-003 显示器屏幕坏了，需要退款

#如下提问会有退款进度
ORD-002、ORD-004 由于产品质量问题，请退款
```

以上对话过程中可以看到Client端每次对话都有审计日志输出，且Server端对应的日志也会输出到Client端。
