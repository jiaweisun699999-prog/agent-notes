# Docker总结

## 一、Docker的介绍

### 1、背景故事

在 Docker 出现之前，软件开发和交付一直面临着经典的**环境不一致**难题。

传统软件开发流程中，开发人员在自己的电脑（比如 Mac 或 Windows）上写完代码、测试通过后，提交给运维人员部署到服务器（通常是 Linux）。然而，到了生产环境，程序经常莫名其妙崩掉或者报错。

最著名的扯皮场景就是：

- **开发**：“在我电脑上跑得好好的啊，肯定是你们服务器环境有问题！”
- **运维**：“服务器环境都是标准化的，肯定是你代码有 Bug！”

这种尴尬的核心根源在于：**软件运行不仅依赖代码本身，还高度依赖系统依赖库、环境变量、配置参数、依赖服务版本乃至系统底层内核**。传统部署方式（如直接打个 Zip/Jar 包放到服务器上）只传递了代码，却没有把代码运行的**整个环境**一起传递过去。

### 2、解决的问题

Docker 的出现，本质上颠覆了传统的软件交付模式。它主要解决了以下四大核心痛点：

#### ① 环境一致性（应用与环境解耦）

- **痛点**：开发、测试、生产三套环境配置不一致，导致的“死在生产环境”现象。
- **Docker 的解法**：**“一次构建，到处运行”（Build Once, Run Anywhere）**。Docker 将应用程序及其依赖（代码、运行时环境、依赖库、配置文件等）打包成一个**镜像（Image）**。镜像就像是软件的“完备快照”，在开发机上构建好，扔到任何安装了 Docker Engine 的服务器上运行，效果完全一致。

#### ② 部署繁琐与运维效率低

- **痛点**：部署一个复杂应用（比如 Nginx + Redis + MySQL + Java 应用）需要手动安装各种依赖、调配置，极其繁琐且容易出错，扩容时更是噩梦。
- **Docker 的解法**：通过简单的命令或配置文件（如 `Dockerfile`、`Docker Compose`），秒级拉起整个服务栈，实现了**标准化、自动化部署**，大幅提升交付速度。

#### ③ 资源利用率与隔离性

- **痛点**：

  - **传统物理机/直接部署**：多个应用混跑在同一主机上，容易产生端口冲突、依赖库版本冲突（如应用 A 要 Python 2.7，应用 B 要 Python 3.10），且一个应用崩溃可能拖垮整台机器。
  - **传统虚拟机（VM）**：虽然实现了隔离，但每台虚拟机都要运行一个完整的 OS（操作系统），启动慢（以分钟计）、内存开销大、CPU 损耗明显。

- **Docker 的解法**：基于 Linux 内核的轻量级虚拟化（容器技术）。容器共享宿主机的操作系统内核，**启动达到秒级甚至毫秒级**，资源占用极小（一个容器可仅占几MB或几十MB内存），同时利用 Linux 内核的 `Namespace`（命名空间隔离）和 `Cgroups`（资源限制）实现了应用间良好的隔离。

  我们来做一个直观对比，加深印象：

  | **维度**     | **传统虚拟机 (VM)**          | **Docker 容器 (Container)**            |
  | ------------ | ---------------------------- | -------------------------------------- |
  | **部署粒度** | 操作系统级（包含完整 OS）    | 应用级（仅打包应用及依赖）             |
  | **启动速度** | 分钟级                       | **秒级 / 毫秒级**                      |
  | **资源占用** | 几 GB 到几十 GB 内存，占用大 | **几 MB 到几百 MB 内存，极轻量**       |
  | **性能损耗** | 存在 Hypervisor 虚拟化损耗   | **几乎无损耗（直接运行于宿主机内核）** |
  | **系统密谋** | 单台主机能开几十个 VM        | **单台主机可拉起数百/上千个容器**      |

总结起来，Docker 就像是**软件工业的“标准化集装箱”**。在集装箱发明前，货物形状各异、运输极难标准化；有了集装箱，不管里面装的是服装、电子产品还是水果，统统按标准规格装箱，轮船、火车、卡车都能无缝运输。Docker 把软件和它的环境打包进集装箱，让软件的交付和部署变得前所未有的轻松。

## 二、Docker的核心思想

> **集装箱化：一次构建，到处运行（Build Once, Run Anywhere）**

如果把它拆解开来，它的核心哲学主要体现在以下三个层面：

### 1. 软件交付的“集装箱”思想（Standardization）

在集装箱发明之前，航运极为低效：不同形状的货物需要用不同方式堆放、搬运和卸载。集装箱发明后，不管里面装的是钢铁、服装还是水果，**外壳规格统一**，吊车、卡车、货轮都能用同一种方式处理。

Docker 把这个概念带到了软件行业：

- **传统模式**：交付的是**代码/安装包**，需要目标服务器去准备 Python、Java、MySQL 等各种环境。
- **Docker 模式**：交付的是**带环境的集装箱（镜像）**。把代码、依赖库、系统配置、运行时环境整体“打爆”封进集装箱，任何安装了 Docker 的地方，直接拉起来就能跑。

### 2. 应用与宿主环境的解耦（Isolation & Decoupling）

Docker 倡导“应用级隔离”：

- 每一个容器都是一个独立、自治的微型环境。
- 应用与应用之间相互隔离（隔离网络、进程、文件系统），不会因为应用 A 的依赖升级导致应用 B 崩溃。
- 应用与宿主机解耦，宿主机只需要提供 Docker Engine 运行时，不再需要为特定应用去配置复杂的系统环境。

### 3. 一切皆不可变与声明式（Immutable Infrastructure）

Docker 鼓励**不可变基础设施**的思想：

- **镜像（Image）是只读的、不可变的**。开发环境打出的镜像，测试环境和生产环境用的是同一个。
- 如果需要修改配置或升级代码，**不要去容器里手动修改**，而是修改配置文件（如 `Dockerfile`），重新构建一个新的镜像并替换运行。这彻底杜绝了生产环境“人肉配置”带来的不可控隐患。

简单来说，Docker 的核心思想就是：**把应用及其运行土壤合二为一，标准打包，秒级拉起，随时替换。**

## 三、Docker的Linux安装

在 Linux 系统上安装 Docker，最推荐也是生产环境最常用的方式是使用 **Docker 官方源（Docker Official Repository）** 进行安装。这样可以确保安装到最新稳定版，并且后续方便用包管理器升级。

下面以常见的 **Ubuntu/Debian** 和 **CentOS/RHEL** 为例，梳理标准的安装流程。

### 1、 Ubuntu / Debian 系统安装

**1.清理旧版本:**防止旧版本冲突.

如果系统之前安装过旧版本的 Docker（如 `docker`、`docker-engine` 或 `docker.io`），先运行清理命令：

```python
sudo apt-get remove docker docker-engine docker.io containerd runc
```

**2.更新 APT 包索引并安装依赖:**

更新系统软件包列表，并安装允许 APT 通过 HTTPS 使用镜像仓库的必要工具：

```python
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
```

**3.添加 Docker 官方 GPG 密钥:**

下载并添加 Docker 的官方密钥，确保下载的软件包是安全的：

```python
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

**4.设置 Docker 软件源:**

将 Docker 官方仓库加入 APT 软件源列表中（注意：如果是 Debian 系统，命令中的 `ubuntu` 需替换为 `debian`）：

```python
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

**5.安装 Docker 引擎及常用插件:**

更新包索引并安装 Docker Community Edition (CE)、命令行工具以及 Docker Compose 插件：

```python
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 2、 CentOS / RHEL 系统安装

#### **1.卸载旧版本:**

清理可能存在的旧版本软件包：

```python
sudo yum remove docker \
                docker-client \
                docker-client-latest \
                docker-common \
                docker-latest \
                docker-latest-logrotate \
                docker-logrotate \
                docker-engine
```

#### **2.安装 yum-utils 并添加 Docker Repo:**

安装管理 yum 仓库的工具，并添加官方 yum 源：

安装管理 yum 仓库的工具，并添加国内阿里云 yum 软件源（解决官方源网络超时问题）：

```python
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
```

#### 3.清理缓存并安装 Docker 引擎

刷新包缓存并安装 Docker 社区版核心包及插件：

```python
sudo yum clean all && sudo yum makecache
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 3、 启动与验证（通用步骤）

安装完成后，Docker 服务默认可能未启动或未设置开机自启，需要手动配置：

#### 1. 启动 Docker 并设置开机自启

```python
# 启动 Docker 服务
sudo systemctl start docker

# 设置开机自启
sudo systemctl enable docker

# 查看运行状态（确保状态为 active (running)）
sudo systemctl status docker
```

#### 2. 配置国内镜像加速器（防拉取超时必做步骤）

创建或修改配置，加入国内镜像代理站点：

```python
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://dockerproxy.com",
    "https://docker.1ms.run",
    "https://dytt.site"
  ]
}
EOF

# 重载配置并重启 Docker
sudo systemctl daemon-reload
sudo systemctl restart docker
```

#### 3. 运行 Hello-World 验证安装

执行官方测试镜像：

```python
sudo docker run hello-world
```

如果看到 `Hello from Docker!` 的欢迎信息，说明 Docker 引擎已经成功安装并在后台运行。

### 4、必备的后置优化配置

在实际使用中，有两件事通常需要立即配置：**非 root 用户权限** 和 **镜像加速**。

#### 1. 配置非 root 用户直接使用 Docker

默认情况下，执行 `docker` 命令必须带有 `sudo`。可以通过将当前用户加入 `docker` 用户组来解决：

```python
# 创建 docker 用户组（通常安装时已自动创建）
sudo groupadd docker

# 将当前用户加到 docker 组
sudo usermod -aG docker $USER

# 刷新用户组（或者退出当前 SSH 会话重新登录生效）
newgrp docker
```

之后再运行 `docker ps` 等命令就不再需要加 `sudo` 了。

#### 2. 配置镜像加速器（解决镜像拉取慢的问题）

国内拉取 Docker Hub 官方镜像时有时会出现超时或连接不上的情况。可通过修改配置文件配置镜像加速器：

编辑（或新建）配置文件 `/etc/docker/daemon.json`：

```python
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.m.daocloud.io",
    "https://dockerproxy.com"
  ]
}
EOF
```

配置完成后重启 Docker 服务生效：

```python
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## 四、Docker镜像概念与操作常用命令

### 1、镜像概念

#### ① 什么是镜像？

- **本质定义**：Docker 镜像是一个**特殊的只读文件系统**。它不仅包含应用程序的代码，还包含了程序运行所需的**所有环境**（操作系统内核以上的根文件系统 `rootfs`、依赖库、环境变量、配置文件、工具等）。
- **形象类比**：
  - 类似于操作系统安装时用到的 **ISO 镜像文件** 或 **Ghost 镜像快照**。
  - 类似于面向对象编程中的 **类（Class）**，它本身是静态的、不占运行内存的定义，只有通过实例化（`docker run`）才能变成动态运行的 **容器对象（Instance）**。

#### ② 镜像的核心技术：分层存储（UnionFS 联合文件系统）

镜像最精妙的设计在于它的**分层（Layer）架构**

```python
+---------------------------------------------------+
|               容器可写层 (Container Layer)         |  <-- 可读写 (只存在于运行的容器)
+---------------------------------------------------+
|               应用层 (如 App Code/Jar)             |  <-- 只读镜像层 (Layer N)
+---------------------------------------------------+
|               环境依赖层 (如 Python/Java/Nginx)    |  <-- 只读镜像层 (Layer 2)
+---------------------------------------------------+
|               基础系统层 (如 Ubuntu/Alpine)        |  <-- 只读镜像层 (Layer 1)
+---------------------------------------------------+
```

**分层只读（Read-Only）**：

- 镜像是由一层层文件系统叠加而成的，每一层在构建完成后就成为了**只读层**。
- 例如：底座是一个 Alpine Linux 层，上面叠加一层 Python 运行环境，最上面叠加你的 App 代码层。

**写时复制（Copy-on-Write, CoW）**：

- 当容器启动时，Docker 会在镜像的所有只读层最上方，加上一层薄薄的**可写层（Container Layer）**。
- 如果你需要修改容器里的某个配置文件，Docker 会先从底层的只读镜像层中把这个文件复制到顶层可写层，然后再修改。**底层的只读镜像永远不会被修改**。

**极高的复用性与省空间**：

- 如果你下载了 10 个基于 `ubuntu:22.04` 构建的镜像，本地磁盘上只会有**一份** `ubuntu:22.04` 的基础层存储，这 10 个镜像共享这份基础层！

### 2、操作常用命令

镜像的操作命令主要围绕：**查找、拉取、查看、删除、导出与导入**。

#### ① 查找与拉取镜像

```python
# 1. 搜索远程仓库（如 Docker Hub）中的镜像
docker search nginx

# 2. 从远程仓库拉取镜像到本地
# 语法：docker pull [镜像名]:[标签/版本]
# 不指定 tag 时，默认拉取 latest (最新版)
docker pull nginx:1.25
docker pull redis:alpine
```

#### ② 查看本地镜像

```python
# 1. 列出本地所有镜像
docker images
# 或
docker image ls

# 2. 查看镜像的详细元数据信息（架构、层信息、环境变量等）
docker inspect nginx:latest

# 3. 查看镜像的构建历史层级（能看到每层执行了什么命令，非常实用）
docker history nginx:latest
```

#### ③ 删除镜像

```python
# 1. 删除指定镜像（按 镜像名:标签 或 镜像ID）
docker rmi nginx:1.25
# 或
docker image rm nginx:1.25

# 2. 强制删除镜像（即使有基于该镜像的停止容器）
docker rmi -f nginx:latest

# 3. 清理所有“悬空镜像”（Dangling Images，即无标签的虚悬镜像 `<none>:<none>`）
docker image prune

# 4. 清理所有未使用的镜像
docker image prune -a
```

#### ④ 镜像构建与打包修改

```python
# 1. 将修改后的容器保存为一个全新的镜像（手动提交，类似 Git commit）
# 语法：docker commit [容器ID/名称] [新镜像名]:[Tag]
docker commit -m "installed vim" -a "developer" my-nginx my-nginx:v1.0

# 2. 为现有镜像打上一个新的标签（别名）
# 语法：docker tag [原镜像]:[原Tag] [新镜像]:[新Tag]
docker tag nginx:latest myregistry.com/web/nginx:v1
```

#### ⑤ 镜像的导入与导出（无网络/离线环境迁移）

在无法连接公网的内网服务器环境，通常用 `save` / `load` 迁移镜像：

```python
# 1. 将本地镜像导出/打包为 tar 文件（宿主机操作）
# -o 或 > 指定输出路径
docker save -o nginx-latest.tar nginx:latest

# 2. 在另一台服务器上从 tar 文件导入镜像
docker load -i nginx-latest.tar
```

## 五、Docker容器

### 1、容器概念

#### ① 什么是容器？

- **直观类比**：如果把 **镜像（Image）** 比作软件的**安装程序（或类/Class）**，那么 **容器（Container）** 就是运行起来的**软件实例（或对象/Instance）**。
- **本质定义**：容器是一个**轻量级、可独立运行的隔离进程集合**。它包含了运行应用所需的所有要素：代码、运行时环境、系统工具、依赖库和配置。

#### ② 容器的四大核心特性

```python
+-------------------------------------------------------+
|                   宿主机 Kernel                        |
+-------------------------------------------------------+
       |                                      |
       v                                      v
+-----------------------+              +-----------------------+
|   容器 A (Web App)    |              |     容器 B (Redis)    |
| - Namespace (隔离)    |              | - Namespace (隔离)    |
| - Cgroups (限流)      |   完全隔离     | - Cgroups (限流)      |
| - 可写层 (读写离)      | <---------->  | - 可写层 (读写隔离)    |
+-----------------------+              +-----------------------+
```

**共享内核，极轻极快**：容器没有自己的 OS 内核，而是直接复用宿主机的 Linux 内核，因此启动只需**毫秒/秒级**，内存开销极小。

**底层隔离机制**：

- **Namespace（命名空间）**：实现**视图隔离**（包括进程 PID、网络 Network、挂载点 Mount、用户 User 等）。容器看自己就像一台独立的 Linux 系统。
- **Cgroups（控制组）**：实现**资源限制**（CPU、内存、磁盘 I/O 等），防止某个容器占满物理机资源。

**分层存储与“可写层”（Container Layer）**：

- 镜像由多层**只读层（Read-Only Layers）** 叠加而成。
- 容器在镜像之上添加了一个薄薄的**可写层（Read-Write Layer）**。
- 容器内部发生的所有文件写/改操作，都只作用在这个可写层（联合文件系统 Copy-on-Write 机制），**绝不会破坏底层的只读镜像**。容器被销毁时，可写层中的数据默认也会随之丢失（除非挂载了数据卷 Volume）。

### 2、操作常用命令

为了方便记忆和检索，我们按**生命周期**把命令划分为四类：

#### ① 创建与生命周期管理

```python
# 1. 创建并启动容器 (最核心命令)
# -d: 后台运行 (Detached)
# -p: 端口映射 (宿主机端口:容器端口)
# --name: 指定容器名称
# -v: 挂载数据卷 (宿主机路径:容器路径)
# -e: 设置环境变量
docker run -d -p 8080:80 --name my-nginx nginx:latest

# 2. 启动 / 停止 / 重启 已存在的容器
docker start <容器名或ID>
docker stop <容器名或ID>      # 优雅停止 (发送 SIGTERM，等待超时后 SIGKILL)
docker kill <容器名或ID>      # 强制停止 (立即发送 SIGKILL)
docker restart <容器名或ID>

# 3. 暂停 / 恢复 容器进程
docker pause <容器名或ID>
docker unpause <容器名或ID>
```

#### ② 查看与状态诊断

```python
# 1. 查看正在运行的容器
docker ps

# 2. 查看所有容器（包括已停止的）
docker ps -a

# 3. 查看容器日志 (非常高频)
# -f: 持续追踪日志 (follow)
# --tail 100: 只看最后 100 行
# -t: 显示时间戳
docker logs -f --tail 100 <容器名或ID>

# 4. 查看容器内部运行的进程
docker top <容器名或ID>

# 5. 查看容器详细元数据信息 (JSON 格式：IP、网络、挂载点等)
docker inspect <容器名或ID>

# 6. 查看容器资源占用情况 (CPU、内存、网络IO、磁盘IO)
docker stats <容器名或ID>
```

#### ③ 交互与文件传输

```python
# 1. 进入正在运行的容器 (最常用)
# -i: 保持标准输入打开
# -t: 分配伪终端 (TTY)
docker exec -it <容器名或ID> /bin/bash   # 如果容器无 bash，可用 /bin/sh

# 2. 宿主机与容器之间复制文件
# 宿主机 -> 容器
docker cp /local/path/file.txt <容器名或ID>:/container/path/
# 容器 -> 宿主机
docker cp <容器名或ID>:/container/path/file.txt /local/path/
```

#### ④ 删除与清理

```python
# 1. 删除已停止的容器
docker rm <容器名或ID>

# 2. 强制删除运行中的容器 (慎用)
docker rm -f <容器名或ID>

# 3. 一键删除所有已经停止的容器
docker container prune

# 4. 删除所有未被使用的资源（停止的容器、未使用的网络、悬空镜像）
docker system prune -a
```

## 六、Docker变量

### 1、设置变量作用

在云原生和容器化架构中，**环境变量（Environment Variables）** 是实现应用配置与代码解耦的核心手段。

在 Docker 中设置环境变量，遵循了现代软件开发的 **12-Factor App** 原则（即“将配置与代码严格分离”）。它的主要作用有以下几点：

1. **实现“一次构建，到处运行”**
   - 如果将数据库 IP、密码或端口硬编码（Hardcode）在镜像或代码里，不同环境（开发、测试、生产）就需要打不同的镜像。
   - **使用环境变量**：同一个镜像，在开发环境传入 `DB_HOST=192.168.1.10`，在生产环境传入 `DB_HOST=prod-db.internal`，无需重新构建镜像。
2. **控制容器的初始化逻辑**
   - 很多主流开源镜像（如 MySQL、PostgreSQL、Redis、Nginx 等）靠环境变量来驱动初始化。
   - 例如启动 MySQL 容器时，必须通过环境变量指定 `MYSQL_ROOT_PASSWORD`，容器启动脚本会自动为你设置 root 密码并创建默认数据库。
3. **保护敏感信息**
   - 避免把账号密码、API Token、秘钥等写死在 `Dockerfile` 或源码库（Git）中。启动容器时动态注入环境变量，安全性更高。
4. **灵活切换应用运行模式**
   - 例如 Java/Spring Boot 应用，可以通过注入 `SPRING_PROFILES_ACTIVE=prod` 或 `dev` 来动态切换加载哪套配置文件。

### 2、操作命令

环境变量的设置和使用分为两个阶段：**容器运行时（Runtime）注入** 和 **镜像构建时（Buildtime）预设**。

#### ① 容器运行时注入（最常用：`docker run`）

这是运维和部署时最高频的使用方式：

```python
# 1. 使用 -e 或 --env 传递单个/多个环境变量
# 示例：启动 MySQL 并设置 root 密码与默认数据库
docker run -d \
  --name my-mysql \
  -e MYSQL_ROOT_PASSWORD=my-secret-pw \
  -e MYSQL_DATABASE=app_db \
  -p 3306:3306 \
  mysql:8.0

# 2. 传递宿主机的环境变量（不指定值时，默认读取宿主机同名变量）
export MY_VAR="hello"
docker run -e MY_VAR ubuntu env

# 3. 通过文件批量注入 (--env-file)
# 当环境变量非常多时，可以写在一个 .env 文件里 (内容格式为 KEY=VALUE)
docker run -d \
  --name my-app \
  --env-file ./.env \
  my-app:v1.0
```

> **`.env` 文件示例格式：**
>
> Ini, TOML
>
> ```
> DB_HOST=10.0.0.5
> DB_USER=root
> DB_PASS=123456
> LOG_LEVEL=debug
> ```

#### ② 镜像构建时设置（`Dockerfile`）

在编写 `Dockerfile` 时，有两种变量指令，作用域完全不同：

##### A. `ENV`（持久化环境变量）

- **特点**：不仅在**构建过程**中有效，还会**保留到最终镜像中**，容器运行时依然能读取到该变量（也可被 `docker run -e` 覆盖）。

Dockerfile

```python
# Dockerfile 示例
FROM ubuntu:22.04

# 设置环境变量
ENV PATH=/usr/local/nginx/sbin:$PATH \
    APP_ENV=production \
    PORT=8080

EXPOSE $PORT
```

##### B. `ARG`（构建期临时变量）

- **特点**：**仅在镜像构建（`docker build`）阶段有效**，镜像打出来后该变量就消失了，不会带入到最终容器中。常用于指定构建时的版本号、下载地址等。

Dockerfile

```python
# Dockerfile 示例
FROM node:18-alpine

# 定义构建参数（可以给默认值）
ARG VERSION=1.0.0

RUN echo "Building version $VERSION..."
```

- **构建时动态传入 `ARG`：**

```python
docker build --build-arg VERSION=2.0.0 -t my-app:2.0 .
```

#### ③ 查看与验证容器内部的环境变量

部署完成后，排查配置问题时常用以下命令验证环境变量是否生效：

```python
# 1. 方式一：进入容器直接运行 env 命令
docker exec -it my-mysql env

# 2. 方式二：通过 docker inspect 查看容器元数据（无需进入容器）
# 过滤输出 Config.Env 节点
docker inspect -f '{{ .Config.Env }}' my-mysql

# 3. 方式三：查看具体某个变量的值
docker exec -it my-mysql echo '$MYSQL_DATABASE'
```

## 七、Docker网络映射

容器默认是一个隔离的沙盒，外界无法直接访问它内部的服务。要让外部（比如浏览器、客户端或其他机器）能够访问到容器里的应用（如 Nginx、MySQL、Spring Boot 等），或者让容器与宿主机之间相互通信，就必须进行**网络映射（Port Mapping & Network Mapping）**。

下面我们把 **“七、Docker 网络映射”** 的概念、工作原理以及常用操作命令完整梳理清楚：

### 1. 网络映射的核心概念

#### ① 为什么需要网络映射？

- **容器隔离性**：每个 Docker 容器都有自己独立的网络命名空间（Net Namespace），拥有独立的 IP 地址（通常是内部私有网段，如 `172.17.0.x`）。
- **局域网/互联网不可达**：容器内部这个 IP 地址只能在**宿主机内部**由 Docker 虚拟网桥访问，外部网络（包括局域网里的其他电脑或互联网）是根本无法直接寻址和连通的。
- **映射的本质**：通过**端口映射（Port Mapping）**，将宿主机（Host）上的某个物理/逻辑端口，与容器（Container）内部的特定端口建立对应映射关系（基于 Linux 内核的 `iptables` DNAT 转发规则）。

#### ② 核心工作原理

```python
[ 外部用户 / 浏览器 ]
          │
          │ 访问 http://宿主机IP:8080
          ▼
┌─────────────────────────────────────────┐
│ 宿主机 (Host System)                    │
│                                         │
│   宿主机端口: 8080                        │
│        │ (iptables NAT 转发)             │
│        ▼                                │
│   [ docker0 虚拟网桥 (172.17.0.1) ]      │
│        │                                │
│        └───────┐                        │
└────────────────┼────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 容器 (Container)                        │
│   容器 IP: 172.17.0.2                   │
│   容器端口: 80 (Nginx/App)               │
└─────────────────────────────────────────┘
```

当外部请求到达`宿主机IP:8080`时，Docker 的 `NAT`（网络地址转换）服务会自动把流量转发到容器内部的`172.17.0.2:80`，实现透明通信。

### 2. 端口映射常用操作命令

端口映射主要通过 `docker run` 命令的 `-p`（指定映射）和 `-P`（随机映射）参数来实现。

#### ① 指定端口映射（最常用：小写 `-p`）

语法格式：`docker run -p [宿主机IP:]宿主机端口:容器端口 [镜像名]`

```python
# 1. 标准映射：将宿主机的 8080 端口映射到容器的 80 端口
docker run -d --name my-web -p 8080:80 nginx:latest

# 2. 多端口映射：一个容器暴露多个端口（如应用端口 + 监控端口）
docker run -d --name my-app -p 8080:8080 -p 9090:9090 my-service:v1

# 3. 指定宿主机绑定 IP（只允许本地 127.0.0.1 访问，增强安全性，常用于数据库/Redis）
docker run -d --name my-redis -p 127.0.0.1:6379:6379 redis:latest

# 4. 指定 UDP 协议端口（默认是 TCP，如果是 DNS 或游戏服务器需要指定 udp）
docker run -d -p 53:53/udp dns-server
```

#### ② 随机端口映射（大写 `-P`）

如果你不关心宿主机使用什么端口，只希望 Docker 自动帮你在宿主机上分配一个未被占用的**高位随机端口**（通常在 32768 ~ 60000 之间），可以使用大写 `-P`。

```python
# 自动将 Dockerfile 中 EXPOSE 声明的所有端口映射到宿主机的随机端口
docker run -d --name test-nginx -P nginx:latest
```

#### ③ 查看端口映射状态

```python
# 1. 查看特定容器的端口映射情况
docker port my-web
# 输出示例：
# 80/tcp -> 0.0.0.0:8080
# 80/tcp -> [::]:8080

# 2. 通过 docker ps 快速查看所有容器的端口映射
docker ps
```

## 八、Docker数据卷

### 1、数据卷的概念

- **本质定义**：数据卷（Volume）是由 Docker 产生并管理的**宿主机目录或文件**，它被“挂载”（Mount）到了容器内部的文件系统中。
- **物理位置**：在 Linux 系统中，默认托管的数据卷通常存在于宿主机的 `/var/lib/docker/volumes/` 目录下。
- **独立性**：数据卷完全**脱离了容器的生命周期**。它的存在独立于容器，容器被删除、停止或重启，数据卷中的数据**绝不会丢失**。

```python
┌───────────────────────────────────────────────────────────┐
│ 宿主机 (Host System)                                      │
│                                                           │
│  物理挂载路径: /var/lib/docker/volumes/my-vol/_data       │
│                            │                              │
│                            │ (目录挂载 / Bind Mount)      │
│                            ▼                              │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 容器 (Container)                                    │  │
│  │   容器内部路径: /var/lib/mysql                        │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

### 2、数据卷解决的问题

数据卷主要解决了 Docker 容器在实际应用中的三大痛点：

1. **数据持久化问题（最核心）**
   - **痛点**：容器默认的可写层是暂时的，容器被删除（`docker rm`）时，所有产生的数据（如数据库记录、日志文件、上传的图片）都会丢失。
   - **解决**：把持久化数据写入数据卷，即使容器删了，重新拉起一个新的容器挂载同一个数据卷，数据完好无损。
2. **宿主机与容器之间的数据共享与实时同步**
   - **痛点**：修改容器内部的配置文件或网站源码，每次都进入容器 `docker exec` 去改极其繁琐。
   - **解决**：将宿主机的开发目录挂载进容器。你在宿主机上用 IDE 修改代码，容器内部**实时生效**，无需重新构建镜像或重启容器。
3. **容器与容器之间的数据共享**
   - **痛点**：多个应用容器需要读取同一份日志、公共静态资源或配置文件。
   - **解决**：多个容器可以同时挂载同一个数据卷，实现容器间的数据实时共享。
4. **解除性能瓶颈**
   - **痛点**：容器可写层依赖写时复制（CoW）的联合文件系统（UnionFS），写入大文件或频繁写磁盘时性能较差。
   - **解决**：数据卷直接读写宿主机原生文件系统，绕过了 UnionFS，性能无损耗。

### 3、数据卷操作命令和使用

Docker 中挂载数据的方式主要有两种：**具名/匿名数据卷（Volume，由 Docker 托管）** 和 **直接目录挂载（Bind Mount，指定宿主机绝对路径）**。

#### ① 数据卷管理基本命令（`docker volume`）

这类命令主要用于管理由 Docker 托管的匿名/具名 Volume：

```python
# 1. 创建一个数据卷
docker volume create my-vol

# 2. 查看所有数据卷
docker volume ls

# 3. 查看某个数据卷的详细信息（可以看到在宿主机的真实物理存储路径）
docker volume inspect my-vol

# 4. 删除未使用的本地数据卷
docker volume prune

# 5. 删除指定数据卷
docker volume rm my-vol
```

#### ② 挂载使用方式一：指定宿主机路径挂载（Bind Mount，最常用！）

直接将宿主机上的**绝对路径**挂载到容器内部。在开发和运维中最推荐这种方式，因为路径清晰可控。

语法格式：`docker run -v <宿主机绝对路径>:<容器内路径>[:ro|rw]`

```python
# 1. 将宿主机的 /data/mysql 目录挂载到 MySQL 容器内
docker run -d \
  --name my-mysql \
  -v /data/mysql:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  mysql:8.0

# 2. 挂载配置文件，并设置为只读 (ro = read-only)
# 容器内应用只能读该文件，无法修改，增强安全性
docker run -d \
  --name my-nginx \
  -p 80:80 \
  -v /opt/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
  -v /opt/nginx/html:/usr/share/nginx/html \
  nginx:latest
```

#### ③ 挂载使用方式二：使用 Docker 托管的具名/匿名数据卷（Volume）

只指定卷名，或者只写容器内路径（不写宿主机路径），由 Docker 自动管理宿主机存放在 `/var/lib/docker/volumes/` 下。

```python
# 1. 具名挂载：指定数据卷名称 my-vol (如果卷不存在，Docker 会自动创建)
docker run -d \
  --name my-nginx \
  -v my-vol:/usr/share/nginx/html \
  nginx

# 2. 匿名挂载：只写容器内路径，不写宿主机路径（Docker 会自动随机生成一串哈希字符串作为卷名）
docker run -d \
  --name my-nginx \
  -v /usr/share/nginx/html \
  nginx
```

#### 💡 核心区分卡片：三者写法对比

在使用 `-v` 参数时，区分这三种挂载方式非常简单，看第一个参数的形式即可：

| **挂载类型**                | **-v 参数示例**                 | **特点与适用场景**                                           |
| --------------------------- | ------------------------------- | ------------------------------------------------------------ |
| Bind Mount（目录挂载）      | `-v /host/path:/container/path` | **以 `/` 开头**。精确控制宿主机路径，适用于挂载配置文件、项目源码、日志目录。 |
| 具名挂载 (Named Volume)     | `-v my-vol:/container/path`     | **只有名字，无斜杠 `/`**。由 Docker 自动托管，适合数据库持久化（如 MySQL、Redis 数据文件）。 |
| 匿名挂载 (Anonymous Volume) | `-v /container/path`            | **只有容器内路径**。Docker 随机生成名，容易产生垃圾碎片，生产环境尽量少用。 |

> ⚠️ **避坑小贴士**：
>
> 如果宿主机挂载的目录是空的，而容器内原路径下有默认文件（如 Nginx 的 html 目录）：
>
> - 使用 **Volume（数据卷）** 挂载时，Docker 会把容器内的默认文件**复制**到宿主机卷中。
> - 使用 **Bind Mount（指定宿主机绝对路径）** 挂载时，宿主机空目录会直接**覆盖**并隐蔽容器内部原有的文件！

## 九、Dokcer网络

### 1、Docker的网络管理背景原因

在 Docker 出现之前或没有独立网络管理功能时，容器通信面临着非常棘手的痛点：

1. **容器 IP 动态漂移问题**
   - 每个容器启动时，Docker 会从默认网段中随机分配一个虚拟 IP 地址（如 `172.17.0.2`）。
   - 一旦容器重启、崩溃或升级，**容器的 IP 地址就会发生变化**。如果在代码里（如 Java 或 Python 配置文件）把数据库 IP 写死为 `172.17.0.2`，容器一重启，服务立刻瘫痪。
2. **默认网桥（`docker0`）缺乏内置 DNS 解析**
   - 默认情况下，所有未指定网络模式的容器都会连到默认的 `docker0` 网桥上。
   - 但默认网桥**不支持通过“容器名”直接域名解析**，容器之间想通信必须手写 IP，极其脆弱。
3. **缺乏隔离与安全控制**
   - 如果所有容器都在一个默认的大网桥下，意味着任何容器都能通过 IP 直接 ping 通其他容器。这在多租户或多服务架构中存在严重的网络安全隐患（比如 Web 前端容器可以直接访问到与它无关的日志处理容器）。

👉 **结论**：我们需要一套标准的**网络管理机制（Docker Network）**

### 2、Docker网络管理配置

Docker 提供了灵活的网络插件机制（CNM - Container Network Model），可以通过命令去**创建、管理和挂载**不同的网络。

#### ① 四大基础网络模式

启动容器时，可以通过 `--network <mode>` 指定使用的网络模式：

| **网络模式**         | **触发命令**                    | **底层实现原理与特点**                                       | **适用场景**                        |
| -------------------- | ------------------------------- | ------------------------------------------------------------ | ----------------------------------- |
| **Bridge (网桥)**    | `--network bridge` （**默认**） | 在宿主机创建虚拟网桥（如 `docker0`），通过 `veth pair` 虚拟网卡对连接容器。容器有独立 IP，通过 NAT 访问外网。 | 90% 的单机容器隔离与通信场景        |
| **Host (主机)**      | `--network host`                | 容器**不隔离网络**，直接共享宿主机的网络命名空间（Net Namespace）、IP 和端口。性能最高，无 NAT 开销，但端口容易冲突。 | 对网络性能要求极高、高并发的服务    |
| **None (无网络)**    | `--network none`                | 为容器创建独立的 Net Namespace，但**不做任何网络配置**（只有 loopback 本地环回口，没有外网网卡）。 | 安全要求极高、离线批处理计算任务    |
| **Container (复用)** | `--network container:NAME`      | 新容器不创建自己的网卡和 IP，而是**直接与已存在的某个容器共享 IP 和端口**。 | 类似 Kubernetes 的 Pod 内多容器协同 |

#### ② 自定义网络（Custom Network - 最推荐的使用方式）

为了解决默认 `docker0` 无法域名解析和缺乏隔离的问题，Docker 允许用户创建自定义网桥：

```python
# 1. 查看当前所有的 Docker 网络
docker network ls

# 2. 创建一个自定义 bridge 网络 (最常用)
docker network create --driver bridge my-net

# 3. 创建网络时显式指定子网网段和网关 (高级用法)
docker network create \
  --driver bridge \
  --subnet 192.168.100.0/24 \
  --gateway 192.168.100.1 \
  custom-net

# 4. 启动容器并加入指定网络
docker run -d --name mysql-db --network my-net -e MYSQL_ROOT_PASSWORD=root mysql:8.0
docker run -d --name web-app --network my-net -p 8080:8080 my-app:v1

# 5. 将一个正在运行的容器连接到某个已有的网络中
docker network connect my-net existing-container

# 6. 断开网络连接与删除网络
docker network disconnect my-net existing-container
docker network rm my-net
```

### 3、Docker网络中的名字

在 Docker 网络体系中，**名字** 是实现服务动态寻址的关键。

- **容器名（Container Name）**：通过 `--name` 显式指定的名称（如 `mysql-db`）。如果未指定，Docker 会随机生成一个（如 `loving_einstein`）。
- **网络名（Network Name）**：通过 `docker network create` 创建的网络标识（如 `my-net`）。
- **核心价值**：在**自定义网络**中，**容器名直接充当了网络中的主机名（Hostname）**。
  - 也就是说，在同一个自定义网络下的 `web-app` 容器里，直接执行 `ping mysql-db` 或在配置文件里写 `jdbc:mysql://mysql-db:3306/db`，系统能自动定位到 MySQL 容器，**彻底抛弃了易变的 IP 地址**！

### 4、DNS机制

Docker 内部有一套非常高效且强大的 **内置嵌入式 DNS 服务器（Embedded DNS Server）**，运行在 `127.0.0.11` 这个特殊 IP 上。

```python
┌─────────────────────────────────────────────────────────────┐
│ 自定义网络 (my-net)                                          │
│                                                             │
│  ┌────────────────────┐            ┌────────────────────┐   │
│  │ 容器: web-app      │            │ 容器: mysql-db     │   │
│  │ (IP: 172.18.0.3)   │            │ (IP: 172.18.0.2)   │   │
│  └────────┬───────────┘            └────────▲───────────┘   │
│           │                                 │               │
│           │ 1. 发起请求: ping mysql-db      │               │
│           ▼                                 │               │
│  ┌──────────────────────────────────────┐   │               │
│  │ Docker 内置 DNS 服务器 (127.0.0.11)  │───┘               │
│  │ 自动解析: mysql-db -> 172.18.0.2     │ 2. 返回解析结果    │
│  └──────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

#### DNS 工作流与机制原理：

1. **自动拦截**：容器内部发出的所有域名解析请求，都会先拦截送到 Docker 内置的 DNS 服务（`127.0.0.11`）。
2. **本地解析**：如果请求的是同一个网络内的**容器名、服务名或别名**，DNS 服务器直接查表，返回对应容器当前的动态 IP。
3. **上游转发**：如果解析的是外部互联网域名（如 `baidu.com`），内置 DNS 会自动将其转发给宿主机配置的外部 DNS（如 `/etc/resolv.conf` 中定义的 `8.8.8.8` 或公网 DNS）。

> ⚠️ **重要规则**：
>
> - **默认网桥 (`docker0`)**：出于历史兼容原因，内置 DNS **不开放** 容器名域名解析服务（除非使用过时的 `--link`）。
> - **自定义网桥 (`Custom Bridge`)**：默认**自动开启**内置 DNS，完美支持基于容器名的解析！**这就是为什么生产环境必须使用自定义网络的原因。**

### 5、别名

有时候，一个容器可能希望用“多个不同的名字”被其他容器访问（例如在服务平滑迁移、读写分离负载均衡或多服务名映射场景）。

Docker 提供了 **网络别名（Network Alias）** 机制，允许你为一个容器在特定的网络中指定一个或多个“网络绰号”。

#### 别名的使用与操作：

通过 `--network-alias` 参数在启动容器时指定：

Bash

```python
# 启动一个 MySQL 容器，属于 my-net 网络，并为其设置别名 db-master 和 db-read
docker run -d \
  --name mysql-prod \
  --network my-net \
  --network-alias db-master \
  --network-alias db-read \
  -e MYSQL_ROOT_PASSWORD=root \
  mysql:8.0
```

#### 别名生效的效果：

在同一个 `my-net` 网络里的其他容器，无论是访问：

- `ping mysql-prod` （通过容器原名）
- `ping db-master` （通过别名 1）
- `ping db-read` （通过别名 2）

**全都能够成功解析并访问到同一个数据库容器！**

#### 💡 别名高级玩法：简易 DNS 轮询负载均衡

如果把同一个网络别名分配给**多个不同的容器**：

Bash

```python
# 启动两个 Web 节点，都赋予相同的别名 web-cluster
docker run -d --name web1 --network my-net --network-alias web-cluster my-web:v1
docker run -d --name web2 --network my-net --network-alias web-cluster my-web:v1
```

当其他容器访问 `http://web-cluster` 时，Docker 内置 DNS 会以轮询（Round-Robin）的方式交替返回 `web1` 和 `web2` 的 IP，实现最轻量级的内部负载均衡！

## 十、Docker日志

### 1. Docker 日志的核心机制

#### ① 标准输出重定向（Standard Streams）

Docker 的日志采集机制非常简单而优雅：

- 容器内部运行的应用（如 Nginx、Java、Python、Node.js 等），只要把日志打印到 **标准输出（`stdout`）** 或 **标准错误（`stderr`）**，Docker Engine 就会自动捕捉这些输出。

- Docker 会将捕捉到的日志以 **JSON 格式** 写入宿主机的特定文件中，路径通常为：

  `/var/lib/docker/containers/<容器ID>/<容器ID>-json.log`

> ⚠️ **避坑提醒**：如果你的应用把日志写到了容器内部的具体文件里（例如 `/app/logs/app.log`），`docker logs` 命令是**看不起/看不到**这些日志的！必须通过挂载数据卷（Volume）或配置日志收集器来处理。

#### ② 日志驱动（Logging Drivers）

Docker 默认使用 `json-file` 驱动将日志存为本地 JSON 文件，但它还支持将日志直接投递到各种集中式日志系统：

| **日志驱动 (Driver)**    | **特点与适用场景**                                           |
| ------------------------ | ------------------------------------------------------------ |
| **`json-file`**          | **默认驱动**。将日志以 JSON 形式写在宿主机本地磁盘，配合 `docker logs` 查看。 |
| **`journald`**           | 将容器日志发送到宿主机的 Systemd Journal 服务中。            |
| **`syslog`**             | 将日志写入宿主机的 syslog 守护进程，适合传统集中日志收集。   |
| **`fluentd` / `splunk`** | 直接投递到 Fluentd 或 Splunk 等现代日志分析平台（企业级微服务常用）。 |
| **`none`**               | 禁用容器日志记录（节省磁盘）。                               |

### 2. 核心操作命令：`docker logs`

排查线上故障时，`docker logs` 是高频使用的命令。以下是常用组合：

```python
# 1. 查看所有日志（基础用法）
docker logs <容器名或ID>

# 2. 实时持续追踪日志（类似 Linux 的 tail -f，最常用！）
docker logs -f <容器名或ID>

# 3. 仅查看最后 N 行日志（避免上万行日志刷屏）
docker logs --tail 100 <容器名或ID>

# 4. 实时查看最后 100 行日志（极高频诊断组合）
docker logs -f --tail 100 <容器名或ID>

# 5. 显示日志的时间戳（-t 或 --timestamps）
docker logs -t --tail 50 <容器名或ID>

# 6. 按时间范围筛选日志（--since / --until）
# 查看最近 30 分钟内的日志
docker logs --since 30m <容器名或ID>
# 查看指定时间之后的日志
docker logs --since "2026-07-28T09:00:00" <容器名或ID>
```

### 3. 生产环境必配：日志清理与限制策略

如果不加限制，默认的 `json-file` 驱动会无限增长，最终**填满宿主机磁盘**，导致整台服务器崩溃。

在生产环境中，有两种方式配置日志大小限制（Log Rotation）：

#### 方式一：全局配置（推荐）

修改 Docker 守护进程配置文件 `/etc/docker/daemon.json`，对所有新创建的容器生效：

JSON

```python
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
```

- `max-size`: 单个日志文件最大 100MB。
- `max-file`: 最多保留 3 个日志文件（超过会自动滚动轮转更新，旧日志被覆盖）。

配置完成后重启 Docker：

```python
sudo systemctl daemon-reload
sudo systemctl restart docker
```

#### 方式二：针对单个容器配置

在创建容器时，通过 `--log-opt` 参数显式指定：

```python
docker run -d \
  --name my-app \
  --log-opt max-size=50m \
  --log-opt max-file=5 \
  p 8080:8080 \
  my-app:v1
```

### 4. 容器日志管理的最佳实践总结

1. **应用日志打到 stdout/stderr**：编写应用代码或配置日志框架（如 Logback、Log4j2）时，控制台输出务必保留。
2. **业务日志文件挂载处理**：如果应用必须生成结构化的本地文件日志（如 `/var/log/app/`），请使用 **Volume 挂载到宿主机**，再配合 Filebeat / Logstash 抽取到 ELK（Elasticsearch, Logstash, Kibana）平台。
3. **设置单文件上限**：服务器部署后第一时间配置 `daemon.json` 的 `max-size`，防止磁盘暴满。

## 十一、Docker容器资源限制

在生产环境中，**容器资源限制（Resource Limits）** 是非常核心的一环。

如果不对容器的资源进行限制，某个容器一旦发生内存泄漏（OOM）或 CPU 死循环，就会疯狂侵占物理机的硬件资源，导致宿主机上其他容器甚至宿主机系统本身卡死崩溃。

Docker 底层主要是基于 Linux 内核的 **Cgroups（Control Groups，控制组）** 技术来实现对容器 CPU、内存、磁盘 I/O 等资源的精细化限制。

下面我们把 **Docker 容器资源限制** 的核心参数、使用命令和实战场景完整梳理清楚：

### 1. 内存资源限制（Memory Limits）

内存限制是最常用、也是优先级最高的配置，能有效防止单一容器把宿主机内存抽干导致系统触发 `OOM Killer`。

#### 核心配置参数

| **参数**               | **含义**                     | **作用与解释**                                               |
| ---------------------- | ---------------------------- | ------------------------------------------------------------ |
| `-m` 或 `--memory`     | **硬限制内存**               | 容器能使用的最大内存上限（如 `512m`、`2g`）。如果容器使用的内存超过此值，**容器会被 OOM Kill 强行杀死**。 |
| `--memory-swap`        | **内存 + Swap 交换分区总量** | 容器可使用的（物理内存 + Swap 分区）的总和。                 |
| `--memory-reservation` | **软限制内存**               | 弹性预留内存（如 `256m`）。只有当宿主机内存紧张时，Docker 才会尝试把容器内存压回这个值以下。 |
| `--oom-kill-disable`   | **禁用 OOM 杀进程**          | 物理内存不足时，禁止系统杀死该容器（**慎用**，必须配合 `-m` 使用，防止挤爆宿主机）。 |

#### 限制规则计算公式（关于 `--memory-swap`）

- `docker run -m 512m`：未指定 swap，默认 swap 为内存的 2 倍。即物理内存 max `512MB`，Swap max `512MB`，总共可使用 `1GB`。
- `docker run -m 512m --memory-swap=1g`：物理内存 max `512MB`，Swap = `1G - 512M = 512MB`。
- `docker run -m 512m --memory-swap=512m`：**禁用 Swap**（Swap 为 0）。物理内存严格限制为 `512MB`，超过立即被杀（适合对性能要求高、不希望频繁读写磁盘交换区的服务，如 Redis/JVM 应用）。

#### 高频实战命令

```python
# 限制内存最高 512MB，且关闭 Swap 交换区
docker run -d \
  --name my-java-app \
  -m 512m \
  --memory-swap 512m \
  -p 8080:8080 \
  my-java-app:v1
```

### 2. CPU 资源限制（CPU Limits）

Linux 宿主机默认会把所有 CPU 核心平等分配给所有进程。对 CPU 的限制分为**权重配额限制**和**硬核数限制**。

#### 核心配置参数

| **参数**               | **含义**                   | **作用与解释**                                               |
| ---------------------- | -------------------------- | ------------------------------------------------------------ |
| `--cpus`               | **限制核心数量**（最推荐） | 限制容器可使用的 **CPU 核心数**（支持浮点数，如 `1.5` 表示最多使用 1.5 个 CPU 核心的计算资源）。 |
| `-c` 或 `--cpu-shares` | **CPU 相对权重**           | 默认值为 `1024`。当 CPU 资源充足时，容器可以随便用；当 CPU 忙碌打满时，按权重比例瓜分 CPU。 |
| `--cpuset-cpus`        | **绑定特定 CPU 核心**      | 绑核（如 `0,1` 表示只能运行在第 0 和第 1 个 CPU 核心上）。能大幅减少 CPU 上下文切换开销。 |

#### 高频实战命令

```python
# 1. 限制容器最多只能使用 1.5 个 CPU 核心
docker run -d --name web-service --cpus="1.5" nginx

# 2. 绑核：限制容器只在 0 号和 2 号 CPU 核心上运行
docker run -d --name my-redis --cpuset-cpus="0,2" redis

# 3. 按权重限制（当 CPU 争抢严重时，app1 和 app2 分别按 2:1 比例分配 CPU）
docker run -d --name app1 --cpu-shares 1024 my-app
docker run -d --name app2 --cpu-shares 512 my-app
```

### 3. 动态修改运行中容器的资源限制

如果一个容器已经在运行了，不需要停机重新 `docker run`，可以使用 `docker update` 命令实现**动态调整资源（热修改）**：

```python
# 1. 将正在运行的容器 my-app 的内存上限调整为 1G，CPU 限制调整为 2 核
docker update --memory 1g --memory-swap 1g --cpus 2.0 my-app

# 2. 查看容器当前的实时资源使用率（CPU、内存、网络、磁盘 IO）
docker stats my-app
```

### 4. 生产环境的最佳实践策略

1. **重要服务设置内存上限（`-m`）**：防止单个服务内存泄露导致全局崩溃，尤其是 JVM 应用（如 Java/Spring Boot），容器内存限制必须比 JVM `-Xmx` 稍大一些（留出元空间和 Native 内存空间）。
2. **关闭 Swap 交换区**：性能敏感型服务（如 Redis、MySQL、Elasticsearch），建议设置 `--memory-swap` 等于 `-m` 的值，避免因硬盘 Swap 导致响应延迟暴涨。
3. **关键业务打上 `--cpus` 标签**：保证核心服务在突发流量时有确定的计算资源保障。
4. **利用 `docker stats` 做监控**：通过监控面板查看各容器的资源消耗比，结合日志做针对性扩容或限流。

## 十二、Docker-Compose

### 1、背景介绍

Docker Compose 是单机环境下**多容器自动化编排与管理**的标准利器。

在实际的生产或开发环境中，一个完整的系统很少只有一个容器，往往包含 **Web 前端 + 后端 API 服务 + MySQL 数据库 + Redis 缓存 + Nginx 反向代理** 等多个相互依赖的服务。

在没有 Docker Compose 之前，要部署一个稍微复杂一点的微服务应用，运维或开发人员必须手动在终端里打一堆又长又繁琐的 `docker run` 命令：

```python
# 1. 创建自定义网络
docker network create my-app-net

# 2. 启动 Redis 容器
docker run -d --name redis --network my-app-net redis:latest

# 3. 启动 MySQL 容器 (需要设置密码、挂载卷、网络等)
docker run -d --name mysql --network my-app-net -v /data/mysql:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=root mysql:8.0

# 4. 启动 Java 后端应用 (需要映射端口、配置环境变量、加入网络)
docker run -d --name api-server --network my-app-net -p 8080:8080 -e DB_HOST=mysql my-api:v1

# 5. 启动 Nginx 前端容器...
```

#### 传统命令方式的四大痛点：

1. **步骤繁琐且极易出错**：命令长且参数多，顺序不能错（比如必须先启动数据库，再启动应用）。
2. **缺乏文档化与可追溯性**：命令打完就没了，换一台机器或换个人部署，根本不知道之前加了哪些环境变量、端口和挂载目录。
3. **维护成本极高**：服务停止、重启或销毁时，需要一个一个容器去手动 `docker stop` / `docker rm`。

👉 **Docker Compose 的诞生**，正是为了解决多容器调度的自动化和标准化问题。

### 2、核心思想

Docker Compose 的核心思想可以概括为两点：

> **“以声明式配置文件定义服务栈，用单一工具实现一键式生命周期管理。”**

#### ① 两个核心概念：

- **服务 (Service)**：一个独立的容器应用（如 `web` 服务、`db` 服务）。在 Compose 中，一个服务本质上就是根据特定镜像启动的一个或一组容器。
- **项目 (Project)**：由一组关联的服务组成的完整应用栈（如整个 e-commerce 电子商城系统）。默认以 `docker-compose.yml` 所在的目录名作为项目名称。

#### ② 声明式哲学（Infrastructure as Code - IaC）

- **不写过程，只写结果**：通过一个文本文件（`docker-compose.yml`），将所有容器的镜像、端口、环境变量、网络、数据卷以及依赖启动顺序，以 YAML 格式**声明**出来。
- **代码即环境**：`docker-compose.yml` 文件可以随代码一起提交到 Git 仓库，实现“一份配置，任何机器一键复现整个服务环境”。

💡 `docker-compose.yml` 经典模板示例

YAML

```python
version: '3.8'

# 1. 定义网络
networks:
  app-net:
    driver: bridge

# 2. 定义持久化数据卷
volumes:
  db-data:

# 3. 定义各项服务
services:
  # 服务 1: Mysql 数据库
  db:
    image: mysql:8.0
    container_name: mysql-db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: myapp
    volumes:
      - db-data:/var/lib/mysql
    networks:
      - app-net

  # 服务 2: Web 后端应用
  web:
    build: .                          # 从当前目录的 Dockerfile 构建镜像
    container_name: web-app
    restart: always
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=db                    # 直接使用服务名 'db' 进行网络通信！
      - DB_PASS=root
    depends_on:                       # 显式声明依赖：必须先启动 db，再启动 web
      - db
    networks:
      - app-net
```

### 3、常用命令

在现代 Docker 环境中，Compose 已集成入官方 CLI，推荐使用 `docker compose`（中间为空格），旧版本的 `docker-compose`（带有中划线）同样兼容。

所有命令都应当在包含 `docker-compose.yml` 文件的**根目录**下执行：

### ① 核心启动与销毁命令

```python
# 1. 后台构建并启动整个项目的所有服务 (-d 表示后台运行，最常用！)
docker compose up -d

# 2. 强制重新构建镜像并启动（当修改了 Dockerfile 或代码后使用）
docker compose up -d --build

# 3. 停止并删除所有服务容器、网络以及挂载（数据卷默认保留，非常安全的清理命令）
docker compose down

# 4. 彻底清理：停止并删除容器、网络，以及**连同数据卷卷一并删除**（慎用！）
docker compose down -v
```

### ② 状态查看与日志诊断

```python
# 1. 查看当前 Compose 项目中所有容器的运行状态
docker compose ps

# 2. 实时追踪查看项目下所有容器的聚合日志
docker compose logs -f

# 3. 实时追踪查看指定服务的日志（如只看 web 服务）
docker compose logs -f web

# 4. 查看当前项目下所有容器的资源占用（CPU、内存、网络 IO）
docker compose top
```

### ③ 容器控制与运维交互

```python
# 1. 启动 / 停止 / 重启 项目中的所有服务
docker compose start
docker compose stop
docker compose restart

# 2. 仅重启其中某一个特定服务（不影响其他容器）
docker compose restart web

# 3. 在指定服务容器内执行一次性命令
docker compose exec web /bin/bash

# 4. 检查 YAML 配置文件语法是否有误，并输出解析后的最终配置
docker compose config
```

### 💡 极简对比记忆卡片

| **维度**     | **传统 docker run**              | **docker compose**                      |
| ------------ | -------------------------------- | --------------------------------------- |
| **管理粒度** | 单个容器                         | 整个服务栈（多容器组合）                |
| **配置形式** | 终端命令行长参数                 | 结构化 YAML 配置文件                    |
| **网络建立** | 手动 `network create` + 手动绑定 | **自动创建专属网络**，服务名即 DNS 域名 |
| **一键启动** | 打 N 条命令                      | **一条命令 `docker compose up -d`**     |

## 十三、Docker封装技术

### 1、操作命令

项目封装主要围绕 **编写 Dockerfile** 和使用 **`docker build`** 构建镜像展开。

#### ① `docker build` 核心构建命令

```python
# 1. 基础构建命令
# -t (tag): 指定镜像名称和版本号号 (格式：镜像名:标签)
# . : 表示上下文路径 (Context Path)，告诉 Docker 去哪里寻找 Dockerfile 和项目代码
docker build -t my-app:1.0.0 .

# 2. 显式指定 Dockerfile 文件路径（如果文件名不叫 Dockerfile 或不在当前根目录）
docker build -f /path/to/custom.Dockerfile -t my-app:1.0.0 .

# 3. 禁用构建缓存（当需要强制重新从网络下载依赖或执行命令时使用）
docker build --no-cache -t my-app:1.0.0 .

# 4. 构建时注入临时变量 (ARG)
docker build --build-arg APP_VERSION=1.0.0 -t my-app:1.0.0 .
```

#### ② Dockerfile 关键指令速查（封装骨架）

编写 `Dockerfile` 时，这几个关键指令负责控制封装逻辑：

| **指令**         | **作用与特点**                       | **避坑/最佳实践**                                     |
| ---------------- | ------------------------------------ | ----------------------------------------------------- |
| **`FROM`**       | 指定**基础镜像**（构建的起点）       | 尽量选用轻量化镜像（如 `alpine` 或 `-slim` 版本）。   |
| **`WORKDIR`**    | 设置容器内部的**工作目录**           | 后续的 `RUN`、`COPY`、`CMD` 都在此目录下执行。        |
| **`COPY`**       | 将宿主机本地文件复制进容器           | 推荐用 `COPY` 代替 `ADD`，语义更清晰（仅复制文件）。  |
| **`ADD`**        | 复制文件，**支持解压 tar.gz** 和 URL | 仅在需要自动解压压缩包时使用。                        |
| **`RUN`**        | 构建镜像时执行命令（如安装依赖）     | 多个 `RUN` 命令尽量用 `&&` 合并为一条，减少镜像层数。 |
| **`ENV`**        | 设置**持久环境变量**                 | 镜像运行和容器启动后均有效。                          |
| **`EXPOSE`**     | **声明**容器运行时监听的端口         | 仅起标识作用，真实映射仍需 `docker run -p`。          |
| **`CMD`**        | 容器启动时默认执行的**命令**         | 指定容器入口，可被 `docker run` 末尾参数覆盖。        |
| **`ENTRYPOINT`** | 容器启动的**定型入口**               | 配合 `CMD` 使用，通常指定容器的主进程。               |

### 2. 项目封装落地流程（标准四步法）

要将任何一个项目封装为 Docker 镜像并运行，标准的工程化步骤如下：

```python
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  1. 准备项目文件 │ ──> │ 2. 编写 .dockerignore│ ──> │ 3. 编写 Dockerfile │ ──> │ 4. 构建与验证运行 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

1. **准备项目产物**：编译/打包项目（例如 Java 打出 `.jar` 包，Go 编译出可执行二进制，Python/Node 准备好依赖清单 `requirements.txt` / `package.json`）。
2. **过滤无关文件（`.dockerignore`）**：在项目根目录新建 `.dockerignore` 文件（类似于 `.gitignore`），排除 `.git`、`node_modules`、`target/`、日志文件和敏感配置文件，**避免构建时把大文件传给 Docker 守护进程，大幅加快构建速度**。
3. **编写 Dockerfile**：定义基础环境、工作目录、复制产物、暴露端口和启动命令。
4. **构建镜像并测试运行**：使用 `docker build` 构建，再用 `docker run` 拉起容器测试验证。

### 3. 实战案例：Spring Boot 与 Python Web 项目封装

为了让你更直观地掌握封装，我们看两个最典型的后端应用封装示例：

#### 示例 A：Java (Spring Boot) 项目标准化封装

##### 1. 项目根目录下创建 `.dockerignore`

Plaintext

```python
.git
.idea
target/*.xml
target/classes
*.log
```

##### 2. 编写 `Dockerfile`（多阶段构建，极致瘦身）

多阶段构建（Multi-stage build）是企业级封装的最高效手段，可以在一个 Dockerfile 里完成**代码编译**与**最终运行镜像打包**，生成的镜像极其干净。

Dockerfile

```python
# === 第一阶段：构建阶段 (Build Stage) ===
FROM maven:3.9.6-eclipse-temurin-17-alpine AS builder
WORKDIR /app

# 先单独复制 pom.xml 下载依赖（利用 Docker 缓存层，提高后续构建速度）
COPY pom.xml .
RUN mvn dependency:go-offline

# 复制源码并编译打包 (跳过单元测试)
COPY src ./src
RUN mvn clean package -DskipTests

# === 第二阶段：运行阶段 (Runtime Stage) ===
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# 设置时区为东八区 (上海/中国标准时间)
RUN apk add --no-tzdata tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone

# 从第一阶段构建结果中只提取打好的 jar 包
COPY --from=builder /app/target/*.jar app.jar

# 声明应用端口
EXPOSE 8080

# 设置 JVM 内存参数并启动应用
ENV JAVA_OPTS="-Xms256m -Xmx512m"
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

##### 3. 构建与运行命令

Bash

```python
# 1. 构建镜像
docker build -t my-spring-app:v1.0 .

# 2. 运行容器
docker run -d \
  --name my-app \
  -p 8080:8080 \
  -e JAVA_OPTS="-Xms512m -Xmx1024m" \
  my-spring-app:v1.0
```

#### 示例 B：Python (FastAPI / Flask) 项目封装

##### 1. 编写 `Dockerfile`

Dockerfile

```python
FROM python:3.11-slim

WORKDIR /app

# 设置环境变量：不生成 .pyc 编译文件，并开启流式标准输出
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用程序代码
COPY . .

EXPOSE 8000

# 使用 Gunicorn / Uvicorn 启动微服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. 镜像封装的五大黄金优化准则（镜像瘦身与安全）

1. **选择轻量化基础镜像**：优先选择 `alpine`（仅 5MB 左右）或 `slim` 版本的镜像，避免引入无用的 Linux 工具。
2. **合理利用构建缓存**：改变频率低的操作（如安装依赖 `COPY requirements.txt` / `pom.xml`）写在前面，改动频繁的代码复制写在后面。
3. **清理构建垃圾**：在一个 `RUN` 指令内安装软件包并清除缓存，如 `apt-get update && apt-get install -y xxx && rm -rf /var/lib/apt/lists/*`。
4. **使用非 root 用户运行**：出于安全考虑，生产环境镜像内建议通过 `RUN adduser ...` 创建普通用户，并用 `USER` 指令切换，降低安全风险。
5. **合理配置 `.dockerignore`**：防止大文件（如日志、IDE 缓存、本地构建包）传入 Docker 上下文。

## 十四、1panel软件介绍和安装使用

### 1. 1Panel 软件介绍

#### ① 什么是 1Panel？

**1Panel** 是一款开源的、新一代的 **Linux 运维管理面板**。如果说“宝塔面板（BT Panel）”是上一个时代的代表，那么 1Panel 就是专门为**云原生和容器化时代**设计的现代运维面板。

- **项目定位**：通过 Web 界面，帮助运维和开发人员轻松管理 Linux 服务器、Docker 容器、站点部署、数据库和防火墙等。
- **技术栈**：后端基于 **Go 语言** 编写（高性能、低内存），前端基于 Vue 3，整体结构非常干净轻量。

#### ② 核心优势与特色（为什么推荐使用它？）

1. **天然深度集成 Docker（极简应用商店）**
   - 宝塔面板等传统面板是在宿主机上直接源码/编译安装服务（环境容易搞乱）。
   - **1Panel 内置的应用商店，所有应用（Nginx、MySQL、Redis、WordPress、Halo、OpenWebUI 等）全部以 Docker 容器形式一键拉起**。卸载时直接删容器，宿主机环境始终保持极度干净。
2. **高性能与低资源占用**
   - 因为用 Go 语言编写，1Panel 本身的守护进程平时只占用 **数十 MB 内存**，对小内存 VPS（如 1核 1G/2G）非常友好。
3. **内置安全与防火墙**
   - 支持系统防火墙（端口放行/拒绝）、SSH 密钥管理、安全审计以及一键申请 HTTPS 免费证书（Let's Encrypt / ZeroSSL 自动化续期）。
4. **现代化一键备份与恢复**
   - 支持将网站数据、数据库备份直接同步存储到阿里云 OSS、腾讯云 COS、七牛云、AWS S3 或 MinIO 等远程对象存储。

### 2. 安装与初始配置

1Panel 官方提供了一键安装脚本，会自动帮你检查并安装 Docker 环境。

#### **1.准备环境与命令行安装:**

以 `root` 用户登录 Linux 服务器，根据系统类型选择执行对应的官方一键安装命令：

**Ubuntu / Debian 系统：**

Bash

```python
curl -sSL https://resource.fit2cloud.com/1panel/package/quick_start.sh -o quick_start.sh && sudo bash quick_start.sh
```

**CentOS / RHEL / AlmaLinux 系统：**

Bash

```python
curl -sSL https://resource.fit2cloud.com/1panel/package/quick_start.sh -o quick_start.sh && sudo bash quick_start.sh
```

#### **2.交互式参数设置:**

脚本运行后会在终端弹出交互配置，通常可以按回车使用默认值，或自定义设置：

1. **设置 1Panel 服务端口**：默认 `8088`（或随机高位端口）。
2. **设置安全入口 (Path)**：如 `/1panel`（防止被公网暴力扫描）。
3. **设置管理员账号与密码**。

#### **3.放行安全组/防火墙:**

安装完成后，终端会输出访问地址（如 `http://服务器IP:8088/安全入口`）。

⚠️ **注意**：如果是在阿里云、腾讯云或华为云等云服务器上使用，**务必去云厂商控制台的“安全组”规则中放行对应的端口（如 8088）**，否则外网无法打开页面！

### 3. 核心功能与使用指南

登录进入 1Panel 的 Web 控制台后，常用功能模块主要分为以下四大类：

```python
┌─────────────────────────────────────────────────────────────┐
│ 1Panel 核心功能板块                                         │
├──────────────┬──────────────┬──────────────┬────────────────┤
│ 容器管理      │ 应用商店     │ 网站管理     │ 数据库 & 运维  │
│ - 容器生命周期│ - 一键部署   │ - OpenResty  │ - MySQL/Redis  │
│ - 镜像与网络  │ - Compose编排│ - 域名&HTTPS │ - 防火墙&备份  │
│ - 实时日志/终端│ - 自动配置挂载│ - 反向代理   │ - 计划任务     │
└──────────────┴──────────────┴──────────────┴────────────────┘
```

#### ① 容器管理（可视化的 Docker 终端）

- **图形化管理**：替代命令行中的 `docker ps`、`docker logs`、`docker exec`。
- **一键查看**：在网页上就能直接看到每个容器的 CPU/内存实时占用卡片，随时查看日志、进入容器内部的 Terminal 终端。
- **Compose 图形化**：支持在界面上直接贴入 `docker-compose.yml` 脚本并一键运行。

#### ② 应用商店（一键安装云原生应用）

- 点击“应用商店”，里面涵盖了上百种常用开源软件（MySQL、Redis、PostgreSQL、Nginx/OpenResty、Kafka、Gitea、Halo 博客等）。
- 点击“安装”，填入端口和密码，1Panel 会自动在后台为你生成 Docker Compose 文件、拉取镜像、挂载 Volume 数据卷并启动容器，体验极佳。

#### ③ 网站管理（OpenResty + SSL 证书）

- **反向代理配置**：当你在应用商店装好了网页应用（如 8080 端口），可以通过 1Panel 的“网站”功能，快速绑定你的域名，自动配置 OpenResty（高性能 Nginx 变体）做反向代理。
- **免费 SSL 证书**：支持申请和自动续期 Let's Encrypt 证书，一键开启网站 `https://` 加密。

#### ④ 常用运维命令（后台 1pctl 工具）

在 Linux 宿主机命令行中，1Panel 提供了 `1pctl` 管理工具：

Bash

```python
# 查看 1Panel 服务状态
1pctl status

# 重启 1Panel 服务
1pctl restart

# 重置管理员密码/取消安全入口限制（当忘记密码或入口时使用，非常有用！）
1pctl reset-password
1pctl reset-entrance

# 查看当前的登录地址与端口
1pctl user-info
```

### 4. 总结：Docker 命令行与 1Panel 的关系

- **命令行 (`docker` / `docker compose`)** 是基础：让你理解容器的本质（镜像分层、端口转发、网络隔离、数据挂载）。
- **1Panel 运维面板** 是效率工具：让你在日常开发、个人服务器运维、快速部署服务时，摆脱琐碎命令，实现可视化高效管理。