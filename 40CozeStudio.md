> 📌 **[AI 大模型与云原生全栈知识库](./README.md)** / **40. Coze Studio 一站式 AI Agent 核心引擎与开源开发工具**
> 🏠 [返回主页 README](./README.md) | ⚡ [面试 30 分钟速记](./interview/00_面试冲刺30分钟速记卡片.md) | 💻 [白板手写代码](./interview/08_大厂手写代码与白板编程题.md)

---

# 1\. **Coze Stdio介绍**

## 1.1. **什么是Coze Stdio**

Coze Studio 是字节跳动推出的一站式 AI Agent（智能体）开发工具，以可视化方式简化智能体的创建、调试与部署。它支持零代码/低代码开发模式，集成 Prompt、RAG（检索增强生成）、插件、工作流等核心技术模块，帮助你快速把创意变成可运行的智能应用。它源自字节跳动“Coze 开发平台”的核心引擎开源版本，已广泛服务数万企业和数百万开发者。

Coze Stdio支持功能如下：

![image.png](./images/40CozeStudio_036224f7c1744ed7a249cc08f32cb164_a2b6aa.jpg)

**Coze Stdio核心特点如下：**

**1) 全面的功能模块支持**

支持包括模型服务管理、智能体/应用构建、工作流设计、插件/知识库/数据库管理以及 API 与 Chat SDK 集成等。

**2) 可视化工作流搭建**

通过拖拽节点即可构建复杂业务流程、管理多轮对话、处理多种交互逻辑。

**3) 增强交互能力**

借助知识库、插件与记忆功能（如用户对话历史），提升智能体应对专业问题和上下文记忆的能力。

**Coze Stdio github地址**：[https://github.com/coze-dev/coze-studio/](https://github.com/coze-dev/coze-studio/)

**Coze Stdio 使用文档地址：**

[https://github.com/coze-dev/coze-studio/blob/main/README.zh\_CN.md](https://github.com/coze-dev/coze-studio/blob/main/README.zh_CN.md)

## 1.2. **Coze Stdio 安装部署**

Coze Stdio 后端采用 Golang，前端由 React + TypeScript 构建，整体基于微服务架构，遵循领域驱动设计（DDD），具备高性能、易扩展、易二次开发特性。

安装Coze Stdio需要基于Docker且要求节点CPU >2Core 、RAM >4GB。用户可以在Window中安装Docker Desktop 安装Docker并部署Coze Stdio，也可以就Linux安装Docker并部署Coze Stdio，这里基于Linux安装Docker部署Coze Stdio，可以按照如下步骤部署Coze Stdio。

**1) 在linux中准备docker环境**

这里默认用户已经安装好了Linux系统，在node2安装docker。获取docker repo文件

```python
wget -O /etc/yum.repos.d/docker-ce.repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
```

查看docker可以安装的版本：

```python
yum list docker-ce.x86_64 --showduplicates | sort -r
```

安装docker:这里指定docker版本为20.10.9版本

```python
yum -y install docker-ce-20.10.9-3.el7
```

如果安装过程中报错:

```python
Error: Package: 3:docker-ce-20.10.9-3.el7.x86_64 (docker-ce-stable)
           Requires: container-selinux >= 2:2.74
Error: Package: docker-ce-rootless-extras-20.10.9-3.el7.x86_64 (docker-ce-stable)
           Requires: fuse-overlayfs >= 0.7
Error: Package: docker-ce-rootless-extras-20.10.9-3.el7.x86_64 (docker-ce-stable)
           Requires: slirp4netns >= 0.4
Error: Package: containerd.io-1.4.9-3.1.el7.x86_64 (docker-ce-stable)
```

缺少一些依赖，解决方式：在/etc/yum.repos.d/docker-ce.repo开头追加如下内容:

```python
[centos-extras]
name=Centos extras - $basearch
baseurl=http://mirror.centos.org/centos/7/extras/x86_64
enabled=1
gpgcheck=0
```

然后执行安装命令：

```python
yum -y install slirp4netns fuse-overlayfs container-selinux
```

执行完以上之后，再次执行yum -y install docker-ce-20.10.9-3.el7安装docker即可。

设置docker 开机启动，并启动docker：

```python
systemctl enable docker
systemctl start docker
```

查看docker版本

```python
docker version
```

修改cgroup方式，并重启docker。

```python
vim /etc/docker/daemon.json

{
        "exec-opts": ["native.cgroupdriver=systemd"],
        "registry-mirrors":[
          "https://docker.m.daocloud.io",
          "https://docker.rainbond.cc",
          "https://docker.lmirror.top",
          "https://docker-0.unsee.tech",
          "https://docker.hlmirror.com"
       ]
}

#重启docker
systemctl restart docker
```

**2) 下载Coze Stdio源码并解压**

Coze Stdio源码下载地址：[https://github.com/coze-dev/coze-studio/](https://github.com/coze-dev/coze-studio/) ，这里下载“coze-studio-0.2.2.tar.gz”版本，下载完成后上传到 Linux节点并解压。

```python
[root@node2 ~]# mkdir -p /software/coze && cd /software/coze

#将 Coze Stdio安装包上传到 /software/coze目录下并解压
[root@node2 coze]# tar -zxvf ./coze-studio-0.2.2.tar.gz 
```

**3) 配置模型**

Coze Studio 是基于大语言模型的 AI 应用开发平台，首次部署并启动 Coze Studio 开源版之前，你需要先在 Coze Studio 项目里配置模型服务，否则创建智能体或者工作流时，无法正常选择模型。本文档以Deepseek模型为例，演示如何为Coze Stdio配置模型服务。如果你需要配置其他模型参考：[https://github.com/coze-dev/coze-studio/wiki/3.-%E6%A8%A1%E5%9E%8B%E9%85%8D%E7%BD%AE](https://github.com/coze-dev/coze-studio/wiki/3.-%E6%A8%A1%E5%9E%8B%E9%85%8D%E7%BD%AE)

```python
#配置deepseek模型
[root@node2 ~]# cd /software/coze/coze-studio-0.2.2/backend/conf/model/template

#将model_template_deepseek.yaml复制到 cd $COZE_STDIO_HOME/backend/conf/model/
[root@node2 template]# cp ./model_template_deepseek.yaml  ../

#修改 model_template_deepseek.yaml
[root@node2 template]# cd ..
[root@node2 template]# vim model_template_deepseek.yaml 
```

注意：所有模型服务的模板文件均位于 /backend/conf/model/template，你需要拷贝至 /backend/conf/model 后修改，重启服务后生效。model\_template\_deepseek.yaml配置内容如下：

![image.png](./images/40CozeStudio_151dbd486781425488184a2bfdc982bc_41ff8e.jpg)

![image.png](./images/40CozeStudio_0b55fb2bc1b64913b5bf6837eec27df9_ff1004.jpg)

在 model\_template\_deepseek.yaml中配置id、meta.capability.function\_call、meta.conn\_config.api\_key、meta.conn\_config.model，三者解释如下：

* id：Coze Studio 中的模型 ID，由开发者自行定义，必须是非 0 的整数，且全局唯一。模型上线后请勿修改模型 id。
* meta.capability.function\_call：是否开启Function Call功能，如果模型支持Function Call，可以设置为true。
* meta.conn\_config.api\_key：模型服务的 API Key。
* meta.conn\_config.model：模型服务的 Model name。

**4) 部署并启动服务**

首次部署并启动 Coze Studio 需要拉取镜像、构建本地镜像，可能耗时较久，请耐心等待。如果看到提示 "Container coze-server Started"，表示 Coze Studio 服务已成功启动。在部署和启动Coze Stdio服务过程中出现问题可以参考：[https://github.com/coze-dev/coze-studio/wiki/9.-%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98](https://github.com/coze-dev/coze-studio/wiki/9.-%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)

```python
# 启动服务
[root@node2 ~]# cd /software/coze/coze-studio-0.2.2/docker/
[root@node2 docker]# cp .env.example .env 
[root@node2 docker]# docker compose up -d
```

备注：通过如下命令将 docker的所有Coze Stdio相关image打包到“all\_coze\_stdio\_images.tar”中：

```python
docker save -o all_coze_stdio_images.tar bitnami/redis:8.0 opencoze/opencoze:latest minio/minio:RELEASE.2025-06-13T11-33-47Z
-cpuv1 bitnami/etcd:3.5 bitnami/elasticsearch:8.18.0 milvusdb/milvus:v2.5.10 mysql:8.4.5 nsqio/nsq:v1.2.1
```

在目标计算机上，打开docker，使用如下命令将all_coze_stdio_images.tar导入到目标计算机中：

```python
docker load -i all_coze_stdio_images.tar
```

**5) 登录访问**

启动服务后，通过浏览器访问 [http://ip:8888/](http://ip:8888/) 即可打开 Coze Studio，输入邮箱和密码，首次点击注册后自动完成登录，后续登录可以输入邮箱和密码后直接点击“登录”。

![image.png](./images/40CozeStudio_e5f66adfe5ff4e6099e9a2d0d7656310_0c953e.jpg)

# 2\. **VMware与虚拟机操作**

## 2.1. **VMware及Centos7安装**

### **2.1.1. 安装VMware并激活**

VMware Workstation 是一系列桌面 Hypervisor 产品，允许用户运行虚拟机，后续我们基于VMware Workstation创建Centos系统搭建HDFS集群。

双击“VMware-workstation-full-16.0.0-16894299.exe”安装包即可安装VMware Workstaion。

![image.png](./images/40CozeStudio_6bd96a8106f0436081669ad16e040f94_b3e253.jpg)

![image.png](./images/40CozeStudio_32dc0ad1cd90437b89556bd2ff614632_7a984a.jpg)

![image.png](./images/40CozeStudio_e9c799eadd544d3b961be729a1b4edce_48a480.jpg)

![image.png](./images/40CozeStudio_e4abb2328a1b4ab9b8e56fbb7f4bd2d4_a76cff.jpg)

![image.png](./images/40CozeStudio_65b8074956364b679e16a66dfd9d8176_2fbc4a.jpg)

![image.png](./images/40CozeStudio_23805d4b3371439b90fe030bc522d69f_3b932e.jpg)

![image.png](./images/40CozeStudio_84ed2e869d1b4cd68560a2cdc5644ef8_7f2339.jpg)

![image.png](./images/40CozeStudio_a08642be762e4b9bad97da30e2bb3e9a_2188fc.jpg)

首次打开需要输入许可证，可以从如下许可证选择一个输入即可：

ZF3RO-FHED2-M80TY-8QYGC-NPKYF

YF390-OHF8P-M81RQ-2DXQE-M2UT6

ZF71R-DMX85-08DQY-8YMNC-PPHV8

![image.png](./images/40CozeStudio_6ac2478f32bb4666a924a97dfe7a2631_7efa16.jpg)

![image.png](./images/40CozeStudio_2eae85d06e984bf4a2b1b3b3e8fba1fd_0ba815.jpg)

### **2.1.2. VMware创建虚拟机**

按照如下步骤创建新的虚拟机。

**1) 创建新的虚拟机**

![image.png](./images/40CozeStudio_092d535bc8ab4b7cac245cb83f7b9e5b_0556a4.jpg)

**2) 选择典型：**

![image.png](./images/40CozeStudio_e494a8b0aebe44c68b18e9984c80f691_4aa159.jpg)

选择稍后安装操作系统【或者傻瓜式安装选择安装程序光盘映像文件(iso)，选择镜像，直接安装成功】：

![image.png](./images/40CozeStudio_a551616b1f624cbe8a00d878263450ca_5ceae9.jpg)

**3) 选择Linux，版本选择CentOS 7 64位：**

![image.png](./images/40CozeStudio_420792cc6d5244bbbfdbe8edce922eaf_d328e8.jpg)

**4) 输入虚拟机名称和位置**

![image.png](./images/40CozeStudio_e257396118e845fd9cb19624160e5c12_a29888.jpg)

磁盘容量可以设置大一些，作为大数据节点可以设置200G，直接下一步：

![image.png](./images/40CozeStudio_b7be8cc372044527adedd8eb6e1deab2_71c9d2.jpg)

**5) 点击完成**

![image.png](./images/40CozeStudio_d158084872b242e984576f71e089659f_83c5e0.jpg)

**6) 配置虚拟机镜像路径，点击编辑虚拟机设置**

![image.png](./images/40CozeStudio_20f7af68b72247eabace083827cba4c9_b8d80c.jpg)

选择CD/DVD(IDE)，右侧连接中选择使用ISO映像文件(M)，选择CentOS7的镜像位置，点击确定。

![image.png](./images/40CozeStudio_0ffcddb05a7542c69fcf3ebc27930fbd_32a73e.jpg)

### **2.1.3. VM安装Centos7及启动**

WMware中配置好虚拟机之后就可以选择Centos7镜像进行安装，按照如下步骤操作即可。

首先点击开启此虚拟机：

![image.png](./images/40CozeStudio_34a5f0bced5e4ed0959274b7d7d7d57f_f77201.jpg)

等待1分钟，也可以直接按enter键继续：

![image.png](./images/40CozeStudio_53524a1982a240e0bf0f63fbdd69507d_7255c0.jpg)

等待检查镜像文件完整，达到100%后自动安装：

![image.png](./images/40CozeStudio_57fe7d0af9eb419699dc356619d8d54e_e1e016.jpg)

点击Continue:

![image.png](./images/40CozeStudio_812d12a0202a4ff7a01b69868d320cbd_02ae26.jpg)

黄色感叹号的选项必须配置，如下：SYSTEM中INSTALLATION DESTINATION 配置磁盘分区规划。

![image.png](./images/40CozeStudio_a751a60742804979a7a31ecf414c51ef_a3d226.jpg)

选择默认磁盘分区即可，点击Done。

![image.png](./images/40CozeStudio_5c648d8926f849cbae8836799557d1ac_e5daf0.jpg)

选择 SOFTWARE下的SOFTWARE SELECTION ，选择图形化界面安装，点击Done：

![image.png](./images/40CozeStudio_aab3d43f53704063afcae7e96948100a_d8e4c8.jpg)

以上图像化界面安装需要注意：Centos7如果选择图形化界面安装，那么未来启动每个虚拟机时除了使用分配外的内存，图形化界面还会单独使用内存，这部分内存也会很大。这样如果有多台虚拟机的话，图形化界面总体使用的内存是一部分很大的开销。

可以在这里选择最小化安装，也可以安装好虚拟机Centos7后使用命令关闭图形化界面，新版本的CentOS系统里使用’targets’ 取代了运行级别的概念。系统有两种默认的’targets’: [多用户.target](http://多用户.target) 对应之前版本的3 运行级别;[而图形.target](http://而图形.target) 对应之前的5运行级别。

```python
#查看默认的target,执行如下命令：
systemctl get-default

#开机以命令模式启动，执行：
systemctl set-default multi-user.target

#开机以图形界面启动，执行：
systemctl set-default graphical.target
```

点击Begin Installation安装：

![image.png](./images/40CozeStudio_f00fe798e6f546929865a2fc608fbe3e_ffbfc0.jpg)

配置root用户密码和添加新的用户：

![image.png](./images/40CozeStudio_04fef70aa8244606b6bd95c438cb272f_6c94d9.jpg)

配置完成后，点击Finish configuration。

![image.png](./images/40CozeStudio_58ac817d23dc454e99ad4f5d34655c05_0716bd.jpg)

点击Reboot重启机器。

![image.png](./images/40CozeStudio_cfa4a7252d294ef5b01588057d5cd31d_230e83.jpg)

重启过程中会遇到没有接受许可证的状况：

![image.png](./images/40CozeStudio_d8d8610781544def8764087fa7d75335_a959be.jpg)

按1->2->c->c选择接受许可证，继续启动即可。

Centos7系统安装完成后，可以进入Centos7系统进行一些设置。启动之后，可以设置向导为汉语，点击前进：

![image.png](./images/40CozeStudio_a3993fca73bd4ddfb6d04322c754549b_62eb8f.jpg)

键盘输入就选择默认即可。

![image.png](./images/40CozeStudio_821d3cc3334849818f397fed59678745_ef0aad.jpg)

点击开始使用。

![image.png](./images/40CozeStudio_b1420bc7eed24f8c8fa60e174365c0a5_fe732e.jpg)

安装完成。

![image.png](./images/40CozeStudio_d7df0f824a27467b963f2b925daf5042_712407.jpg)

## 2.2. **配置VMware网络环境**

### **2.2.1. 配置VMware网络环境**

想要安装的系统能连接网络，需要进行VMware网络环境配置。在VMware中，打开编辑->虚拟网络编辑器进行设置即可。

* **配置VMnet1 仅主机模式**

![image.png](./images/40CozeStudio_c607b5a664154aa69fbb4e0e6f030393_ff7c73.jpg)

点击DHCP设置，采用默认即可：

![image.png](./images/40CozeStudio_aab7fe16ae4b43149e0e1de73cdc1a55_a22f8f.jpg)

* **配置VMnet8 NAT模式**

![image.png](./images/40CozeStudio_32c99ae8efe34d8986d506a8c8aa8e92_24a481.jpg)

点击DHCP设置，采用默认即可：

![image.png](./images/40CozeStudio_b19241d2d33e47e69547611a68a62f08_d23cb3.jpg)

### **2.2.2. 配置本地网卡环境**

* **在网络连接中打开VMnet1,右键->属性->IPv4**

![image.png](./images/40CozeStudio_4b38646a65c8410d81f4785b4fc620ed_096621.jpg)

* **在网络连接中打开VMnet8,右键->属性->IPv4**

![image.png](./images/40CozeStudio_b9cfa51653fb4c1293c276a719689c68_410626.jpg)

### **2.2.3. 启动虚拟机配置IP**

使用root用户登录系统，点击Not listed? 输入用户名root和密码登录系统。

![image.png](./images/40CozeStudio_3b9133b0a98a4739bcc0d74708d72d7d_bdf570.jpg)

![image.png](./images/40CozeStudio_be63eeb18a254f648fbf5c11e93ed513_0d2a01.jpg)

进入/etc/sysconfig/network-scripts中，修改文件ifcfg-eno16777736，如下配置好之后，wq保存：

![image.png](./images/40CozeStudio_41cfd5eb2dbc4d33a8b2e9c7816dc6d3_dadb8c.jpg)

![image.png](./images/40CozeStudio_33b1acb17f2946279616555243cfdefd_2c6069.jpg)

```python
TYPE=Ethernet
BOOTPROTO=static     #使用static配置
DEFROUTE=yes
PEERDNS=yes
PEERROUTES=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_PEERDNS=yes
IPV6_PEERROUTES=yes
IPV6_FAILURE_FATAL=no
NAME=eno16777736
UUID=e8def32b-2132-4b8c-9733-e1de92a2a522
DEVICE=eno16777736
ONBOOT=yes      #开机启用本配置
IPADDR=192.168.179.100   #静态IP
GATEWAY=192.168.179.2   #默认网关
NETMASK=255.255.255.0   #子网掩码
DNS1=192.168.179.2       #DNS配置 可以与默认网关相同
```

重启网络服务：

![image.png](./images/40CozeStudio_b99047269e664346b5ea8b5d7d4facf2_ddc7fa.jpg)

```python
systemctl restart network.service
```

检查ip是否修改，ip addr 查看静态ip,也可以使用ifconfig查看：

```python
Ip addr
```

![image.png](./images/40CozeStudio_20b721284c5741e4ac293fe0d894f649_3168cd.jpg)

测试ping外网：

![image.png](./images/40CozeStudio_651c929b37b74a94922222adbf6d8441_b8c5af.jpg)

如果想要关闭图像化界面展示，也可以在Terminal中执行如下命令关闭图形化界面展示。

```python
#开机以命令模式启动，执行：
systemctl set-default multi-user.target
```

## 2.3. **xshell与xftp**

我们可以使用xshell连接搭建好的虚拟机系统，通过xftp向虚拟机中交互文件。下面分别介绍。

### **2.3.1. xshell安装及使用**

这里安装xshell5，双击“xshell\_5.0.0553.exe”进行xshell安装：

![image.png](./images/40CozeStudio_d92b39d13ab949c5988d6adca2f58599_882ad1.jpg)

![image.png](./images/40CozeStudio_01a15f8d9cc1421c88c3e77bcee00c77_d42f3e.jpg)

![image.png](./images/40CozeStudio_55c4d266bdf748d9b6dc0199d5024931_e2365c.jpg)

![image.png](./images/40CozeStudio_2d335d364f204f95b28ef6c62c0ac0c7_2a3322.jpg)

![image.png](./images/40CozeStudio_496786c1530b4b5cb830bf7f37a5d1c2_bb64bf.jpg)

![image.png](./images/40CozeStudio_3f550f0cbfa547cbb2a174dc9c66f6e6_ce7451.jpg)

![image.png](./images/40CozeStudio_b0d17f4f4f4e4279b5f2aa05a140181b_2a21bf.jpg)

按照以上步骤安装xshell完成后，连接现有虚拟机。

![image.png](./images/40CozeStudio_97ac2a38f2f7439c85d2b2ac36328c7f_1032cf.jpg)

![image.png](./images/40CozeStudio_cdadddeb47624e968e6502ebdf21fcbe_223c0b.jpg)

![image.png](./images/40CozeStudio_86f96cc36c5644cea56d1ab1ff03d6ac_d9ec36.jpg)

输入用户名和密码即可通过xshell连接Centos虚拟机节点。

使用xshell过程中最好配置下复制粘贴功能快捷键，后续在各个节点上执行命令时，非常方便。

![image.png](./images/40CozeStudio_e4b238eb3f7648dcbf0246568545078b_c69864.jpg)

![image.png](./images/40CozeStudio_48be49b327b14103a45636f22994a4f6_8ca738.jpg)

### **2.3.2. xftp安装及使用**

双击安装包“Xftp\_5.0.543.exe”进行xftp安装，xftp的安装与xshell安装方式一样，安装完成后可以通过xshell直接打开xftp进行文件传输：

![image.png](./images/40CozeStudio_e88c0c2f9e9743f5af104985171130e2_d5a94b.jpg)

![image.png](./images/40CozeStudio_7e29eac6a7424f9d8afe29a658d4664d_7c988b.jpg)

## 2.4. **快照与克隆虚拟机**

后续为了方便基于VMware创建多个虚拟机，我们可以基于已有搭建好的虚拟机节点进行快照，然后基于快照进行克隆，快速得到多个虚拟机。

**1) 清除节点MAC地址**

清除/etc/udev/rules.d/ 70-persistent-ipoib.rules文件，这个文件记录了这台机器的MAC地址，虚拟机在第一次启动时候会在这个文件中自动生成MAC地址，下面我们要克隆虚拟机，需要将这个文件删除，如果不删除，克隆出来的虚拟机也是这个MAC地址，那么就会有冲突，导致新克隆的机器ip不可使用。

![image.png](./images/40CozeStudio_82b2060990bc4173964a041eaec08651_f01d38.jpg)

**2) 保存快照**

![image.png](./images/40CozeStudio_085185d70fc3496ea8e9add6d6cd7397_5b7513.jpg)

![image.png](./images/40CozeStudio_1a4e0babcb9a4405949bd57836ac8815_8ca512.jpg)

![image.png](./images/40CozeStudio_b6a6a6bb5f4143a59598e6e0c63b8b2f_2dcd9b.jpg)

**3) 克隆虚拟机节点**

点击克隆：

![image.png](./images/40CozeStudio_0199f1df48924b9ca20060afe7a4e827_d50878.jpg)

![image.png](./images/40CozeStudio_722fd605fa364e1ca6d64150508ea9db_c0e971.jpg)

![image.png](./images/40CozeStudio_5c7610f9a6de4392b2a040e94322bd1a_b479ac.jpg)

![image.png](./images/40CozeStudio_33cad415ce864ea4bf7b08592840cd2c_da8dd2.jpg)

![image.png](./images/40CozeStudio_524c5af53e33474388d1da4a42ebc8bf_d9ebb3.jpg)

![image.png](./images/40CozeStudio_0e56012d2a0443118330099704a813b6_7da8be.jpg)

按照以上步骤，就可以完成虚拟机克隆，克隆出一台新的节点。

# 3\. **Coze Stdio模型配置**

## 3.1. **Ollama下载与安装**

Ollama 是一个开源的大型语言模型（LLM）平台，Ollama 提供了简洁易用的命令行界面和服务器，使用户能够轻松下载、运行和管理各种开源 LLM，通过 Ollama，用户可以方便地加载和使用各种预训练的语言模型，支持文本生成、翻译、代码编写、问答等多种自然语言处理任务。

ollama官网：[https://ollama.com](https://ollama.com)

Ollama下载地址:[https://github.com/ollama/ollama,这里以window中下载为例：](https://github.com/ollama/ollama,这里以window中下载为例：)

![image.png](./images/40CozeStudio_80c7e7b4539c400397f35ea5ce52915d_d072c2.jpg)

下载完成后双击“OllamaSetup.exe”进行安装，默认安装在“C\\users\\{user}\\AppData\\Local\\Programs”目录下，建议C盘至少要有10G 剩余的磁盘空间，因为后续Ollama中还要下载其他模型到相应目录中。

![image.png](./images/40CozeStudio_739941b4442b47829aee3fd23befa509_1e3e37.jpg)

安装完成后，电脑右下角自动有“Ollama”图标并开机启动。可以在cmd中运行模型进行会话

```python
#命令 ollama run +模型 deepseek-r1:1.5b
ollama run deepseek-r1:1.5b
>>> 你是谁？
<think>
</think>
您好！我是由中国的深度求索（DeepSeek）公司开发的智能助手DeepSeek-R1。如您有任何任何问题，我会尽我所能为您提供帮助。
>>>
```

注意：使用run命令第一次运行模型，如果模型不存在会自动下载，然后进入模型交互窗口。后续使用会自动进入到交互窗口。

在浏览器中输入“localhost:11434”可以访问ollama，输出“Ollama is running”。默认情况下，Ollama 服务仅监听本地回环地址（127.0.0.1），这意味着只有在本地计算机上运行的应用程序才能访问该服务，如果想要使用“window ip:11434”访问ollama需要在环境变量中加入“OLLAMA\_HOST”为“0.0.0.0”,这样就将 Ollama 的监听地址设置为 0.0.0.0，使其监听所有网络接口，包括本机 IP 地址。

![image.png](./images/40CozeStudio_f973ce136130466999293923fb7b9eff_2264b6.jpg)

注意：以上环境变量设置完成后，需要重启ollama。

## 3.2. **Ollama聊天模型配置**

Coze Studio 是基于大语言模型的 AI 应用开发平台，首次部署运行 Coze Studio 开源版之前，你需要先克隆到本地的项目中，配置所需要的模型。项目正常运行过程中，也可以随时按需添加新的模型服务、删除不需要的模型服务。

Coze Studio 支持的模型服务如下：

* 火山方舟 | Byteplus ModelArk
* OpenAI
* DeepSeek
* Claude
* Ollama
* Qwen
* Gemini

在 Coze Studio 开源版中，模型配置统一放在backend/conf/model 目录中，目录下存在多个 yaml 文件，每个文件对应一个可访问的模型。 为方便开发者快速配置，Coze Studio 在 backend/conf/model/template 目录下提供了一些模板文件，覆盖了常见的模型类型，例如火山方舟、OpenAI 等。开发者可以找到对应厂商的模型模板，复制到backend/conf/model 目录，根据模板注释设置各个参数。

以上各种模型的配置可以参考：[https://github.com/coze-dev/coze-studio/wiki/3.-%E6%A8%A1%E5%9E%8B%E9%85%8D%E7%BD%AE](https://github.com/coze-dev/coze-studio/wiki/3.-%E6%A8%A1%E5%9E%8B%E9%85%8D%E7%BD%AE) ，如下演示在Coze Stdio中配置Ollama 的“deepseek-r1:1.5b”模型，步骤如下：

**1) 复制模板文件**

```python
[root@node2 ~]# cp /software/coze/coze-studio-0.2.2/backend/conf/model/template/model_template_ollama.yaml /software/coze/coze-studio-0.2.2/backe
nd/conf/model/
```

**2) 修改模型配置**

```python
[root@node2 ~]# cd /software/coze/coze-studio-0.2.2/backend/conf/model/
[root@node2 model]# vim model_template_ollama.yaml
```

![image.png](./images/40CozeStudio_330dd40cd4bc4e22b5265fe39a256eea_2ae9a5.jpg)

name为展示在Coze Stdio中模型的名字；meta.conn\_config.base\_url为ollama地址；meta.conn\_config.model为使用的Ollama中的模型名称。

**3) 重启Coze Stdio 服务**

```python
#停止Coze Stdio服务
[root@node2 docker]# docker compose down

#启动Coze Stdio服务
[root@node2 docker]# docker compose up -d
```

## 3.3. **Ollama向量化模型配置**

Coze Studio 开源版支持自定义设置知识库向量化依赖的 Embedding 模型，使知识库的向量化环节效果更符合指定场景的业务需求。

Coze Studio 支持四种方式接入向量化模型：

![image.png](./images/40CozeStudio_711a92f7b5fc438da0612eaf7d5d8728_9ad901.jpg)

如下我们使用Ollama中“nomic-embed-text:latest”模型作为向量Embedding模型，配置方式如下：

**1) 配置.env**

进入$COZE\_STIDIO\_HOME/docker/.env 文件，找到Embedding配置模块，配置如下：

```python
export EMBEDDING_TYPE="ollama"
export OLLAMA_EMBEDDING_BASE_URL="http://192.168.1.104:11434"
export OLLAMA_EMBEDDING_MODEL="nomic-embed-text"
export OLLAMA_EMBEDDING_DIMS="768"
```

配置文成后保存.evn文件。

![image.png](./images/40CozeStudio_81fd590c2bf7411db5738a58f08bdff4_3594c9.jpg)

注意：EMBEDDING\_TYPE 默认值为ark（火山方舟向量模型），这里使用Ollama中“nomic-embed-text”向量模型，所以改为ollama；“nomic-embed-text”模型需要在Ollama中提前下载，该模型向量化后的维度为768。

**2) 重启Coze Stdio服务**

```python
#停止Coze Stdio服务
[root@node2 docker]# docker compose down

#启动Coze Stdio服务
[root@node2 docker]# docker compose up -d
```

# 4\. **Coze Stdio使用**

## 4.1. **快速上手案例**

按照如下步骤实现一个暖心机器人，当和暖心机器人对话时，它可以给你正向的鼓励，抚慰你的情绪。

**1) 创建智能体**

![image.png](./images/40CozeStudio_6f46df4c7a1a412cb2376e887caff776_f2655f.jpg)

![image.png](./images/40CozeStudio_929c7c78d0424f829fa37d0f5e0a8829_3df095.jpg)

![image.png](./images/40CozeStudio_2188183a2cd042e8b7e4badb7d0fbe76_290daa.jpg)

创建智能体后，你会直接进入智能体编排页面。你可以：

* 在左侧人设与回复逻辑面板中描述智能体的身份和任务。
* 在中间技能面板为智能体配置各种扩展能力。
* 在右侧预览与调试面板中，实时调试智能体。

**2) 编写提示词**

配置智能体的第一步就是编写提示词，也就是智能体的人设与回复逻辑。智能体的人设与回复逻辑定义了智能体的基本人设，此人设会持续影响智能体在所有会话中的回复效果。建议在人设与回复逻辑中指定模型的角色、设计回复的语言风格、限制模型的回答范围，让对话更符合用户预期。

在智能体配置页面的人设与回复逻辑面板中输入提示词。例如暖心机器人的提示词可以设置为：

```python
# 角色 
你是一个充满正能量的赞美鼓励机器人，时刻用温暖的话语给予人们赞美和鼓励，让他们充满自信与动力。 
## 技能 
### 技能 1：赞美个人优点 
1. 当用户提到自己的某个特点或行为时，挖掘其中的优点进行赞美。回复示例：你真的很[优点]，比如[具体事例说明优点]。 
2. 如果用户没有明确提到自己的特点，可以主动询问一些问题，了解用户后进行赞美。回复示例：我想先了解一下你，你觉得自己最近做过最棒的事情是什么呢？ 
### 技能 2：鼓励面对困难 
1. 当用户提到遇到困难时，给予鼓励和积极的建议。回复示例：这确实是个挑战，但我相信你有足够的能力去克服它。你可以[具体建议]。 
2. 如果用户没有提到困难但情绪低落，可以询问是否有不开心的事情，然后给予鼓励。回复示例：你看起来有点不开心，是不是遇到什么事情了呢？不管怎样，你都很坚强，一定可以度过难关。 
### 技能 3：回答专业问题 
遇到你无法回答的问题时，调用 top_news 搜索答案 
## 限制 
- 只输出赞美和鼓励的话语，拒绝负面评价。 
- 所输出的内容必须按照给定的格式进行组织，不能偏离框架要求。 
```

注意：相比于Coze AI开发平台，Coze Stdio不能自动优化提示词。

**3) 为智能体添加技能**

如果模型能力可以基本覆盖智能体的功能，则只需要为智能体编写提示词即可。但是如果你为智能体设计的功能无法仅通过模型能力完成，则需要为智能体添加技能，拓展它的能力边界。例如文本类模型不具备理解多模态内容的能力，如果智能体使用了文本类模型，则需要绑定多模态的插件才能理解或总结 PPT、图片等多模态内容。

如暖心机器人中，模型能力基本可以实现我们预期的效果。但如果你希望为暖心机器人添加更多技能，例如遇到模型无法回答的问题时，通过搜索引擎查找答案，那么可以为智能体添加一个“搜狐热闻”插件。

![image.png](./images/40CozeStudio_3f594a93341c4f5da0eaafcea905cb9b_c041b2.jpg)

也可以给智能体添加开场白、用户问题建议、背景图片等功能，增强对话体验，如下：

![image.png](./images/40CozeStudio_63453b0f99ee44f493f4d7974a9acbcd_dd6e04.jpg)

**4) 调试智能体**

配置好智能体后，可以在预览与调试区域中测试智能体是否符合预期。

![image.png](./images/40CozeStudio_c5a23b76f1314d7a8fa9418d90f9fd33_76ed94.jpg)

可见智能体会自动调用工具并反馈。

**5) 发布智能体**

完成调试后，单击发布将智能体发布到API、ChatSDK渠道中，在终端应用中使用智能体。注意：目前Coze Stdio与Coze AI平台发布智能体支持渠道不同，Coze AI 支持将智能体发布到飞书、微信、抖音、豆包等多个渠道中，而Coze Stdio只能发布为API、ChatSDK两个渠道。

![image.png](./images/40CozeStudio_540c236b53854df68548391bbd82dc4f_4be6d6.jpg)

## 4.2. **为智能体添加技能**

### **4.2.1. 插件**

插件是一个工具集，一个插件内可以包含一个或多个工具（API）。插件工具可以扩展 LLM 的能力，比如联网搜索、科学计算或绘制图片，赋予并增强了 LLM 连接外部世界的能力。Coze Studio 提供了两种插件工具类型，即官方内置工具和自定义工具。官方内置工具由后台统一配置，支持 Coze Studio 开源版中所有用户使用；自定义工具的使用范围为当前工作空间。

**案例：创建“文档查询助手”智能体，使用“文库搜索”插件获取AI领域文章。**

**1) 创建智能体，命名为文档助手**

![image.png](./images/40CozeStudio_360d4ba33dd24a1a92bc86ce9eeabb90_03c42c.jpg)

**2) 编写提示词**

提示词如下（**注意提示词中使用了文库搜索中的“document\_search”工具**）：

```python
# 角色
你是一个专业文档助手，能够使用文库搜索中“document_search”工具搜索文章，并给用户做出回复。

## 技能
### 技能 1: 搜索并总结文章
1. 当用户提出搜索文章并返回相关内容的需求时，使用“document_search”工具搜索相关文章。
2. 对搜索到的文章进行分析和提炼，总结出核心内容。
===回复示例===
核心内容：<总结的文章核心内容>
引用来源：<若有相关引用说明引用来源>
===示例结束===

## 限制:
- 只回答与搜索文章并总结核心内容相关的问题，拒绝回答无关话题。
- 所输出的内容必须按照给定的格式进行组织，不能偏离框架要求。
- 总结部分应简洁准确，突出关键要点。 
```

**3) 为智能体添加插件**

![image.png](./images/40CozeStudio_1c9fa4349e5f44bd85c2ab029080fcb9_2bd859.jpg)

**4) 调试智能体**

配置好智能体后，可以在预览与调试区域中测试智能体是否符合预期。

![image.png](./images/40CozeStudio_08c7af66d17c406788eb8d49904b7aac_d259ce.jpg)

可见智能体会自动调用工具并反馈。

**5) 发布智能体**

点击发布，发布智能体。

![image.png](./images/40CozeStudio_1263bccc689c4f87b15dfee1494f4b67_78c409.jpg)

**注意：在智能体中添加插件后，可以通过参数配置灵活设置参数的默认值及可见性。**

参数的默认值可有效避免大模型运行时因插件参数值缺失而导致的报错。同时，针对一些值较为稳定的参数，设置其默认值且隐藏其可见性可减少大模型的无效判断，从而提高插件调用效率。

![image.png](./images/40CozeStudio_a71310687bf6499b9618b4d377e2f712_ee1ee0.jpg)

修改参数配置：

* **默认值**：设置参数的默认值。你可以输入固定值，或引用变量值，例如启动系统变量，并引用系统变量值。
* **开启**：打开开关，表示参数对大模型可见，大模型可以读取该参数；关闭开关，表示隐藏参数，大模型无法读取该参数。

如果设置了参数默认值且打开开启开关，那么调用插件时，大模型会以该默认值为基础，但仍会根据自身的逻辑判断是否使用其他值。

如果设置了参数默认值且关闭开启开关，那么调用插件时，大模型只会使用这个默认值。

### **4.2.2. 工作流**

工作流支持通过可视化的方式，对插件、大语言模型、代码块等功能进行组合，从而实现复杂、稳定的业务流程编排，例如旅行规划、报告分析等。当目标任务场景包含较多的步骤，且对输出结果的准确性、格式有严格要求时，适合配置工作流来实现。关于工作流使用详细内容参考“Coze AI 平台课程中工作流讲解”部分。

可以为智能体添加工作流，并在提示词中引用工作流的名称来调用工作流，智能体会按照工作流编排的流程来响应用户需求。

**案例：创建“绘制海报”智能体，实现生成海报。**

**1) 创建智能体，命名为“绘制海报”**

![image.png](./images/40CozeStudio_a33de6f184054752a6e3660a492181ac_96add4.jpg)

**2) 设置Agent使用工作流**

![image.png](./images/40CozeStudio_73f238cf4c414d15b3ddbfea33c7af83_e0ca6d.jpg)

如果没有创建过工作流，那么需要首先创建工作流，工作流名称为“generate\_poster”，描述为“根据用户输入提示词返回海报链接”：

![image.png](./images/40CozeStudio_6039cd76517e40768d4690128da758e5_ebdaee.jpg)

以上工作流的名称不能使用中文，创建工作流后，加入“大模型”、“创可贴智能设计”节点，并设置各个节点：

![image.png](./images/40CozeStudio_1c93bdef7c2344a88e5e67652f41a588_d2aadb.jpg)

开始节点配置：

![image.png](./images/40CozeStudio_03637ff3d1b24901830b3a16e7e7c16d_35cb04.jpg)

大模型节点配置：

![image.png](./images/40CozeStudio_67139ff73c694dff964d8bf91da866dd_feb49a.jpg)

```python
根据用户输入内容{{input}} 给我输出生成该海报内容的提示词，只需要直接输出提示词即可，不需要额外解释
```

“创可贴智能设计”插件节点配置：

![image.png](./images/40CozeStudio_491e3d185c214fb886b379f75922fc8d_bd7186.jpg)

结束节点配置：

![image.png](./images/40CozeStudio_2ab36b1b01e34c7686246a86440f1dac_15133d.jpg)

注意：以上在提示词中引入变量使用“{{变量}}”形式，完成以上工作流设置后，可以测试预览，没有问题后即可发布。

![image.png](./images/40CozeStudio_e64d6e2189244558a5f67cd6f3c49f09_a1a869.jpg)

![image.png](./images/40CozeStudio_a6421b096e1d4a62a0e2a9ed43703a97_8145b1.jpg)

**3) 给Agent设置提示词**

在智能体的“人设与回复逻辑”中，引用工作流的名称来调用工作流。

![image.png](./images/40CozeStudio_54f971c29faa4b9ba169dedae3b813fd_9264f6.jpg)

**4) 调试智能体**

![image.png](./images/40CozeStudio_4b078d3f145b4314884be43c6af150ea_53e7e3.jpg)

**5) 发布智能体**

点击发布，发布智能体。

![image.png](./images/40CozeStudio_65215e8c81404758bb83b97844424a64_78f354.jpg)

## 4.3. **为智能体添加知识库**

### **4.3.1. 知识库相关内容**

Coze Stdio知识库功能支持上传和存储外部知识内容，并提供了多种检索能力。Coze Stdio的知识能力可以解决大模型幻觉、专业领域知识不足的问题，提升大模型回复的准确率。

![image.png](./images/40CozeStudio_42d5875f0b8544429036eaa2bd9c8f84_05e7c0.jpg)

#### **4.3.1.1. 知识库类型与限制**

使用知识库功能的第一步就是上传知识内容，知识内容分为如下三种知识类型:

![image.png](./images/40CozeStudio_31bb2bd4d03b404d8cabbd72730b4937_8a2e59.jpg)

#### **4.3.1.2. 创建文本知识库**

Coze Stdio支持从本地文档、自定义等渠道上传文本内容到知识库。具体使用可以参考：[https://www.coze.cn/open/docs/guides/create\_knowledge](https://www.coze.cn/open/docs/guides/create_knowledge)

下面以本地文档方式上传pdf文件为例，演示创建文本知识库。

**1) 创建知识库**

进入Coze Stdio平台，找到“资源库”，创建“知识库”,选择“创建Coze Stdio知识库”：

![image.png](./images/40CozeStudio_9ce5b699cd2b4753962584a66f7e76d0_d5e6d4.jpg)

**2) 上传pdf文件并设置知识库**

上传文本“内科学.pdf”，以及设置文档解析、分段、存储、索引等策略。

![image.png](./images/40CozeStudio_24c9aafa1b5641d0ae774f8bffe6e6e4_02dcf4.jpg)

![image.png](./images/40CozeStudio_dd4f73fc8dd14d17af569b768a03a2aa_019f9a.jpg)

![image.png](./images/40CozeStudio_e0fe2c4d68a944a186dc4df26d001aea_34a8e1.jpg)

![image.png](./images/40CozeStudio_1b19aeb871304069a0ff7939aa53b7ff_6418fb.jpg)

![image.png](./images/40CozeStudio_77635acc6d2a497dba74741d48541706_9dfc8f.jpg)![image.png](./images/40CozeStudio_1f8e21e330e4430a8a89649e654eed04_6a9f99.jpg)

#### **4.3.1.3. 创建表格知识库**

Coze Stdio支持从本地文档、自定义等渠道上传表格到知识库。具体使用可以参考：[https://www.coze.cn/open/docs/guides/create\_table\_knowledge](https://www.coze.cn/open/docs/guides/create_table_knowledge)

下面以本地文档方式上传xlsx文件为例，演示创建表格知识库。

**1) 创建知识库**

进入Coze Stdio平台，找到“资源库”，创建“知识库”,选择“创建Coze Stdio知识库”：

![image.png](./images/40CozeStudio_f3281839c08347a394cc4ccd1224378c_582d99.jpg)

**2) 上传xlsx文件并设置知识库**

![image.png](./images/40CozeStudio_02a5081694184f3d899cbb99e9536d04_a9c1da.jpg)

![image.png](./images/40CozeStudio_2dc73be0fe94408a82502095681310cd_5d2790.jpg)

![image.png](./images/40CozeStudio_afeb1849145a4e7d9e006724e0e4b700_b128a0.jpg)

![image.png](./images/40CozeStudio_2a0543f526064a7a88e48430003a42d3_87640f.jpg)

![image.png](./images/40CozeStudio_76562c20983a4786bbcebd38fd776d87_ea7f36.jpg)

#### **4.3.1.4. 创建图片知识库**

Coze Stdio支持上传本地图片到知识库。具体使用可以参考：[https://www.coze.cn/open/docs/guides/create\_image\_knowledge](https://www.coze.cn/open/docs/guides/create_image_knowledge)

下面从本地上传图片为例，演示创建图片知识库。

**1) 创建知识库**

进入Coze Stdio平台，找到“资源库”，创建“知识库”,选择“创建Coze Stdio知识库”：

![image.png](./images/40CozeStudio_f572c13a873b4de085c6ab65cc09159f_61359b.jpg)

**2) 上传图片并配置知识库**

![image.png](./images/40CozeStudio_42f052f6b40d43148a735fae55ad8e36_d5819e.jpg)

![image.png](./images/40CozeStudio_8e3e73ec5f5e4cd6b5ccb543d9bce5ed_c4bb19.jpg)

![image.png](./images/40CozeStudio_9891355a8ff5421d83a6027a9d33304b_7b27ee.jpg)

![image.png](./images/40CozeStudio_e79f16ac6658496e8d5e6fc02b1cc6e1_73921a.jpg)

注意：标注是为了让系统能够更准确地检索和召回相关的图片数据。如果不进行图片标注，尤其是对于包含表格数据的图片，系统将无法理解图片中的数据结构和内容，导致无法有效地建立索引。

目前支持两种标注方式：

* 智能标注：系统会深度理解图片内容，自动提供详细的内容描述信息。
* 人工标注：根据图片内容，手动添加图片描述信息。如果选择人工标注，则需等待服务器处理完成后，单击图片手动添加标注信息。

### **4.3.2. 为智能体添加知识库**

案例：创建智能体，根据用户问题从指定知识库中查找答案并回复。

**1) 创建智能体，命名为“智能体使用知识库”**

![image.png](./images/40CozeStudio_b03a23ad5b9f46a8963357bea22e5e31_cda0d6.jpg)

**2) 给Agent添加知识库并给Agent设置提示词**

添加知识库及设置提示词：

![image.png](./images/40CozeStudio_5aad50ef014b402899e439212e304288_241df9.jpg)

提示词内容如下：

```python
# 角色
你是一个智能体，能够依据知识库内的科学知识，严谨且准确地回答用户的问题。

## 技能
### 技能 1: 回答问题
1. 当用户提出问题时，在知识库{#LibraryBlock id="7504581101433470988" uuid="X_5RYITPDpolVavU8FyGn" type="text"#}内科学知识{#/LibraryBlock#}中进行精准搜索。
2. 如果知识库中有相关内容，依据知识库内容回答用户问题。
3. 如果从知识库中没有找到相关内容，直接告诉用户不清楚这个问题的答案。

## 限制:
- 仅能依据知识库{#LibraryBlock id="7504581101433470988" uuid="JYh3rdv1Rhck8EFQn4TAU" type="text"#}内科学知识{#/LibraryBlock#}来回答问题，拒绝回答知识库外无依据的问题。
- 回答需严谨准确，不能随意发挥或进行无根据的猜测。
- 回答内容需简洁明了，符合逻辑。
- 需明确回答用户问题，若知识库无相关内容，必须明确告知用户不清楚答案。 
```

**3) 调试智能体**

![image.png](./images/40CozeStudio_2caab0df158942afb7b19a1eca91a014_dd5a84.jpg)

**4) 发布智能体**

![image.png](./images/40CozeStudio_f7dfd73596aa45929c31a8a7501c96e5_528637.jpg)

## 4.4. **为智能体添加记忆**

### **4.4.1. 变量**

你可以通过创建变量来保存用户个人信息，例如语言偏好等，并让智能体记住这些特征，使回复更加个性化。变量以 key-value 形式存储用户的某一行为或偏好。**大语言模型会根据用户输入内容进行语义匹配，为定义的变量赋值并保存值。你可以在提示词中为智能体声明某个变量的具体使用场景。**

变量分为系统变量和用户变量：

* 系统变量：系统默认创建用户信息系统变量，你不可以新增、修改、删除默认的系统变量。这些系统变量默认全部关闭，为不可用状态，你可以根据实际业务需求选择开启需要的系统变量。开启后，系统在用户请求时自动产生变量数据，这些数据是只读的，不可由用户或开发者修改。
* 用户变量：用户变量用于存储每个用户在使用智能体过程中，需要持久化存储和读取的数据，例如用户的个性化设置、语言偏好、历史交互记录等。开发者可以在Coze Stdio平台中配置用户变量，并在用户与智能体交互时存储和检索这些变量，用户变量的值在用户会话之间持久化存储，支持可读可写。

案例：创建智能体，设置变量指定用户名称，在让智能体回复用户问题时，先称呼名称再进行问题回复。

**1) 创建智能体，命名为“智能体使用变量”**

![image.png](./images/40CozeStudio_96fd517885244f01b17aa2f8d05a1295_973f1d.jpg)

**2) 给智能体添加变量并设置提示词**

给智能体添加name变量：

![image.png](./images/40CozeStudio_40008a13464f4617aade2ef0e0bbde75_f855e3.jpg)

设置提示词：

![image.png](./images/40CozeStudio_a41b5b08dc9645b489043e296f0407a9_ae3883.jpg)

提示词内容如下：

```python
# 角色
你是一个名为“智能体使用变量”的智能助手，在回答用户问题时，需按照特定格式回复。

## 技能
### 技能 1: 标准回复
1. 当用户提出问题时，按照“你好,name ”,然后再加上回复的内容 的格式进行回复，name 需根据具体情况合理代入相关称呼或信息。

## 限制:
- 回复必须严格按照指定格式“你好,name ,然后再加上回复的内容”进行，不得偏离此框架要求。
```

**3) 调试智能体**

![image.png](./images/40CozeStudio_467839032c9a45398674fbaa755b94fb_ae28ef.jpg)

可以通过如下方式查看修改后的变量：

![image.png](./images/40CozeStudio_a60680a79abc4a7eb1a29ad5e4e2ccfc_0710e3.jpg)

**4) 发布智能体**

![image.png](./images/40CozeStudio_e05ad9abf9b74a98a9306951e5b9345b_2fcd72.jpg)

### **4.4.2. 数据库**

Coze Stdio提供了类似传统软件开发中数据库的功能，允许用户以表格结构存储数据。这种数据存储方式非常适合组织和管理结构化数据，例如客户信息、产品列表、订单记录等。

案例：创建智能体，使用数据库记录日常开支。

**1) 创建智能体，命名为“智能体使用数据库”**

![image.png](./images/40CozeStudio_2aaef53a368b49cc955076a82eec2f79_7b9c1f.jpg)

**2) 给智能体设置数据库**

![image.png](./images/40CozeStudio_20784d9cc93b43f78797cc7e47ab9f92_39a430.jpg)

![image.png](./images/40CozeStudio_56df2709a0e94862b9e7d9224c7f3d51_df6794.jpg)

设置数据库表：

![image.png](./images/40CozeStudio_0524e74d3b85420986dbe8e56fa9a828_1f9f33.jpg)

**3) 给智能体设置提示词**

![image.png](./images/40CozeStudio_86861e8a48164981884d4a8a4412994d_541904.jpg)

```python
# 角色
你是一位专业的日常开支记录助手，可详细记录并深入分析日常开销。

## 技能
### 技能1:记录开支
将用户输入的信息准确记录在“daily_expenses”表中。
-date: 消费时间。
-goods: 所购商品。
-expense: 消费金额。

### 技能2:开支分析
根据用户的输入信息，从“daily_expenses”表中查询开支数据，生成开支报告。
 -报告内容包括各项支出的占比情况。
 -对比不同时期的开支趋势。
 -基于分析结果给出合理的消费建议。

## 限制：
仅服务于日常开支的记录与查询，不回应其他无关问题。
```

**4) 调试智能体**

![image.png](./images/40CozeStudio_02b0c028edc54eb6bb374a26ab5b7095_0332c0.jpg)

**5) 发布智能体**

![image.png](./images/40CozeStudio_7c477168771b404fbab12495bf5e0810_812055.jpg)

# 5\. **开发AI应用**

目前Coze Stdio中AI 应用并没有完全开源，只支持构建一些工作流，在Coze Stdio中主推Agent开发，所以AI 应用只做了解即可。

如下步骤完成AI 翻译应用开发。

**1) 创建AI应用，命名为“AI翻译”**

![image.png](./images/40CozeStudio_5edb76fc15a745038d6e3159f9280807_f49871.jpg)

![image.png](./images/40CozeStudio_5dfc8a56664142839a43088166f254e9_cda90d.jpg)

**2) 编排业务逻辑**

在业务逻辑界面，找到工作流，然后单机“+”,新建工作流。

![image.png](./images/40CozeStudio_cf2bdd7179b34510b321842bbad78afb_0e5cbd.jpg)

在工作流画布，单击开始节点的连接线或画布下方的添加节点按钮，然后选择大模型节点，并完成连线。

![image.png](./images/40CozeStudio_df7837f0e01f4e73864e3e683ed71040_a3eede.jpg)

单击开始节点进行配置：

![image.png](./images/40CozeStudio_b1c134af152140cfa1b36f15baeb0d04_3f67c3.jpg)

点击大模型节点进行配置：

![image.png](./images/40CozeStudio_6ce8808144eb4f299fd46ded6d589d43_f5c4de.jpg)

系统提示词如下：

```python
# 角色
你是一个专业的翻译官，能够准确地将用户输入的内容翻译成目标语言，不进行随意扩写。

## 技能
### 技能 1：翻译文本
1. 当用户提供一段文本时，迅速将其翻译成目标语言。
2. 确保翻译的准确性和流畅性。

## 限制：
- 只进行翻译工作，不回答与翻译无关的问题。
- 严格按照用户要求的目标语言进行翻译，不得擅自更改。
```

用户提示词如下：

```python
将用户输入的内容{{content}}翻译成目标语言{{lang}}。
```

设置结束节点，返回文本：

![image.png](./images/40CozeStudio_7957fe5c279441caad0c9c612744dea4_7aec13.jpg)

**3) 试运行工作流**

为了保证业务逻辑实现符合预期，单击试运行测试工作流的执行。

![image.png](./images/40CozeStudio_b826a80ce8674cffb703abbe024e411e_814ed2.jpg)

**4) 发布工作流**

![image.png](./images/40CozeStudio_7cff3946a84c4a748db9a86b5e72a638_6486e5.jpg)

# 6\. **自定义插件**

Coze Stdio目前自带的插件较少，如果Coze Stdio集成的插件不满足你的使用需求，你还可以创建自定义插件来集成需要使用的 API。

更多插件定义内容参数Coze官网：[https://www.coze.cn/open/docs/guides/plugin](https://www.coze.cn/open/docs/guides/plugin)

基于已有服务创建插件时，直接将公开使用或本人开发的 API 配置为插件。创建插件后，必须发布插件才可以被智能体使用。

下面实现“基于API”创建插件，来实现查询微博热搜新闻。微博热搜新闻API连接为：[https://shanhe.kim/api/za/weibo.php](https://shanhe.kim/api/za/weibo.php)

**1) 配置插件**

基于已有服务创建插件：

![image.png](./images/40CozeStudio_63c1919f574349ae8e60ccd03ebdea22_03074f.jpg)

![image.png](./images/40CozeStudio_26895d3a281a4dc5a59b4e75ec7d0280_bd74f6.jpg)

![image.png](./images/40CozeStudio_9553f523a7114582ac5625a908f42e2e_1c7f46.jpg)

![image.png](./images/40CozeStudio_58d958b6ba834fe4bfea5978a7886f32_ed2cf1.jpg)

![image.png](./images/40CozeStudio_a431bd2cda3c4a28813825b9282376ea_ec3880.jpg)

![image.png](./images/40CozeStudio_55221cedfb0348d8b4e03c74da2c7ef0_59aed8.jpg)

微博连接测试访问返回内容如下：

```python
{
  "code": "200",
  "day": "xxxx年xx月xx日 xx:xx",
  "fresh_text": "热榜每分钟更新一次",
  "Top_1": {
    "title": "积极促进产业高端化智能化绿色化",
    "heatnum": "获取失败",
    "url": "https://s.weibo.com//weibo?q=积极促进产业高端化智能化绿色化",
    "labelname": "热"
  },
  ... ...
  "Top_50": {
    "title": "孙颖莎vs石洵瑶",
    "heatnum": 136039,
    "url": "https://s.weibo.com//weibo?q=孙颖莎vs石洵瑶",
    "labelname": "无"
  }
}
```

**2) 发布插件**

![image.png](./images/40CozeStudio_50513c5c59b1412b9104c3799531acfd_fa8cb0.jpg)

**3) 在智能体中使用插件**

![image.png](./images/40CozeStudio_fd74367d02934a7fa9e29629c024c612_03b96d.jpg)

![image.png](./images/40CozeStudio_50915725beef4dceb654bf74fd5a4a1e_805953.jpg)

![image.png](./images/40CozeStudio_ae904f8cd60c496ca54447cef435afef_807e63.jpg)

# 7\. **Chat API 和Chat SDK**

## 7.1. **Chat API使用**

Coze Studio 并未提供像 Coze AI 那样完整的Python/Go/Java SDK，但它支持通过 Rest API 方式来与发布的Agent进行对话，即这里所说的Chat API。

### **7.1.1. 准备工作**

使用Chat API 必须先将智能体发布为API服务且要设置访问令牌。

* **发布智能体为API服务**

智能体发布为 API 服务之后，才能通过调用 API 的方式使用这个智能体，例如查看智能体的基本设置、发起一个智能体对话等。

* **获取访问令牌**

Coze Studio 社区版 API 和 Chat SDK 通过个人访问令牌鉴权。调用 API 之前，你需要先获得访问令牌。 调用扣子 API 时，你需要在 Header 中通过 Authorization 参数指定访问令牌（Access token），扣子服务端会根据访问令牌验证调用方的操作权限。

获取访问令牌的操作步骤如下：

![image.png](./images/40CozeStudio_08fb3d50d1d14f57a28d7b42d2c9f8f6_13ed2d.jpg)

### **7.1.2. Python API**

Python代码中使用Rest API 代码方式与Coze Stdio 中Agent进行对话代码如下：

```python
import json, requests
'''
 使用Http 方式使用 Coze Stdio中的Agent
'''

# 本地部署的 Coze Studio API 服务地址
BASE = "http://node2:8888"
# 你的 Coze API 访问令牌
TOKEN = "pat_2dffc6a017ff0840a5e53a7379bcb870d456edcee6602e00cf9c4f7aa719ee1d"
# Coze Stdio中机器人 ID
BOT_ID = "7537182040039358464"
# 自定义用户 ID，用于区分不同会话
USER_ID = "123"

# 设置 HTTP 请求头，包含认证信息和请求体类型
headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

# 1) 创建会话
resp = requests.post(
    f"{BASE}/v1/conversation/create",  # 会话创建接口
    headers=headers,  # 请求头
    json={"bot_id": BOT_ID},  # 请求体，指定使用的机器人 ID
    timeout=30  # 超时时间 30 秒
)

# 检查请求是否成功，否则抛出异常
resp.raise_for_status()

# 解析返回 JSON，提取会话 ID
conv_id = resp.json()["data"]["id"]

# 2) 发起流式聊天（SSE）
params = {"conversation_id": conv_id}  # 附加参数，指定会话 ID

payload = {
    "bot_id": BOT_ID,  # 机器人 ID
    "user_id": USER_ID,  # 用户 ID
    "stream": True,  # 启用流式响应
    "auto_save_history": True,  # 自动保存对话历史
    "additional_messages": [  # 附加消息，作为对话输入
        {"role": "user", "content": "给我讲个励志的故事", "content_type": "text"}  # 用户发送的文本消息
    ],
}

# 用于存储完整的回答内容
full_answer = []

# 用于跟踪当前回答的消息 ID（便于增量拼接）
current_msg_id = None

# 发送 POST 请求到聊天接口，开启 SSE 流式连接
with requests.post(
    f"{BASE}/v3/chat",  # 聊天接口
    headers=headers,  # 请求头
    params=params,  # 查询参数
    json=payload,  # 请求体
    stream=True,  # 开启流式传输
    timeout=600  # 设置超时为 600 秒
) as r:
    r.raise_for_status()  # 检查响应状态码
    r.encoding = "utf-8"  # 强制设置响应编码为 UTF-8（SSE 标准要求）
    for raw in r.iter_lines(decode_unicode=True):  # 按行读取流式数据
        # print("raw:",raw)
        if not raw:  # 跳过空行
            continue
        if raw.startswith("data:"):  # 只处理 data: 开头的 SSE 数据
            data = raw[5:].strip()  # 去掉 data: 前缀并去掉空格
            if data == "[DONE]":  # 如果收到 [DONE] 表示流结束
                break
            try:
                pkt = json.loads(data)  # 将 JSON 字符串解析为 Python 对象
            except json.JSONDecodeError:  # 如果解析失败（可能是心跳包或注释），跳过
                continue

            # 提取必要字段
            msg_type = pkt.get("type")  # 消息类型，例如 answer、follow_up 等
            role = pkt.get("role")  # 消息发送方角色，assistant 或 user
            content = pkt.get("content")  # 消息内容
            msg_id = pkt.get("id")  # 消息 ID

            # 只处理机器人（assistant）发的 answer 类型消息
            if msg_type == "answer" and role == "assistant":
                if current_msg_id is None:  # 如果是当前对话的第一条回答消息
                    current_msg_id = msg_id
                if content:  # 如果有文本内容
                    # 实时输出到终端（流式显示）
                    print(content, end="", flush=True)
                    full_answer.append(content)  # 保存到完整回答列表

    # 当流式对话完成后，打印完整拼接的回答
    print("\n\n====== 模型的完整回复 ======\n")
    print("".join(full_answer))
```

### **7.1.3. Java API**

Java代码中使用Rest API 代码方式与Coze Stdio 中Agent进行对话代码，需要在IDEA中创建Maven项目，并引入如下依赖：

```python
<!--引入jackson依赖，将Java 对象（POJO）序列化为 JSON-->
<dependency>
  <groupId>com.fasterxml.jackson.core</groupId>
  <artifactId>jackson-databind</artifactId>
  <version>2.17.2</version>
</dependency>
```

完整代码如下：

```python
package org.example;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

public class CozeSSEClient {

    // 本地部署的 Coze Studio API 服务地址
    private static final String BASE = "http://node2:8888";
    // 你的 Coze API 访问令牌
    private static final String TOKEN = "pat_2dffc6a017ff0840a5e53a7379bcb870d456edcee6602e00cf9c4f7aa719ee1d";
    // Coze Stdio中机器人 ID
    private static final String BOT_ID = "7536753703852703744";
    // 自定义用户 ID，用于区分不同会话
    private static final String USER_ID = "123";

    //Jackson 的 ObjectMapper 实例，用于 JSON 编解码
    private static final ObjectMapper MAPPER = new ObjectMapper();
    //HttpClient 实例，支持设置超时、发送请求等
    private static final HttpClient CLIENT = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(15))// 设置连接超时为 15 秒
            .build();

    public static void main(String[] args) throws Exception {
        // 1) 创建会话
        String convId = createConversation(BOT_ID);

        // 2) 发起流式对话（SSE）
        String question = "如何保持早起的习惯？";
        String full = chatStream(convId, BOT_ID, USER_ID, question);

        System.out.println("\n\n====== 模型的完整回复 ======");
        System.out.println(full);
    }

    /**
     * 调用 /v1/conversation/create 创建会话，返回 conversation_id
     * */
    private static String createConversation(String botId) throws Exception {
        String url = BASE + "/v1/conversation/create";
        String body = "{\"bot_id\":\"" + escape(botId) + "\"}";// 请求体 JSON 字符串，指定 bot_id

        HttpRequest req = HttpRequest.newBuilder(URI.create(url))
                .timeout(Duration.ofSeconds(30))  // 设置请求超时 30 秒
                .header("Authorization", "Bearer " + TOKEN)  // 授权头
                .header("Content-Type", "application/json") // 内容类型
                .POST(HttpRequest.BodyPublishers.ofString(body, StandardCharsets.UTF_8)) // POST JSON 请求
                .build();

        // 发送请求并以 UTF-8 解码响应
        HttpResponse<String> resp = CLIENT.send(req, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));

        // 如果 HTTP 状态码不是 2xx，抛异常
        if (resp.statusCode() / 100 != 2) {
            throw new IOException("create conversation failed: " + resp.statusCode() + " - " + resp.body());
        }

        // 将响应体 JSON 反序列化为 Map
        Map<String, Object> root = MAPPER.readValue(resp.body(), new TypeReference<>() {});
        // 获取 data 节点
        Map<String, Object> data = (Map<String, Object>) root.get("data");
        if (data == null || data.get("id") == null) {
            throw new IOException("missing conversation id in response: " + resp.body());
        }
        // 返回 conversation_id 字符串
        return String.valueOf(data.get("id"));
    }

    /**
     * 调用 /v3/chat（SSE）进行流式聊天：
     * - 强制以 UTF-8 读取（SSE 规范要求 UTF-8）
     * - 只聚合 type=answer 且 role=assistant 的内容
     * - 同时把流式增量实时打印出来
     */
    private static String chatStream(String conversationId, String botId, String userId, String question) throws Exception {
        // 拼接 URL，conversation_id 作为 query 参数
        String url = BASE + "/v3/chat?conversation_id=" + conversationId;

        // 构造请求体 JSON，包含参数、模式设定和问题内容
        String payload = MAPPER.writeValueAsString(Map.of(
                "bot_id", botId,
                "user_id", userId,
                "stream", true,
                "auto_save_history", true,
                "additional_messages", new Object[]{
                        Map.of("role", "user", "content", question, "content_type", "text")
                }
        ));

        HttpRequest req = HttpRequest.newBuilder(URI.create(url))
                .timeout(Duration.ofSeconds(600))  // 最长允许 600 秒执行时间
                .header("Authorization", "Bearer " + TOKEN)
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(payload, StandardCharsets.UTF_8))
                .build();

        // 接收响应为 InputStream，以便逐行读取 SSE
        HttpResponse<java.io.InputStream> resp =
                CLIENT.send(req, HttpResponse.BodyHandlers.ofInputStream());

        //打印响应体 ，调试可以打开，查看响应体内容，实际运行过程中不要解开，因为读取完响应就没有数据了
        //System.out.println(new String(resp.body().readAllBytes(), StandardCharsets.UTF_8));


        // 检查 HTTP 状态码是否为 2xx，否则抛出异常
        if (resp.statusCode() / 100 != 2) {
            // 如果返回 HTML（可能被错误路由到前端），直接抛异常便于排查
            String err = new String(resp.body().readAllBytes(), StandardCharsets.UTF_8);
            throw new IOException("chat failed: " + resp.statusCode() + " - " + err);
        }

        StringBuilder fullAnswer = new StringBuilder();
        // 创建 BufferedReader，从流中按 UTF-8 解码并读取每行 SSE 数据
        try (BufferedReader br = new BufferedReader(
                new InputStreamReader(resp.body(), StandardCharsets.UTF_8))) {

            String line;
            while ((line = br.readLine()) != null) {
                if (line.isBlank()) continue;         // 跳过空行
                if (!line.startsWith("data:")) continue;  // 只处理以 "data:" 开头的行

                String data = line.substring(5).trim();   // 去除前缀，提取 JSON 字段内容
                if ("[DONE]".equals(data)) break;         // 若为结束标记，则中断循环

                Map<String, Object> pkt;
                try {
                    pkt = MAPPER.readValue(data, new TypeReference<>() {});  // 将 JSON 转 Map
                } catch (Exception ignored) {
                    continue;  // 若解析失败（非 JSON 包），忽略跳过
                }

                // 提取消息字段
                String type = str(pkt.get("type"));
                String role = str(pkt.get("role"));
                String content = str(pkt.get("content"));

                // 只处理机器人 assistant 返回的 answer 类型内容
                if ("answer".equals(type) && "assistant".equals(role) && content != null && !content.isEmpty()) {
                    System.out.print(content);      // 实时打印内容（形成流式体验）
                    System.out.flush();
                    fullAnswer.append(content);     // 收集至最终完整回复
                }
            }
        }
        return fullAnswer.toString();  // 返回最终完整回复文本
    }

    /**
     * 安全转换对象为字符串，null 转 null，否则调用 toString
     **/
    private static String str(Object o) { return o == null ? null : String.valueOf(o); }

    /**
     * 转义 JSON 字符串里的双引号，避免格式错乱
     **/
    private static String escape(String s) { return s.replace("\"", "\\\""); }
}
```

## 7.2. **Chat SDK使用（了解）**

ChatSDK 是 Coze Studio 提供的一个前端开发工具包（Software Development Kit，简称 SDK），用于在网页或应用中快速嵌入并使用 Coze Stdio的智能体（Agent）聊天功能。它封装了与 Coze 平台交互的逻辑，包括消息的发送与接收、会话管理、UI 组件渲染等，让开发者不必从零编写 API 调用和聊天界面逻辑，只需按照提供的接口调用即可实现一个完整的聊天窗口。

简单来说：ChatSDK = Coze Stdio聊天功能的“前端组件+API封装”，需要基于一个React前端项目，只需要配置 Agent ID、Coze Stdio地址和鉴权的Token，就能直接在你的网页/应用中通过组件 &#x3c;ChatFramework/>、&#x3c;ChatSlot/> 即可渲染出完整的聊天界面，从而使用AI 聊天。

注意：React 是一个由 Facebook开发和维护的 前端 JavaScript 框架/库，主要用于构建用户界面（UI），尤其是单页应用（SPA, Single Page Application）。

### 7.2.1. **准备工作**

使用Chat API 必须先将智能体发布为API服务且要设置访问令牌。

* **发布智能体为“Chat SDK”渠道**

使用Chat SDK 前我们需要先在 Coze Stdio里把 Agent 发布到 “Chat SDK” 渠道。智能体发布为“ **Chat SDK** ”渠道之后，才能在前端项目中使用这个智能体。

* **获取访问令牌**

Coze Studio 社区版 API 和 Chat SDK 通过个人访问令牌鉴权。使用Chat SDK之前，你需要先获得访问令牌。 调用扣子 API 时，你需要在 Header 中通过 Authorization 参数指定访问令牌（Access token），扣子服务端会根据访问令牌验证调用方的操作权限。

获取访问令牌的操作步骤如下：

![image.png](./images/40CozeStudio_6779dfea3dd8441a9420b16a5bd66fc8_376ab0.jpg)

### 7.2.2. **安装Node.js**

Node.js 是一个基于 Chrome V8 引擎 的 JavaScript 运行环境，它让 JavaScript 不仅能在浏览器里运行，还可以在服务器或本地电脑的命令行中运行，这样使得 JavaScript 从前端语言扩展成了全栈语言。

nodejs 自带npm（Node Package Manager），npm 是全球最大的开源包管理平台，用来安装、管理各种 JavaScript 库和工具，如 ChatSDK、React、Vite 等。所以使用Chat SDK 必须要安装Node.js ,通过其提供的npm 来安装和管理Chat SDK。

按照如下步骤在Centos7 中安装Node.js ，Coze Studio Chat SDK要求Node.js版本为v18以上，这里安装v18.19.1版本，下载地址：[https://unofficial-builds.nodejs.org/download/release/v18.19.1/node-v18.19.1-linux-x64-glibc-217.tar.xz](https://unofficial-builds.nodejs.org/download/release/v18.19.1/node-v18.19.1-linux-x64-glibc-217.tar.xz)

**1)上传nodejs安装包并配置**

```python
# 将 node-v18.19.1-linux-x64-glibc-217.tar.xz 上传至如下目录
[root@node2 ~]# mkdir -p /software/nodejs && cd /software/nodejs

#解压
[root@node2 nodejs]# tar -xJf node-v18.19.1-linux-x64-glibc-217.tar.xz
[root@node2 nodejs]# mv node-v18.19.1-linux-x64-glibc-217 nodejs-v18
```

**2)****配置环境变量**

```python
[root@node2 nodejs]# vim /etc/profile

#加入如下内容
export NODE_HOME=/software/nodejs/nodejs-v18/
export PATH=$PATH:$NODE_HOME/bin

#保存并生效
[root@node2 nodejs]# source /etc/profile
```

**3) 验证安装**

```python
[root@node2 ~]# node -v
v18.19.1
[root@node2 ~]# npm -v
10.2.4
```

### 7.2.3. **ChatSDK使用**

使用ChatSDK需要有一个前端项目，所以这里首先创建一个前端项目，然后在该项目中使用ChatSDK 与已发布的Agent进行对话。按照如下步骤配置：

**1)** **使用vite初始化一个React项目**

Vite 是一个前端项目构建工具。

```python
[root@node2 ~]# cd ~
#准备一个空目录作为项目根目录
[root@node2 ~]# mkdir coze-chat-demo && cd coze-chat-demo

#在当前目录生成一个基于 React 的 Vite 前端项目骨架
[root@node2 ~]# npm create vite@5 . -- --template react
（需要输入y）

#安装react相关依赖
[root@node2 ~]# npm install react@18.2.0 react-dom@18.2.0

#安装chatsdk
[root@node2 ~]# npm install @coze/chat-sdk@0.1.11-beta.19
```

**2)** **配置App.jsx文件**

在前端项目中，src/App.jsx 是 React 应用的根组件，负责定义整个应用的主结构和布局，也是全局状态与逻辑的入口。它由入口文件 main.jsx 挂载到 index.html 中的指定 DOM 节点，并作为其他页面或功能组件的容器，贯穿应用运行的全程。

创建App.jsx文件，内容如下：

```python
import "@coze/chat-sdk/webCss";
import ChatSdk from "@coze/chat-sdk/webJs";
const { ChatFramework, ChatSlot, ChatType, Language } = ChatSdk;

export default function App() {
  return (
    <div style={{ height: "100vh" }}>
      <ChatFramework
        chat={{
          appId: "7536753703852703744", // 在 Coze 开源版里即智能体ID
          type: ChatType.Bot,
        }}
        setting={{
          apiBaseUrl: "http://node2:8888", // 你的 Coze Studio URL地址
          language: Language.ZH_CN,
          logLevel: "debug",
        }}
        auth={{
          token: "pat_3edb4ddb0689beb7000ff88b5c5e9f9020fc06d82206c9e6abe9eca32ee7194d",                // 你的 Personal Access Token
          onRefreshToken: () => "pat_3edb4ddb0689beb7000ff88b5c5e9f9020fc06d82206c9e6abe9eca32ee7194d", // 刷新后的 token
        }}
        user={{
          id: "demo-user-1",
          name: "Demo User",
        }}
      >
        <ChatSlot className="chat-slot" />
      </ChatFramework>
    </div>
  );
}

```

注意：以上appID 替换为你的Coze中智能体的BotID ;apiBaseUrl替换为你的Coze Stdio URL地址；token替换为你的令牌。

创建好App.jsx后，将该文件上传至前端项目/root/coze-chat-demo/src目录中，替换该目录中的App.jsx文件。

**3) 修改vite.config.js**

进入前端项目/root/coze-chat-demo/中，修改该目录下的vite.config.js文件，全部内容如下：

```python
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',    // 监听所有网卡
    port: 5173,         // 使用固定端口（默认）
    strictPort: true,   // 如果端口占用则报错而不是改端口
  },
})
```

该配置文件中主要配置可以通过非本机节点访问该前端项目。

**4) 启动前端项目测试ChatSDK**

```python
#进入到项目地址
[root@node2 ~]# cd /root/coze-chat-demo/
#启动项目
[root@node2 coze-chat-demo]# npm run dev

> coze-chat-demo@0.0.0 dev
> vite



  VITE v5.4.19  ready in 299 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.179.6:5173/
  ➜  press h + enter to show help

```

启动项目后，在浏览器中直接访问：http://你的ip:5173/ 可以看到前端页面，并可以进行与Agent对话：

![image.png](./images/40CozeStudio_89cf1008f6ad4785b76620b0412d329b_7833db.jpg)

---

> 📌 **[AI 大模型与云原生全栈知识库](./README.md)** / **40. Coze Studio 一站式 AI Agent 核心引擎与开源开发工具**
> 🏠 [返回主页 README](./README.md) | ⚡ [面试 30 分钟速记](./interview/00_面试冲刺30分钟速记卡片.md) | 💻 [白板手写代码](./interview/08_大厂手写代码与白板编程题.md)
