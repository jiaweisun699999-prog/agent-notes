# Kubernetes

## 一、K8S简介

### 1、传统Docker的局限性

Docker 无疑是一场革命，它通过“镜像（Image）”和“容器（Container）”彻底解决了**环境一致性**（“在我机器上能跑，在服务器上跑不了”）的问题。

但当应用规模从“单体架构”**演变为**“大型微服务架构”，或者业务访问量爆发时，**单靠 Docker 或 Docker Compose 在生产环境中就会遇到极大的局限性**：

- **单机局限，无法做跨机器的集群调度**： Docker 和 Docker Compose 本质上都是**单机工具**。如果你有 20 台物理服务器，想把 100 个容器均匀部署上去，Docker 无法自动评估哪台服务器 CPU 空闲、哪台内存满了。你必须手动登录到每一台机器上去敲 `docker run`。
- **缺乏真正的自动自愈能力（Self-Healing）**： 虽然 Docker 提供了 `--restart=always`，但这只能解决“容器内部进程崩溃重启”。**如果宿主机本身断电、蓝屏或网线被拔掉**，Docker 无能为力，这台机器上的所有服务就彻底挂掉了，无法自动迁移到健康的机器上。
- **无法实现弹性伸缩（Auto-Scaling）**： 面对突发流量（比如大促活动、热点新闻），单靠 Docker 需要运维人员手动敲命令去增加容器数量；流量退去后又得手动删容器，整个过程极度依赖人工，滞后且容易出错。
- **复杂的网络与服务发现**： 当数十个微服务分布在不同的物理机上时，容器的 IP 是动态变化的。Docker 缺乏一套原生且高效的机制，来自动管理跨机器容器之间的通信、域名解析和流量负载均衡。
- **更新升级容易中断服务（无滚动更新）**： 使用 Docker 升级应用时，通常需要先停掉旧容器，再启动新容器。在这重启的几秒到几分钟内，用户请求会直接报错（502/504），无法做到零停机平滑过渡。

### 2、K8S产生的背景

为了解决上述 Docker 的单机局限与大规模容器运维痛点，**容器编排（Container Orchestration）** 技术应运而生。

- **Google 15 年 Borg 系统的基因传承**： Google 内部很早就使用了名为 **Borg** 的内部超大规模集群管理系统，用它来管理全球数据中心的数十亿个容器。2014 年，Google 借鉴 Borg 的核心思想与架构经验，用 Go 语言重构并开源了 **Kubernetes**（简称 K8s，源自希腊语，意为“舵手”或“飞行员”）。
- **CNCF 基金会与云原生标准**： 为了打破单一家大厂控制开源项目的局面，Google 将 K8s 捐赠给了 **CNCF（云原生计算基金会）**。由于其出色的架构设计和谷歌的背书，K8s 击败了同期的 Docker Swarm 和 Apache Mesos，成为了**事实上的云原生操作系统标准**。

### 3、K8S的核心思想

理解 K8s 的核心思想，是后续编写 YAML 文件和敲 `kubectl` 命令的底层思维基石。K8s 的设计理念主要体现在以下 3 个核心思想上：

#### ① 声明式 API（Declarative API）与期望状态（Desired State）

- **传统命令式（Imperative）**：“请去 192.168.1.100 机器上，帮我拉取 Nginx 镜像，然后启动一个容器，把 80 端口映射出来。”（每一步都要你传达命令）
- **K8s 声明式（Declarative）**：你写一份 YAML 配置文件，直接告诉 K8s：**“我不管你用什么方法，请在集群里时刻给我保持 3 个 Nginx 容器处于运行状态。”**
- **控制回路（Control Loop）**：K8s 内部有一个无限循环的“管家机制”。它会不断对比**实际状态（Actual State）\**与你声明的\**期望状态（Desired State）**。如果发现某台机器宕机，实际只剩 2 个容器了，它会自动在其他机器上拉起第 3 个，直到实际状态再次匹配期望状态。

#### ② 抽象与解耦（一切皆资源对象）

K8s 极具前瞻性地将复杂的底层计算、网络、存储资源抽象成了统一的**资源对象（Objects）**：

- **解耦应用与底层物理机**：开发者只需要关心 API 与对象，不需要关心应用究竟运行在哪台具体的物理机上。
- **Pod 抽象**：K8s 不直接操作单个 Docker 容器，而是提出了 **Pod**（豆荚）的概念，将紧密相关的容器封装在一起，作为最小调度单元。
- **Service 抽象**：将频繁变动的 Pod IP 隐藏在 Service 的固定 ClusterIP 后面，实现稳定的服务发现与负载均衡。

#### ③ 自动化与自愈（Automation & Self-healing）

K8s 把原本需要高级运维人工处理的繁琐工作（如重启挂掉的容器、替换故障节点、根据 CPU 利用率自动扩缩容、滚动更新与一键回滚），全部变成了**代码化、自动化的基础设施控制流程**。

## 二、K8S 架构设计与核心组件

K8s 采用标准的**主从（Master-Worker）架构**。你可以把整个 K8s 集群想象成一个**高度自动化的工厂**：

- **Master 节点（控制面 Control Plane）**：相当于“工厂指挥部/大脑”，负责接单（API）、调度排班（Scheduler）、监控生产状态（Controller）和保存档案（etcd）。
- **Worker 节点（工作面 Data Plane）**：相当于“生产车间/仓库”，负责真实拉取镜像、运行容器并维护网络与存储。

```python
┌─────────────────────────────────────────────────────────────┐
│                   Master Node (控制节点 / 指挥部)              │
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────┐   │
│  │  kube-apiserver │ │ kube-scheduler│ │kube-controller-manager│
│  │ (集群大门/入口) │ │  (调度排班员)  │ │ (状态监控管家) │   │
│  └──────┬───────┘   └──────────────┘   └────────────────┘   │
│         │                                                   │
│  ┌──────┴───────┐                                           │
│  │    etcd      │                                           │
│  │ (集群数据库) │                                           │
│  └──────────────┘                                           │
└─────────┬───────────────────────────────────────────────────┘
          │ (指令下发 / 状态汇报)
          ├──────────────────────────────┐
          ▼                              ▼
┌──────────────────┐           ┌──────────────────┐
│  Worker Node 1   │           │  Worker Node 2   │
│   (车间/节点A)    │           │   (车间/节点B)    │
│                  │           │                  │
│ ┌──────────────┐ │           │ ┌──────────────┐ │
│ │   kubelet    │ │           │ │   kubelet    │ │
│ │  (厂长/看门人)│ │           │ │  (厂长/看门人)│ │
│ └──────────────┘ │           │ └──────────────┘ │
│ ┌──────────────┐ │           │ ┌──────────────┐ │
│ │  kube-proxy  │ │           │ │  kube-proxy  │ │
│ │ (网络路由器)  │ │            │ │ (网络路由器) │ │
│ └──────────────┘ │           │ └──────────────┘ │
│ ┌──────────────┐ │           │ ┌──────────────┐ │
│ │ Container    │ │           │ │ Container    │ │
│ │ Runtime      │ │           │ │ Runtime      │ │
│ │(containerd/  │ │           │ │(containerd/  │ │
│ │   Docker)    │ │           │ │   Docker)    │ │
│ └──────────────┘ │           │ └──────────────┘ │
└──────────────────┘           └──────────────────┘
```

### 1. Master 节点核心组件（大脑与控制面）

Master 节点负责管理整个集群，集群中的所有决策（如调度、响应事件、平滑升级）都由它发起。

#### ① `kube-apiserver`（集群统一网关与入口）

- **角色**：工厂的“总接单前台”。
- **职责**：
  - 是集群内部与外部通信的**唯一入口**。不管是我们用 `kubectl` 敲命令，还是 YAML 文件，甚至是 Worker 节点的组件汇报状态，**全部都要走 API Server**。
  - 负责安全认证（Authentication）、鉴权（Authorization）和准入控制（Admission Control）。
  - 它是唯一有权限直接读写 `etcd` 数据库的组件。

#### ② `etcd`（高可用分布式键值数据库）

- **角色**：工厂的“核心档案室”。
- **职责**：
  - 一个用 Go 语言编写的高可用、强一致性的分布式键值（KV）数据库。
  - **存储了集群所有的状态数据**（比如当前集群有几个 Node、部署了哪些 Pod、每个 Pod 的 IP 和配置等）。
  - *注意：etcd 绝对不能崩溃！一旦 etcd 数据丢失，整个 K8s 集群的状态就瘫痪了，因此生产环境中 etcd 必须做高可用集群备份。*

#### ③ `kube-scheduler`（资源调度器）

- **角色**：工厂的“排班调度员”。
- **职责**：
  - 专门监听新建的 Pod，为其**选择一个最合适的 Worker 节点**去运行。
  - 调度过程分两步：
    1. **过滤（Filtering/Predicates）**：筛选出满足 Pod 硬件资源要求（如 CPU/内存足够、显卡资源匹配）的节点。
    2. **打分（Scoring/Priorities）**：在过滤出的节点中打分，选出负载最合理、综合得分最高的节点分配给该 Pod。

#### ④ `kube-controller-manager`（自动化状态管家）

- **角色**：工厂的“巡视督导管家”。
- **职责**：
  - 运行着各种**控制器（Controllers）**（如 NodeController、DeploymentController、PodGC 等）。
  - 它内部不断执行**控制回路（Control Loop）**：“读取期望状态 $\rightarrow$ 检查实际状态 $\rightarrow$ 发现不一致 $\rightarrow$ 发起修复”。
  - *例子*：声明了 3 个 Pod 副本，如果有一个 Pod 挂了，DeploymentController 就会监听到，并通知 API Server 去新建一个 Pod。

### 2. Worker 节点核心组件（车间与数据面）

Worker 节点是真正干活的地方，负责接收 Master 的命令，并在本地运行容器。

#### ① `kubelet`（驻场厂长 / 节点看门人）

- **角色**：车间里的“驻场厂长”。
- **职责**：
  - **每台 Worker 节点上都会运行一个 `kubelet` 进程**。
  - 负责与 Master 节点的 `api-server` 保持持续通信，接收派发给本节点的任务（ PodSpec）。
  - 调用本地的容器运行时去创建、启动、停止容器，并**持续监控本地容器和节点的健康状态**，定时向 `api-server` 汇报。

#### ② `kube-proxy`（网络路由代理）

- **角色**：车间的“网络路由与分流员”。
- **职责**：
  - 运行在每个 Worker 节点上，维护节点上的网络规则（利用 Linux 的 `iptables` 或 `IPVS` 技术）。
  - 负责实现 **Service 的虚拟 IP（ClusterIP）机制与负载均衡**。当流量发往某 Service 时，`kube-proxy` 负责把请求均匀地转发给后端的各个 Pod。

#### ③ `Container Runtime`（容器运行时）

- **角色**：车间里的“底层打包与运行机器”。
- **职责**：
  - 负责下载镜像以及真正运行容器的底座软件。
  - 早期 K8s 默认使用 Docker，后来为了轻量化和标准化（CRI 规范），目前主流生产环境已全面转向 **`containerd`** 或 **`CRI-O`**。

### 3. 一次完整的 Pod 创建全流程

理解了这个流程，你就彻底搞懂了 K8s 架构组件间是如何联动的：

**1.1. 提交请求:**

用户执行 `kubectl apply -f nginx.yaml`，请求发送给 Master 的 api-server。

**2.2. 校验与写入:**

api-server 校验通过后，将“期望创建一个 Nginx Pod”的信息写入 etcd。

**3.3. 调度排班:**

kube-scheduler 监听到有新 Pod 处于 Pending 状态，开始评估节点，最终选择 Worker Node 1，并将调度结果告知 api-server（更新写回 etcd）。

**4.4. 下发执行:**

Worker Node 1 上的 kubelet 监听到有分配给自己的 Pod 任务，调用本地的 Container Runtime（如 containerd）拉取镜像并启动容器。

**5.5. 状态汇报:**

容器启动成功后，kubelet 将 Pod 的运行状态（如 Running、分配的 IP）汇报给 api-server，存入 etcd。

### 💡 组件速记与对照表

| **组件名称**                  | **属于 Master 还是 Worker** | **核心一句话功能**                                 |
| ----------------------------- | --------------------------- | -------------------------------------------------- |
| **`kube-apiserver`**          | Master                      | 集群大门，唯一的请求入口与控制中心。               |
| **`etcd`**                    | Master                      | 存储整个集群状态数据的键值数据库。                 |
| **`kube-scheduler`**          | Master                      | 计算并决定 Pod 应该运行在哪台机器上。              |
| **`kube-controller-manager`** | Master                      | 监控集群实际状态，维持“期望状态”与“实际状态”一致。 |
| **`kubelet`**                 | Worker                      | 接收指令，管理本地节点上的容器生命周期。           |
| **`kube-proxy`**              | Worker                      | 维护节点网络规则，实现 Service 负载均衡与转发。    |
| **`Container Runtime`**       | Worker                      | 容器运行底座（如 containerd / Docker）。           |

## 三、 K8S 4 大核心对象解析

在 K8s 中，**“一切皆对象”**。无论你是要部署一个普通的 Web 服务、一个数据库，还是一个复杂的 AI 大模型推理引擎，本质上都是在通过编写 YAML 文件去声明和管理这些对象。

我们可以先通过这张关联图厘清这 4 个最核心对象之间的层级与协作关系：

```python
┌──────────────────────────────────────────────────────────────┐
│  Ingress (集群最外层：七层 HTTP/HTTPS 入口，支持域名分流)          │
└──────────────────────────────┬───────────────────────────────┘
                               │ (路由分发)
                               ▼
┌──────────────────────────────────────────────────────────────┐
│  Service (集群内部固定入口：ClusterIP，提供服务发现与负载均衡)      │
└──────────────────────────────┬───────────────────────────────┘
                               │ (基于 Label Selector 匹配)
                               ▼
┌──────────────────────────────────────────────────────────────┐
│  Deployment (控制层：管理 Pod 副本数量、实现滚动升级与自愈)         │
└──────────────────────────────┬───────────────────────────────┘
                               │ (控制/维护多个 Pod 实例)
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
┌──────────────────┐┌──────────────────┐┌──────────────────┐
│      Pod 1       ││      Pod 2       ││      Pod 3       │
│ ┌──────────────┐ ││ ┌──────────────┐ ││ ┌──────────────┐ │
│ │  App Container│ ││ │  App Container│ ││ │  App Container│ │
│ └──────────────┘ ││ └──────────────┘ ││ └──────────────┘ │
└──────────────────┘└──────────────────┘└──────────────────┘
```

### 1. Pod（K8s 的最小调度基本单元）

#### ① 为什么 K8s 不直接操作单个 Docker 容器，而是设计 Pod？

- **比喻**：Pod（豆荚）就像是一个封装胶囊，里面的 Container（豌豆）是实际运行的进程。
- **紧密协同场景**：在实际业务中，有些容器必须“同生共死”、高频共享数据或网络（比如：一个容器跑主应用 Nginx/Python API，另一个 **Sidecar 辅助容器** 负责实时收集日志或监控指标）。如果把它们分散在不同机器上，网络延迟会极高。

#### ② Pod 的核心特性

- **共享网络栈（Shared Network）**：同一个 Pod 内部的所有容器，共享同一个网络命名空间（IP 地址、端口号）。Pod 内的容器间可以通过 `localhost:端口` **直接进行本地通信**。
- **共享存储卷（Shared Volumes）**：同一个 Pod 内的多个容器可以挂载同一个磁盘数据卷（Volume），实现文件共享。
- **短暂性（Ephemeral）**：**Pod 是有生命周期的，且随时可能死亡**。如果节点宕机，该 Pod 就废了。新建的 Pod 会拥有一个**全新的 IP 地址**。

### 2. Deployment（自动化副本控制器）

#### ① 为什么不能直接手动创建裸 Pod？

因为裸 Pod 一旦崩掉或者宿主机宕机，没有东西会自动把它拉起来。在生产环境中，**我们几乎永远不会直接创建单个 Pod，而是通过 Deployment 来管理 Pod**。

#### ② Deployment 的 4 大核心能力

1. **期望状态与副本保持（Replicas）**：在 YAML 中声明 `replicas: 3`，Deployment 就会确保集群中时刻有 3 个健康的 Pod 在运行。
2. **故障自愈（Self-Healing）**：如果某个 Pod 崩溃或所在的节点宕机，Deployment 会自动在其他健康节点上拉起一个新的 Pod。
3. **零停机滚动更新（Rolling Update）**：修改镜像版本时， Deployment 会“先启动一个新版本 Pod，正常提供服务后，再销毁一个旧版本 Pod”，实现用户无感知的平滑升级。
4. **一键版本回滚（Rollback）**：如果新版本代码报错，一条命令就能把整个 Pod 组合恢复到上一个历史版本。

### 3. Service（服务发现与固定入口）

#### ① 解决什么痛点？

前面提到，Pod 的生命周期是短暂的，销毁重建后 **IP 地址会频繁变动**。如果前端或上游服务直接调用具体的 Pod IP，系统必然崩溃。

#### ② Service 的核心功能

- **固定 IP 与域名**：Service 会为一组相同功能的 Pod 绑定一个**固定且永不改变的虚拟 IP（ClusterIP）**。
- **基于 Label（标签）的服务发现**：Service 靠 **`selector`（标签选择器）** 去精准匹配后端绑定了特定 Label 的 Pod（比如 `app: my-api`）。
- **自动负载均衡**：当流量发往 Service 的 ClusterIP 时，底层的 `kube-proxy` 会将请求按照轮询等算法**均匀地分发**给后端的各个健康 Pod。

#### ③ 常用 Service 类型

1. **`ClusterIP`（默认）**：仅在集群内部可访问的虚拟 IP（适合微服务内部互相调用，如 API 调用 MySQL/Redis）。
2. **`NodePort`**：在集群的每一台机器（Node）上都开放一个指定端口（如 30080），将外网流量直接映射引入到内部 Service（适合测试环境或简易暴露服务）。
3. **`LoadBalancer`**：结合公有云（AWS、阿里云等）自动创建云厂商的外部负载均衡器。

### 4. Ingress（七层 HTTP/HTTPS 统一网关）

#### ① 为什么有了 Service NodePort 还需要 Ingress？

- `NodePort` 的缺点：每一个服务都要占用节点上的一个高位端口（30000-32767），端口数量有限，且暴露大量端口很不安全。
- `Ingress` 的优势：它是集群最外侧的**统一域名网关**（底层通常是基于 Nginx 或 Envoy 开发的控制器）。**只需要占用宿主机的 80 / 443 端口**，就能根据**域名**和 **URL 路径**将流量路由给内部不同的 Service。

#### ② 核心路由机制示例

```python
请求地址: https://app.example.com/api/v1  --> Ingress 匹配到 /api  --> 路由给 api-service
请求地址: https://app.example.com/web     --> Ingress 匹配到 /web  --> 路由给 web-service
```

此外，Ingress 还方便统一配置 **SSL/TLS 证书卸载**（在 Ingress 处统一配置 HTTPS，内部流量走 HTTP）以及流式 responses（如 SSE 长连接）支持。

### 5. 一份包含 3 大核心对象的标准 YAML 拆解

在实际开发中，我们通常把同一个服务的对象定义写在一个 YAML 文件里（用 `---` 隔开）：

YAML

```python
# ------------------ 1. 定义 Deployment ------------------
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-deployment
spec:
  replicas: 3                   # 保持 3 个副本
  selector:
    matchLabels:
      app: my-app               # 1. 寻找匹配这个 Label 的 Pod 进行管理
  template:                     # Pod 的定义模板
    metadata:
      labels:
        app: my-app             # 2. 给生成的 Pod 贴上 app: my-app 的标签
    spec:
      containers:
      - name: web-container
        image: nginx:1.25
        ports:
        - containerPort: 80

---
# ------------------ 2. 定义 Service ------------------
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  type: ClusterIP               # 集群内部访问
  selector:
    app: my-app                 # 3. 极其重要！Service 通过这个标签绑定上述的 Pod
  ports:
  - port: 8080                  # Service 暴露的端口
    targetPort: 80              # 转发给容器内部的真实端口号

---
# ------------------ 3. 定义 Ingress ------------------
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
spec:
  rules:
  - host: myapp.example.com     # 域名匹配
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-app-service # 4. Ingress 将域名请求路由给上述的 Service
            port:
              number: 8080
```

### 💡 四大对象总结

| **核心对象**   | **角色定位**   | **一句话底层逻辑**                                    |
| -------------- | -------------- | ----------------------------------------------------- |
| **Pod**        | 最小颗粒度     | 容器胶囊，共享网络与存储，生命周期短暂。              |
| **Deployment** | 自动化管家     | 靠 Label 选定 Pod，保证副本数量、做自愈和滚动更新。   |
| **Service**    | 内部固定入口   | 靠 Label 绑定 Pod，提供固定 ClusterIP 和负载均衡。    |
| **Ingress**    | 最外层七层网关 | 靠域名和路径规则分发流量给 Service，统一 HTTPS 卸载。 |

## 四、 本地极简安装与实践操作 (Minikube 篇)

Minikube 里面运行的就是正宗的 K8s，它就是专门为了本地开发和学习而生的“轻量打包版 K8s”。用 Minikube 这个自动化工具，快速帮你装好了一个单节点（Single-Node）的 K8s 集群。降低 90% 的搭建门槛（防入门即放弃）

- **原生 K8s 安装（`kubeadm` / 二进制）**：

  - 需要准备至少 2~3 台服务器/虚拟机。
  - 需要配置复杂的静态 IP、修改 `/etc/hosts`、关闭防火墙/SWAP/SELinux、配置复杂的 CNI 网络插件（如 Calico / Flannel）、手动签发 TLS 证书。
  - 只要其中一个步骤选错，集群就无法初始化，非常挫伤学习积极性。

- **Minikube 安装**：

  - 把所有 Master（`api-server`、`etcd` 等）和 Worker（`kubelet` 等）组件打包封装在一个虚拟机或 Docker 容器里。

  - **只需一行命令（`minikube start`）**，就能在 3 分钟内自动拉起一个完整的 K8s 环境，把核心精力放在学习 `kubectl` 和写 `YAML` 上。

    | **维度**             | **Minikube**                                    | **原生企业级 K8s (如 kubeadm 部署)**              |
    | -------------------- | ----------------------------------------------- | ------------------------------------------------- |
    | **本质**             | K8s 的本地开发/测试镜像封装工具。               | 生产环境的多节点分布式集群。                      |
    | **使用的命令**       | 完全一样（都用 **`kubectl`** 操作）。           | 完全一样（都用 **`kubectl`** 操作）。             |
    | **API 与 YAML 语法** | 100% 相同（完全遵从 K8s 官方 API）。            | 100% 相同。                                       |
    | **节点数量**         | 通常为 1 个节点（控制节点与工作节点混在一起）。 | 多个 Master（高可用） + 几十/上百个 Worker 节点。 |
    | **使用场景**         | 个人电脑学习、开发调试、CI/CD 自动化测试。      | 生产环境部署、高并发业务。                        |

针对你的 **VMware 虚拟机（CentOS 7 + Docker 26.1.4 + 4GB 内存 / 2 核）** 黄金配置，这里为你梳理一份**没有任何多余步骤、专门避开国内网络坑**的完整 Minikube 安装与实操流程：

# 四、本地极简安装与实践操作 (Minikube 终极通关篇)

### 步骤 1：前置环境准备与关闭 Swap

K8s 强要求关闭系统 Swap 交换分区，并确保 SELinux 不阻挡容器通信：

```python
# 1. 临时与永久关闭 Swap 分区
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

# 2. 临时关闭 SELinux
sudo setenforce 0

# 3. 确保 Docker 正常运行
sudo systemctl start docker
sudo systemctl enable docker
```

### 步骤 2：下载并安装 `kubectl` (K8s 官方命令行客户端)

```python
# 1. 下载 v1.28.2 稳定版 kubectl 二进制文件
curl -LO "https://dl.k8s.io/release/v1.28.2/bin/linux/amd64/kubectl"

# 2. 赋予执行权限并放入系统 Path
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/

# 3. 验证安装
kubectl version --client
```

### 步骤 3：下载并安装 Minikube 可执行文件

```python
# 1. 下载 Minikube 二进制文件
curl -LO https://storage.googleapis.com/minikube/releases/v1.33.1/minikube-linux-amd64

# 2. 赋予执行权限并安装
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# 3. 验证版本
minikube version
```

### 步骤 4：一键拉起 Minikube 集群（关键核心命令）

复制并在终端中运行下面这条**量身定制的国内加速启动命令**（宿主有VPN的关闭VPN）：

```python
minikube start \
  --driver=docker \
  --force \
  --memory=2048mb \
  --cpus=2 \
  --kubernetes-version=v1.28.3 \
  --image-mirror-country='cn' \
  --image-repository='registry.cn-hangzhou.aliyuncs.com/google_containers'
```

> **参数说明**：
>
> - `--memory=2048mb`：严格限制使用 2GB 内存，为 CentOS 7 系统留足 2GB 物理内存，防止 VMware 虚拟机因内存不足卡死。
> - `--kubernetes-version=v1.28.3`：锁定稳定版本，避开阿里云新版本 OSS 404 文件下载报错的坑。
> - `--image-repository=...`：全量使用阿里云镜像源，无需访问谷歌 `gcr.io` 镜像。

### 步骤 5：验证集群健康状态

等待终端最后输出 `Done! kubectl is now configured to use "minikube" cluster...` 后，输入：

```python
kubectl get nodes
```

> **成功标志**：看到节点名为 `minikube` 且 `STATUS` 显示为 **`Ready`**！

### 实践操作（用 `kubectl` 部署并测试第一个 Nginx 服务）

环境通关后，我们用实践命令体验 K8s 中的 3 个核心对象（`Pod`、`Deployment`、`Service`）：

#### 步骤 1：导入镜像并部署 Deployment（2 个副本）

由于国内网络限制，建议先将镜像拉取到本地并加载进 Minikube 集群，再进行创建：

```python
# 1. 在宿主机拉取镜像并加载进 Minikube 集群
docker pull nginx:1.25
minikube image load nginx:1.25

# 2. 创建 Deployment（保持 2 个副本）
kubectl create deployment my-nginx --image=nginx:1.25 --replicas=2
```

#### 步骤 2：查看 Pod 的运行状态

```python
kubectl get pods -o wide
```

> **成功标志**： 看到 2 个名为 `my-nginx-xxxx-yyyy` 的 Pod，`READY` 显示为 **`1/1`**，`STATUS` 显示为 **`Running`**，且分别被分配了独立的 Cluster IP。

#### 步骤 3：创建 Service 对外暴露 NodePort 端口

```python
kubectl expose deployment my-nginx --port=80 --type=NodePort --name=my-nginx-service
```

#### 步骤 4：查看 Service 端口与节点 IP

由于 Minikube 使用 Docker 驱动（`--driver=docker`），宿主机无法直接访问容器内网的 ClusterIP，需要通过  Minikube 节点 IP + NodePort 映射端口 进行访问：

```python
# 1. 查看 Service 映射的外部 NodePort 端口（找到 PORT(S) 列中的 3xxxx 端口，如 30661）
kubectl get svc my-nginx-service

# 2. 查看 Minikube 节点的真实 IP
minikube ip
```

#### 步骤 5：连通性测试-访问 Nginx 服务

在宿主机终端中，结合节点 IP 与映射端口直接运行 `curl`：

```python
# 方式 A：直接使用变量自动拼接访问（推荐）
curl http://$(minikube ip):$(kubectl get svc my-nginx-service -o jsonpath='{.spec.ports[0].nodePort}')

# 方式 B：手动填入节点 IP 和端口（假设 nodePort 为 30661）
curl http://$(minikube ip):30661
```

> **响应验证**： 如果终端返回 `<!DOCTYPE html>` 以及 `Welcome to nginx!` 的 HTML 页面，说明 Pod 部署、镜像加载、负载均衡及端口暴露整条链路已全部**完美通关**！

### 清理测试资源或暂停集群

练习完成后，运行以下命令回收资源或暂停环境：

```python
# 1. 删除测试创建的 Service 和 Deployment
kubectl delete service my-nginx-service
kubectl delete deployment my-nginx

# 2. 暂停 Minikube 集群（保留配置与镜像，下次执行 minikube start 可秒级恢复）
minikube stop
```

## 五、 `kubectl` 核心与指令

### kubectl的作用

**`kubectl` 就是你控制整个 Kubernetes 集群的“总遥控器”或“超级终端”。**

无论你是想部署一个新的微服务、查看容器有没有报错、给系统扩容副本，还是重启某个服务，所有的操作指令都是通过 `kubectl` 发送给 K8s 的。

为了让你彻底搞懂它的本质，我们可以从以下 **3 个维度** 来理解：

#### 通俗类比：它就像 Linux 的 `terminal`，或者数据库的 `navicat`

- **没有 `kubectl` 时**：K8s 集群就像是一个藏在后台的高级操作系统或数据库，你根本无法直接与它对话。
- **有了 `kubectl` 时**：你在 CentOS 的终端里敲下一行 `kubectl` 命令，它就会把你的意图（比如“帮我起 2 个 Nginx”）打包成标准请求，发送给 K8s 的大脑（API Server），K8s 收到后就会立刻去执行。

#### `kubectl` 在实际开发/运维中的 4 大核心作用

##### ① 资源的“增删改查”（CRUD 管理）

你之前敲的所有命令，本质上都是在进行资源管理：

- **查**：`kubectl get pods`（查看所有容器）、`kubectl get nodes`（查看服务器节点）。
- **增**：`kubectl apply -f app.yaml`（根据配置文件一键创建应用）。
- **删**：`kubectl delete deployment my-nginx`（删除指定的部署）。

##### ② 线上故障排查（运维排错）

当容器起不来或程序报 500 错误时，`kubectl` 是排错的第一工具：

- **看详细事件**：`kubectl describe pod <pod-name>`（能精准指出是镜像拉不动、内存超限还是端口冲突）。
- **看程序运行日志**：`kubectl logs <pod-name>`（直接查看容器内 Java/Python/Go 应用输出的日志）。

##### ③ 动态扩缩容与滚动更新（极速运维）

无需修改代码，一条指令就能搞定高并发流量：

- **扩容**：`kubectl scale deployment my-nginx --replicas=5`（1 秒钟内把副本从 2 个扩到 5 个）。
- **滚动更新**：`kubectl set image deployment/my-nginx nginx=nginx:1.26`（零停机时间平滑升级应用版本）。

##### ④ 极速生成 YAML 模版（开挂工具）

利用 `--dry-run=client -o yaml` 参数，它能帮你直接自动生成 100% 语法正确的 YAML 标准模版，完全不需要手敲。

`kubectl` 的语法结构非常统一，几乎所有命令都遵循这个公式：

$$\text{kubectl } [\text{动作 Action}] \ [\text{资源类型 Resource}] \ [\text{资源名称 Name}] \ [\text{可选参数 Flags}]$$

在日常开发与运维中，你 90% 的时间只需要用到以下 **3 大类核心指令**：

### 1. 基础查询类

查看集群里面有什么，用来实时掌握 Pod、Service、Deployment 等资源的状态。

| **命令**                 | **作用**             | **实用场景 / 常用参数**                      |
| ------------------------ | -------------------- | -------------------------------------------- |
| **`kubectl get nodes`**  | 查看集群节点状态     | 检查 Master / Worker 节点是否 `Ready`        |
| **`kubectl get pods`**   | 查看所有运行的 Pod   | 加 `-o wide` 可额外查看 Pod 的 IP 和所在节点 |
| **`kubectl get svc`**    | 查看 Service 状态    | 快速获取 NodePort 暴露的外部映射端口         |
| **`kubectl get deploy`** | 查看 Deployment 状态 | 检查副本数（DESIRED / READY）是否符合预期    |
| **`kubectl get all`**    | 一键查看当前所有资源 | 快速概览当前命名空间下的所有组件             |

### 2. 核心排错路线

当 Pod 状态出现 `ImagePullBackOff`、`CrashLoopBackOff` 或 `Pending` 时，按顺序执行这三条命令，99% 的问题都能精准定位：

```python
# 斧头 1：看 Pod 全局分布与 IP（初步看状态）
kubectl get pods -o wide

# 斧头 2：看 Pod 详细事件 Events（排错神器！）
kubectl describe pod <pod-name>
# 💡 提示：重点看输出结果最底部的 "Events" 区域！
# 镜像拉不动、节点内存不够、挂载失败等，这里全都有明确报错提示。

# 斧头 3：看容器内部程序的真实日志输出（代码/应用报错）
kubectl logs <pod-name>
# 如果 Pod 已经 Running 但接口报 500，或者 Java/Python 抛了空指针，用这个看程序 Console 日志。
```

### 3. 极速生成 YAML 骨架

不需要手写 YAML 语法，直接通过 `--dry-run=client -o yaml` 演习并导出标准模板：

```python
# 1. 生成 Deployment 的标准 YAML 骨架
kubectl create deployment my-app --image=nginx:1.25 --dry-run=client -o yaml > deployment.yaml

# 2. 生成 Service 的标准 YAML 骨架
kubectl expose deployment my-app --port=80 --type=NodePort --dry-run=client -o yaml > service.yaml
```

### 🎯 `kubectl` 阶段实操

在进入 YAML 学习前，你可以直接在你的 CentOS 终端里敲下面这条命令，感受一下 `kubectl` 自动为你生成配置文件的快乐：

```python
kubectl create deployment demo-yaml --image=nginx:1.25 --dry-run=client -o yaml
```

## 六、 学习如何用 Kubernetes YAML 配置文件

### 1. YAML 的 4 大“顶层核心结构”（骨架）

不管是配置简单的 Pod，还是复杂的 Deployment、Service，所有 K8s 的 YAML 配置文件，**都由以下 4 个固定顶层字段组成**：

YAML

```python
apiVersion: apps/v1       # 1. API 版本（告诉 K8s 用哪个版本的规则来解析这个文件）
kind: Deployment          # 2. 资源类型（声明你要创建什么：Deployment / Service / Pod / ConfigMap）
metadata:                 # 3. 元数据（给这个资源起的名字、打的标签 Label）
  name: my-nginx
  labels:
    app: nginx
spec:                     # 4. 详细规格 Specification（核心！这里定义资源的具体期望状态）
  replicas: 2             # 期望副本数
  ...
```

> **💡 记忆口诀**：**“API 种类加元数据，详细规格在 spec”**（`apiVersion`, `kind`, `metadata`, `spec`）。

### 2. 核心语法规则

YAML 语法极其优雅，但也非常严格：

1. **严格缩进**：只能使用 **空格（Space）** 进行缩进，**严禁使用 Tab 键**（Tab 会直接报错导致解析失败）。
2. **大小写敏感**：`Deployment` 的 `D` 大写，字段名 `metadata` 全小写，不能乱改。
3. **冒号后必须加空格**：写 `name: my-nginx` 时，**`:` 后面必须空一格**！
4. **横杠 `-` 表示列表数组**：如果一个字段下面有多个项（比如一个 Pod 里有多个容器，或者定义多个端口），用 `-` 开头表示列表。

### 3. 拆解一个标准的 Deployment YAML

我们直接看一个最通用的 `nginx-deployment.yaml`，每一行都加上了详细注解：

YAML

```python
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-nginx-deploy    # Deployment 的名称
  labels:
    app: nginx             # Deployment 自己的标签
spec:
  replicas: 2              # 1. 保持 2 个 Pod 副本
  selector:
    matchLabels:
      app: nginx-pod       # 2. 标签选择器：用来管理带有 app=nginx-pod 标签的 Pod
  template:                # 3. Pod 模板（这里定义每个 Pod 内部长什么样）
    metadata:
      labels:
        app: nginx-pod     # Pod 的标签（必须和上面的 matchLabels 对应！）
    spec:
      containers:          # 4. 容器配置列表
      - name: nginx-container
        image: nginx:1.25  # 容器使用的镜像
        ports:
        - containerPort: 80 # 容器内部监听的端口
```

### 4. 将 Service 拼接到同一个 YAML 文件中

在 K8s 中，我们可以用 **`---`（三个横杠）** 将多个资源的 YAML 定义写在同一个文件里。

比如，我们将 **Deployment（部署应用）** 和 **Service（对外暴露端口）** 合二为一，创建一个 `app.yaml`：

YAML

```python
# ------------------ 1. 定义 Deployment ------------------
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        ports:
        - containerPort: 80
---
# ------------------ 2. 定义 NodePort Service ------------------
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: NodePort           # 暴露类型为 NodePort
  selector:
    app: my-app            # 关键！Service 通过这个标签识别并绑定上面的 Pod
  ports:
  - port: 80               # Service 自身的集群内部端口
    targetPort: 80         # 转发给容器内部的端口
    nodePort: 30080        # 显式指定宿主机映射端口（范围 30000-32767，不填则随机分配）
```

### 5. 声明式配置的最高频操作命令

有了 YAML 文件后，我们不再手敲 `kubectl create`，而是统一使用 `kubectl apply` 指令：

```python
# 1. 极速生成 YAML 骨架文件（开挂命令）
kubectl create deployment test-app --image=nginx:1.25 --dry-run=client -o yaml > test.yaml

# 2. 应用/更新配置（如果修改了 YAML，重新运行此命令即可实现增量更新或平滑升级）
kubectl apply -f app.yaml

# 3. 查看根据该 YAML 创建的所有资源
kubectl get -f app.yaml

# 4. 一键删除 YAML 文件里定义的所有资源（清理极其干净）
kubectl delete -f app.yaml
```