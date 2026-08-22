# Python网络编程与并发编程 终极精炼笔记（AI/大模型面试工程版）

## 一、计算机网络核心基础

### 1\. 网络通信三要素

**IP地址**：定位网络中唯一一台设备。

**端口号**：定位设备中唯一运行的程序，范围 0\~65535，1024以下为系统保留端口。

**通信协议**：设备之间的数据传输规则，核心分为 UDP、TCP 两大协议。

### 2\. UDP 协议

**核心特性**：无连接、不可靠、传输速度快、支持一对一/一对多通信。

**工作机制**：无需提前建立连接，直接发送数据包，无确认、无重传机制，可能丢包、乱序。

**适用场景**：对实时性要求高、允许少量数据丢失的场景，如直播、语音通话、视频传输。

**工程说明**：大模型、大数据、AI 业务几乎不用 UDP，仅需掌握概念区别、看懂基础代码即可，无需深耕复杂项目。

#### UDP 最简实战代码（无连接通信 Demo）

UDP 核心：无需 connect 建立连接，直接收发数据包，天然支持一对一、一对多。

##### UDP 服务端

```python
import socket

# SOCK_DGRAM 代表UDP协议
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("127.0.0.1", 9999))
print("UDP服务端启动成功")

# 接收数据 + 获取客户端地址 (阻塞)
data, addr = server.recvfrom(1024)
print(f"收到{addr}消息：{data.decode('utf-8')}")

# 回复客户端
server.sendto("UDP收到！".encode("utf-8"), addr)
server.close()

```

##### UDP 客户端

```python
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 直接发数据，无需连接
client.sendto("Hello UDP".encode("utf-8"), ("127.0.0.1", 9999))

# 接收服务端响应
data, addr = client.recvfrom(1024)
print("服务端响应：", data.decode("utf-8"))
client.close()

```

### 3\. TCP 协议

**核心特性**：面向连接、可靠传输、速度稍慢、有序传输、无数据丢失。

**核心机制**：三次握手建立连接、四次挥手断开连接、超时重传、应答确认、流量控制。

**衍生考点：粘包现象**

**超级重点：TCP三次握手、四次挥手、粘包完整原理（面试必考完整版）**

#### 1\. TCP 三次握手（建立连接）

**核心目的**：双向确认「发送能力、接收能力」都正常，建立可靠连接。

**完整流程**：

- **第一次握手（客户端→服务端 SYN）**：客户端发送同步报文，请求建立连接。服务端收到，确认：**客户端发数据正常、服务端收数据正常**。

- **第二次握手（服务端→客户端 SYN\+ACK）**：服务端回复同步\+确认报文。客户端收到，确认：**服务端发数据正常、客户端收数据正常**。

- **第三次握手（客户端→服务端 ACK）**：客户端最后确认回复，连接正式建立。

**面试必背一句话**：三次握手是为了**双向校验收发能力**，确保双方都能收能发，保证连接可靠性。

**为什么不能两次握手？** 两次只能证明客户端能发、服务端能收，无法验证「服务端发送、客户端接收」的链路，会造成无效连接占用服务端资源。

#### 2\. TCP 四次挥手（断开连接）

**核心目的**：TCP连接是**全双工**，收发通道独立，必须分别关闭读写通道。

**完整流程**：

- **第一次挥手（主动方发 FIN）**：主动关闭方告知对方：**我不再发数据了**。

- **第二次挥手（被动方回 ACK）**：被动方确认收到，此时连接**半关闭**。主动方不能发，被动方还可以继续发剩余数据。

- **第三次挥手（被动方发 FIN）**：被动方数据发送完毕，告知对方：我也不发了。

- **第四次挥手（主动方回 ACK）**：最终确认，双方彻底断开连接。

**面试必背一句话**：四次挥手因为 TCP 全双工通信，**读、写通道独立关闭**，无法一次性断开，所以需要四次。

#### 3\. TCP 粘包问题

**什么是粘包？**

TCP 是**流式协议**，没有数据包边界。多次发送的短小数据，会被操作系统缓冲区合并，导致一次 recv 读到多条数据、或者数据不完整，这就是粘包。

**粘包两种形态**：

- **打包**：多次发送的短数据，一次接收全部拿到

- **拆包**：一条大数据被拆分，多次接收才能拿完

**粘包产生根本原因（必背）**

1. TCP 无消息边界，流式传输

2. 操作系统存在 **发送缓冲区、接收缓冲区**

3. TCP 自带**Nagle算法**：合并小数据包减少网络开销

**如何解决粘包（工程方案）**

核心思路：**手动给数据加边界**，让数据有分割规则。

- 固定长度报文

- 特殊字符结尾分割（如换行符）

- **头部长度\+数据体**（企业最常用）：包头存数据长度，服务端先读包头、再精准读对应长度数据

**重要区分**：**UDP 不会粘包**！UDP 自带数据报文边界，一次发送对应一次接收，不会合并拆分。

TCP 是流式协议，无数据边界，多次发送的小数据会被内核合并接收，导致单次 recv 读取多条数据，即为粘包。

**适用场景**：对数据完整性要求极高的场景，HTTP、HTTPS、接口请求、文件传输、大模型服务通信（底层均基于 TCP）。

### 4\. TCP 最简实战代码

#### 服务端

```python
import socket

# 创建TCP套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 绑定IP和端口
server_socket.bind(("127.0.0.1", 8888))
# 开启监听
server_socket.listen(5)
print("服务端启动成功，等待客户端连接...")

# 阻塞等待客户端连接
conn, addr = server_socket.accept()
# 接收客户端数据
data = conn.recv(1024)
print("收到客户端数据：", data.decode("utf-8"))
# 响应数据
conn.send("收到消息！".encode("utf-8"))

# 关闭连接
conn.close()
server_socket.close()

```

#### 客户端

```python
import socket

# 创建TCP套接字
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 连接服务端
client_socket.connect(("127.0.0.1", 8888))

# 发送数据
client_socket.send("Hello TCP".encode("utf-8"))
# 接收响应
res = client_socket.recv(1024)
print("服务端响应：", res.decode("utf-8"))

client_socket.close()

```

### 5\. 废弃内容说明（重点）

UDP 聊天、TCP 多人聊天室、界面开发、消息广播、聊天记录保存等项目，**全部无需学习、无需编码**。

原因：属于传统老旧多线程 Socket 教学项目，生产环境 AI、大模型、大数据领域完全不用，现代服务统一基于 FastAPI、HTTP、SSE、gRPC、消息队列实现，手写裸 Socket 业务无工程价值、无面试加分。

### 6、Python Socket 全网常用核心函数

统一汇总 TCP/UDP 通用高频函数，无需死记，全部是工作常用 API。

```python
# 1. 创建套接字
socket.socket(family, type)
# family: AF_INET ipv4
# type: SOCK_STREAM(TCP) / SOCK_DGRAM(UDP)

# 2. 绑定地址端口（服务端专用）
socket.bind(("ip", port))

# 3. 开启监听（仅TCP服务端）
socket.listen(backlog)  

# 4. TCP专用：接受客户端连接（阻塞）
conn, addr = socket.accept()  

# 5. 接收数据
socket.recv(bufsize)       # TCP用
socket.recvfrom(bufsize)   # UDP用（返回数据+客户端地址）

# 6. 发送数据
socket.send(data)         # TCP用
socket.sendto(data, addr) # UDP用

# 7. 设置端口复用（解决重启端口占用报错）
socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 8. 设置超时阻塞时间
socket.settimeout(3)

# 9. 关闭套接字
socket.close()

```

### 7、Socket 关键面试区别

- TCP：**listen\(\) \+ accept\(\) \+ send\(\) \+ recv\(\)** 面向连接

- UDP：**无listen、无accept** 直接 recvfrom / sendto

## 二、并发编程核心体系

Python 并发三剑客：**多进程、多线程、协程**，分工明确，适配不同业务场景。

### 1\. 多进程 Process

#### 核心特性

- 资源完全隔离，每个进程拥有独立内存空间

- 不受 GIL 锁限制，**可以利用多核 CPU**

- 创建开销大、切换慢、通信复杂

#### 核心知识点

- 两种进程创建方式：普通创建、类继承创建

- **join\(\) 方法**：阻塞主进程，等待子进程执行完毕再继续执行

- 进程池 Pool：同步执行、异步执行，适合批量任务处理（大数据核心用法）

- 进程全局变量不共享，进程间通信唯一常用方式：Queue 队列

#### 适用场景

**CPU 密集型任务**：大数据计算、模型训练、批量数据处理、数值运算

#### 1\. 最基础：单个进程 / 多进程原生写法

```python

# 原生最基础多进程（无池、最简单）
from multiprocessing import Process
import time

def work(name):
    print(f"子进程 {name} 开始工作")
    time.sleep(2)
    print(f"子进程 {name} 结束工作")

if __name__ == "__main__":
    print("主进程开始")

    # 1. 创建子进程
    p1 = Process(target=work, args=("进程1",))
    p2 = Process(target=work, args=("进程2",))

    # 2. 启动进程
    p1.start()
    p2.start()

    # 3. 等待子进程结束
    p1.join()
    p2.join()

    print("主进程结束")

```

#### 2\. join\(\) 到底是干嘛的（必懂）

**不加join：主进程不等子进程，直接跑完结束**

**加了join：主进程阻塞，等子进程全部跑完再往下走**

#### 3\. 为什么需要「进程池」？

上面的原生写法有巨大问题：

- 如果我要开 **1000个任务**，难道手动写100次 Process\(\)？

- 频繁创建销毁进程 **极度消耗资源**

**进程池作用**：提前创建固定数量进程，循环复用，不用反复创建销毁，高效管理批量任务。

#### 4\. 进程池通俗版

```python

from multiprocessing import Pool
import time

def task(num):
    print(f"任务{num} 执行中")
    time.sleep(1)
    return num * 2

if __name__ == "__main__":
    # 池子里面永远只保留3个进程，反复干活
    with Pool(3) as p:
        # 把1-5五个任务丢进池子，自动分配执行
        res = p.map(task, [1, 2, 3, 4, 5])

    print("结果：", res)

```

#### 5\. 进程池同步、异步 通俗区别

- **map 同步**：任务全部跑完，代码才会往下走

- **apply\_async 异步**：丢任务进池子，代码直接往下走，不等结果

#### 6\. 进程核心总结

1. **原生 Process**：适合少量任务，手动创建、手动启动

2. **进程池 Pool**：适合大批量任务，自动复用进程、节省资源

3. **进程之间数据完全隔离**，全局变量不共享

4. **想要通信只能用 Queue**

5. Python 多进程**不受GIL限制**，唯一能利用多核CPU

#### 多进程常用核心函数汇总

```python
from multiprocessing import Process, Pool, Queue

# 1. 进程创建 & 启动
p = Process(target=func, args=(参数,))
p.start()        # 启动进程
p.join()         # 阻塞主进程，等待子进程结束
p.daemon = True  # 守护进程：主进程退出，子进程直接终止

# 2. 进程池常用
pool = Pool(n)           # 创建n个进程池
pool.map(func, 可迭代对象)  # 同步批量执行
pool.apply_async()       # 异步执行单个任务

# 3. 进程通信
q = Queue()
q.put(data)   # 存入数据
q.get()       # 取出数据

```

### 2\. 多线程 Thread

#### 核心特性

- 线程是轻量级进程，共享同一进程内存资源

- 创建开销小、切换快

- **GIL 全局解释器锁**：Python 同一时刻只有一个线程执行代码，无法利用多核

#### 1\. 守护线程

**通俗一句话定义**：守护线程就是「后台跟班线程」，**主线程是老大，老大走了，跟班必须强制陪葬**。

**普通线程 vs 守护线程 核心区别**

- **普通线程（默认）**：主线程执行完毕后，**会等待所有普通子线程跑完**，程序才会彻底退出

- **守护线程**：主线程执行完毕，**直接终止所有守护线程，程序立刻退出**，不等子线程执行完

##### 核心作用场景

专门用来做**后台辅助任务**：日志打印、心跳检测、状态监控、定时巡检。主业务结束，后台辅助任务直接停止，不需要继续跑。

##### 代码1：普通线程（默认不守护）

```python
import threading
import time

def task():
    # 子线程要跑3秒
    time.sleep(3)
    print("普通子线程执行完毕")

if __name__ == "__main__":
    t = threading.Thread(target=task)
    t.start()
    print("主线程执行完毕")
    # 结果：主线程跑完会等3秒，等子线程跑完才退出

```

##### 代码2：守护线程（Daemon=True）

```python
import threading
import time

def task():
    time.sleep(3)
    print("守护子线程执行完毕")

if __name__ == "__main__":
    # 设置为守护线程
    t = threading.Thread(target=task, daemon=True)
    t.start()
    print("主线程执行完毕")
    # 结果：主线程立刻退出，守护线程直接被杀死，不会打印上面语句

```

##### 关键注意点（面试坑点）

1. **守护线程必须在 start\(\) 之前设置**，启动后再设置会报错

2. 如果加了 **join\(\)**，无论是不是守护线程，主线程都会等待子线程结束

3. 守护线程适合辅助任务，核心业务绝对不能用守护线程（会被强制终止）

##### 面试标准话术

守护线程是后台辅助线程，生命周期跟随主线程，主线程结束后守护线程会立刻被销毁，无需执行完毕；常用于日志监控、心跳保活等非核心辅助任务，核心业务禁止使用。

#### 2\. 核心面试考点

- 守护线程：主线程退出，守护线程自动销毁

- 线程安全问题：多线程同时修改共享变量，产生脏数据

- 线程同步锁 Lock：解决线程安全问题，保证数据一致性

- 死锁：多个线程互相持有对方所需资源，互相等待卡死，需规避循环等待

- 守护线程：主线程退出，守护线程自动销毁

- 线程安全问题：多线程同时修改共享变量，产生脏数据

- 线程同步锁 Lock：解决线程安全问题，保证数据一致性

- 死锁：多个线程互相持有对方所需资源，互相等待卡死，需规避循环等待

#### 适用场景

**IO 密集型任务**：接口请求、文件读写、数据库查询、网络请求

#### 线程锁最简示例

```python
import threading

num = 0
lock = threading.Lock()

def add():
    global num
    for _ in range(100000):
        lock.acquire()  # 加锁
        num += 1
        lock.release()  # 解锁

t1 = threading.Thread(target=add)
t2 = threading.Thread(target=add)
t1.start()
t2.start()
t1.join()
t2.join()
print("最终结果：", num)

```

#### 多线程常用核心函数汇总

```python
import threading

# 1. 线程创建与启动
t = threading.Thread(target=func, args=())
t.start()        # 启动线程
t.join()         # 主线程阻塞等待
t.daemon = True  # 守护线程

# 2. 线程锁核心（解决线程安全）
lock = threading.Lock()
lock.acquire()   # 上锁
lock.release()   # 解锁

# 3. 获取当前线程信息
threading.current_thread()
threading.enumerate()

```

### 3\. 协程 Asyncio

#### 核心特性

- 单线程实现高并发，用户态切换，无系统开销，效率极高

- 主动切换任务，非抢占式调度

- 无需锁机制，天然线程安全

#### 核心知识点

- **async / await**：定义异步函数、阻塞等待异步任务

- **asyncio\.create\_task\(\)**：创建异步任务，实现多协程并发

- 协程返回值获取、任务终止、回调机制

#### 适用场景

大模型批量接口调用、SSE 流式输出、FastAPI 异步接口、RAG 多路并发检索、高并发 IO 任务

#### 多协程并发最简示例

```python
import asyncio

# 定义异步函数
async def work(num):
    print(f"协程{num}开始执行")
    await asyncio.sleep(1)
    print(f"协程{num}执行结束")
    return num

async def main():
    # 创建多个异步任务，并发执行
    tasks = [asyncio.create_task(work(i)) for i in range(3)]
    # 等待所有任务执行完毕
    res = await asyncio.gather(*tasks)
    print("任务返回结果：", res)

# 运行协程程序
asyncio.run(main())

```

#### 协程常用核心函数汇总

```python
import asyncio

# 1. 定义异步函数
async def func():
    await asyncio.sleep(1)  # 异步阻塞

# 2. 入口运行
asyncio.run(main())

# 3. 创建并发任务
task = asyncio.create_task(func())

# 4. 批量等待所有任务
await asyncio.gather(*tasks)

# 5. 休眠、超时控制
await asyncio.sleep(1)

```

## 三、并发模型终极选型

- **CPU 密集型 → 多进程**：规避 GIL 限制，利用多核提升算力

- **普通 IO 密集型 → 多线程**：轻量高效，适配常规网络、文件 IO

- **超高并发 IO（大模型/流式） → 协程**：单线程高吞吐，无切换开销，性能最优

## 四、核心面试必背总结

1. TCP 面向连接、可靠有序；UDP 无连接、高速不可靠，HTTP 基于 TCP 协议。

2. GIL 锁导致 Python 多线程无法利用多核，CPU 密集必须用多进程。

3. 进程资源隔离、线程资源共享、协程最轻量、并发效率最高。

4. 线程安全靠锁解决，死锁核心是循环等待资源，需主动规避。

5. 协程是大模型流式输出、异步接口、批量推理的底层核心支撑。
