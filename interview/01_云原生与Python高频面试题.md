# 🎓 云原生容器化 (Docker/K8s) & Python 底层与高并发面试高频题

> 本文档精选自云原生基础设施 (Docker, Kubernetes) 与 Python 语言底层机制、内存管理、高并发编程的核心面试考点，提供深度原理剖析与标准回答。

---

## 一、 Docker & 容器化技术

### Q1: Docker 的核心隔离与限制机制是什么？Namespace 和 cgroups 有何区别？
**标准回答**：
- **Namespace（命名空间）**：实现**资源隔离**（视图隔离）。Docker 利用 Linux 内核的 Namespace 机制，让容器拥有独立的资源视图。
  - `PID Namespace`：隔离进程 ID。
  - `NET Namespace`：隔离网络设备、IP 地址、端口及路由表。
  - `IPC Namespace`：隔离进程间通信（共享内存、信号量）。
  - `MNT Namespace`：隔离挂载点（文件系统视图）。
  - `UTS Namespace`：隔离主机名与域名。
  - `USER Namespace`：隔离用户与用户组。
- **cgroups（Control Groups，控制组）**：实现**资源限制与统计**。控制容器能够使用的物理资源上限（如 CPU 使用率/核数、Memory 内存配额、Disk I/O 读写限速、Network 带宽等），防止单个容器耗尽宿主机资源导致 OOM 或宕机。
- **总结区别**：Namespace 决定了容器**能看到什么**（隔离），cgroups 决定了容器**能用多少**（限制）。

---

### Q2: 详细说明 Docker 的联合文件系统 (UnionFS / Overlay2) 及其镜像分层机制。
**标准回答**：
- **联合挂载 (Union Mount)**：UnionFS 是一种分层、轻量级及高性能的文件系统，它支持把不同的目录联合挂载到同一个虚拟文件系统下。
- **Overlay2 结构**：
  - **Lowerdir（只读镜像层）**：包含 Docker 镜像构建时的各个层（Image Layers），只读不可变。多容器可共享同一个只读镜像层。
  - **Upperdir（可读写容器层）**：容器启动时在只读层之上创建的薄写层，保存容器运行期间所有产生的新增、修改文件。
  - **Mergeddir（联合挂载统一视图）**：挂载呈现给容器内部进程看到的最终完整文件系统目录。
- **写时复制 (Copy-on-Write, CoW)**：当容器修改 Lowerdir 中的只读文件时，Overlay2 不会直接修改只读层，而是将该文件复制一份到 Upperdir 中再进行修改。删除文件时，则在 Upperdir 中创建一个空隐藏掩码文件（whiteout file）。
- **优势**：节省存储空间、镜像下载极快、容器启动秒级响应。

---

## 二、 Kubernetes (K8s) 架构与组件

### Q3: 请简述 Kubernetes 的核心架构，并说明创建一个 Pod 的完整工作流程。
**标准回答**：
- **核心组件**：
  - **Control Plane（控制平面）**：`kube-apiserver`（统一入口与 REST API）、`etcd`（高可用分布式元数据存储）、`kube-scheduler`（Pod 调度决策）、`kube-controller-manager`（自动化状态控制器集合）。
  - **Worker Node（工作节点）**：`kubelet`（节点 Agent，管理容器生命周期）、`kube-proxy`（管理节点网络代理与 Service 负载均衡）、`Container Runtime`（如 containerd/CRI-O）。
- **创建 Pod 完整流程**：
  1. 用户通过 `kubectl` 或 API 向 `kube-apiserver` 发送创建 Pod 请求（YAML）。
  2. `kube-apiserver` 校验权限与语法后，将 Pod 配置持久化写入 `etcd`。
  3. `kube-scheduler` 监听到未绑定的 Pod，根据资源需求、亲和性/反亲和性、污点/容忍度等策略计算最优节点，并将调度结果写入 `etcd`。
  4. 目标节点的 `kubelet` 通过 Watch 机制监听到分配给本节点的 Pod。
  5. `kubelet` 调用 Container Runtime (CRI) 拉取镜像并创建容器，调用 CNI 网络插件配置 Pod IP，调用 CSI 存储插件挂载存储卷。
  6. 容器启动完成后，`kubelet` 向 `kube-apiserver` 汇报 Pod 状态为 `Running`。

---

### Q4: K8s 的 Service 是如何实现负载均衡的？kube-proxy 的 iptables 与 IPVS 模式有什么区别？
**Standard Answer**：
- **Service 原理**：Service 是对一组提供相同服务的 Pod 的抽象访问入口（拥有固定 ClusterIP），通过 Label Selector 动态关联背后的 Endpoints (Pod IP:Port)。
- **kube-proxy 工作模式对比**：
  - **iptables 模式**：
    - 原理：kube-proxy 监控 APIServer，当 Service/Endpoint 变化时生成对应的 iptablesDNAT/SNAT 规则。
    - 缺点：规则呈线性链表存储，规则数量成成千上万（大集群）时，查找延迟急剧上升（复杂度 $O(n)$），刷链时全量更新易导致 CPU 飙高。
  - **IPVS 模式（推荐生产使用）**：
    - 原理：基于 Linux 内核 Netfilter Hook，使用哈希表（Hash Table）存储路由规则（复杂度 $O(1)$）。
    - 优点：高性能、低延迟，支持多种负载均衡算法（如 rr 轮询、lc 最小连接、dh 目标哈希等），并且支持节点健康检查与会话保持。

---

## 三、 Python 编程底层机制与内存管理

### Q5: 详细剖析 Python 中 `__new__` 与 `__init__` 的底层区别，并写出一个线程安全的单例模式。
**标准回答**：
- **核心区别**：
  - `__new__(cls, *args, **kwargs)`：**构造方法**。静态方法（首个参数为类对象 `cls`），负责在内存中开辟空间并创建/返回类的新实例对象。
  - `__init__(self, *args, **kwargs)`：**初始化方法**。实例方法（首个参数为实例 `self`），在 `__new__` 返回实例后被自动调用，负责给实例的属性赋值。
- **线程安全的单例模式 (Singleton Pattern)**：
```python
import threading

class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # 双重检查锁 (Double-Checked Locking)
                    cls._instance = super().__new__(cls)
        return cls._instance
```

---

### Q6: 简述 Python 的垃圾回收 (GC) 机制（引用计数 + 标记清除 + 分代回收）。
**标准回答**：
1. **引用计数 (Reference Counting) - 主机制**：
   - 每个 Python 对象头中都有一个 `ob_refcnt` 变量记录被引用次数。
   - 当引用增加（如赋值、作为参数传递）时 `+1`；引用减少（如 `del`、超出作用域）时 `-1`。
   - 当 `ob_refcnt == 0` 时，对象被立即销毁并回收内存。
   - **缺点**：无法解决**循环引用**（如 `a.py = b; b.px = a`）。
2. **标记清除 (Mark-Sweep) - 辅助机制**：
   - 主要针对容器对象（如 `list`, `dict`, `tuple`, 自定义类）。
   - 从根对象（Root Object：全局变量、栈帧中的局部变量）出发，沿着引用链遍历标记所有可达（Reachable）对象；未被标记到的对象即为不可达（Unreachable）的循环引用垃圾，予以清除。
3. **分代回收 (Generational Collection) - 性能优化**：
   - 依据经验法则：“存活时间越长的对象，越不可能是垃圾”。
   - 将对象划分为三代：`0 代`（新创建对象）、`1 代`（经历一次 GC 存活）、`2 代`（经历多次 GC 存活）。
   - 0 代触发 GC 频率最高，2 代最低，从而大幅降低全量 GC 的开销。

---

## 四、 Python 高并发编程（多线程 / 多进程 / asyncio）

### Q7: 什么是 Python 的 GIL（全局解释器锁）？它对多线程 CPU 密集型与 I/O 密集型任务有何影响？如何绕过 GIL？
**标准回答**：
- **GIL (Global Interpreter Lock) 定义**：CPython 解释器中的一个互斥锁，确保在任何时刻只有一个线程在 CPU 核心上执行 Python 字节码。它的存在主要是为了保护 CPython 内部非线程安全的内存管理（如引用计数计数器的并发修改安全）。
- **对不同任务的影响**：
  - **I/O 密集型任务**（如网络请求、文件读写、数据库查询）：线程在等待 I/O 时会自动释放 GIL，其他线程可以继续获得 GIL 执行，因此**多线程能显著提升性能**。
  - **CPU 密集型任务**（如复杂数学计算、图像处理）：多线程无法利用多核 CPU，反而因线程频繁上下文切换和 GIL 竞争导致**比单线程更慢**。
- **绕过/解决 GIL 的方案**：
  1. **使用多进程 (`multiprocessing`)**：每个进程拥有独立的 CPython 解释器实例和独立的内存空间，彻底绕过 GIL，利用多核 CPU。
  2. **使用 C/C++/Rust 扩展模块**：在计算密集的 C 扩展部分手动释放 GIL（如 NumPy, PyTorch 底层）。
  3. **使用异步编程 (`asyncio`)**：单线程事件循环处理海量并发 I/O 任务。
  4. **使用无 GIL 解释器**：如 PyPy（部分支持）或 Python 3.13 引入的自由线程模式（Free-threaded CPython / PEP 703）。

---

### Q8: 深入说明 Python `asyncio` 协程的核心运行原理（事件循环、Future、Task）。
**标准回答**：
- **核心组件关系**：
  - **EventLoop（事件循环）**：单线程上的死循环，不断监视注册的 Socket 文件描述符 (FD) 事件状态（底层基于 OS 提供的 `epoll` / `kqueue` / `select` 系统调用）。
  - **Coroutine（协程）**：使用 `async def` 定义的函数，调用时返回协程对象。自身不会自动运行，需要放入事件循环中调度。
  - **Future**：代表一个未来的异步操作结果，包含状态（`PENDING`, `CANCELLED`, `FINISHED`）和回调函数链。
  - **Task**：`Future` 的子类，用于把协程包裹起来，并负责将协程一步步推进（驱动 `send(None)` 并在遇到 `await` I/O 阻塞时挂起让出 CPU）。
- **运行机理**：
  1. 协程执行到 `await asyncio.sleep()` 或异步网络 I/O 时，向事件循环注册 Socket 读写监听事件并挂起当前协程。
  2. 事件循环立即切换去执行其他就绪状态的 Task。
  3. 当操作系统内核通知某个 Socket I/O 数据已就绪（如通过 `epoll_wait`），事件循环唤醒对应的 Task 恢复执行 `send()` 推进下一步。
