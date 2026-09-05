//5.最后使用execute 方法触发执行
env.execute()

以上输出结果开头展示的是处理当前数据的线程,一个Flink应用程序执行时默认的线程数与当前节点cpu的总线程数有关。

## 2.4 Flink批和流案例总结

关于以上Flink 批数据处理和流式数据处理案例有以下几个点需要注意：

### 1. Flink程序编写流程总结

编写Flink代码要符合一定的流程,Flink代码编写流程如下:

a. 获取flink的执行环境, 批和流不同, Execution Environment。

b. 加载数据-- source。

c. 对加载的数据进行转换-- transformation。

d. 对结果进行保存或者打印-- sink。

e. 触发flink程序的执行 --env.execute()

在Flink批处理过程中不需要执行execute触发执行,在流式处理过程中需要执行env.execute触发程序执行。

### 2. 关于Flink的批处理和流处理上下文环境

创建Flink批和流上下文环境有以下三种方式,批处理上下文创建环境如下:

```
//设置Flink运行环境,如果在本地启动则创建本地环境,如果是在集群中启动,则创建集群环境
ExecutionEnvironment env = ExecutionEnvironment.getExecutionEnvironment();

//指定并行度创建本地环境
LocalEnvironment localEnv = ExecutionEnvironment.createLocalEnvironment(10);

//指定远程JobManagerIp 和RPC 端口以及运行程序所在Jar包及其依赖包
ExecutionEnvironment remoteEnv = ExecutionEnvironment.createRemoteEnvironment("JobManagerHost", 60);
```

流处理上下文创建环境如下:

```
//设置Flink运行环境,如果在本地启动则创建本地环境,如果是在集群中启动,则创建集群环境
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
```