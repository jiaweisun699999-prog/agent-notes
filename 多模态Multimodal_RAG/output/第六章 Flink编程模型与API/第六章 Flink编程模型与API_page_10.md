```groovy
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment

import org.apache flink api scala._

val arrays: Array[StationLog] = Array(StationLog("001", "186", "187", "busy", 1000L, 0L),
StationLog("002", "187", "186", "fail", 2000L, 0L),
StationLog("003", "186", "188", "busy", 3000L, 0L),
StationLog("004", "188", "186", "busy", 4000L, 0L),
StationLog("005", "188", "187", "busy", 5000L, 0L))

val dataStream: DataStream[StationLog] = env.fromCollection arrays
dataStream.print()

env.execute()
```

除了以上可以从集合中获取ibiStream之外，类似的还有从多个元素对象获取对应的ibiStream
方法如下：

```
env.fromElements(elem1, elem2, elem3...)
```

集合Source也常用于程序测试。

### 6.3.4 Kafka Source

在实时处理场景中Flink读取kafka中的数据是最常见的场景, Flink在操作Kafka时天生支持容错、数据精准消费一次, 所以Flink与Kafka是一对“黄金搭档”, 关于两者整合容错机制原理在后续章节再介绍, 这里主要从API层面实现Flink操作Kafka数据, Flink读取Kafka中的数据需要配置Kafka Connector依赖, 依赖如下:

```xml
 <!-- 读取Kafka 依赖 -->
<dependency>
    <groupId>org.apache flink</groupId>
    <artifactId>flink-connector-kafka</ artifactId>
    <version>${flink.version}</version>
</dependency>
```

读取Kafka中的数据时可以选择读取每条数据的key和value,也可以选择只读取Value,两者API写法不同。

#### 6.3.4.1 读取Kafka中Value数据

* Java代码如下