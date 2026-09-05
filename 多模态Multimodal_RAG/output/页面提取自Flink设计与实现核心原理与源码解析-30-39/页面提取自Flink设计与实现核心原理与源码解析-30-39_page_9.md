### 1.3.1 源码编译

Flink源码编译过程比较简单，主要涉及从GitHub上拉取Flink源码，运行Maven编译命令。

#### 1. 准备编译环境

在运行环境中安装JDK和Maven编译工具，确保JDK版本在1.8以上，Maven编译工具版本在3.0以上。

#### 2. 下载Flink源码

执行Git命令，下载最新版本的Flink源码，本书中用到的版本为1.10。下载完成后，将代码分支切换为release-1.10版本。

```
$ git clone https://github.com/apache/flink.git
```

由于网络延时等原因，下载过程中可能会出现中断的情况，再尝试几次即可。通常情况下，源码下载过程还是比较顺利的。

#### 3. Flink源码编译

进入Flink源码项目路径进行编译。如果不对源码进行编译，在IDEA编译器中会出现Class未被发现的情况，影响阅读源码。执行以下Maven编译命令对源码进行编译，添加-DskipTests参数加速编译速度。

```
$ mvn clean install -DskipTests
```

通过以下命令可以同时屏蔽QA plugins、JavaDocs等编译插件，以达到加速的目的。

```
$ mvn clean install -DskipTests -Dfast
```

see more please visit: https://homeofpdf.com