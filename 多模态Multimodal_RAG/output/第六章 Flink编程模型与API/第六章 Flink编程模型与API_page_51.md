Flink的KafkaSink是将数据写入Kafka消息队列的可靠且高性能的输出组件,在大数据实时处理场景中,经过Flink处理分析后的数据写入到Kafka也是常见的场景,Kafka Sink保证写出到Kafka数据的至少一次(at-least-once)和精确一次(exactly-once)语义,确保数据被准确地写入Kafka,避免重复写入或数据丢失。

当然,在实际工作中我们希望Flink程序重启恢复后以exactly-once的方式继续将数据写出到Kafka中,下面我们以exactly-once方式写出到Kafka为例来演示Kafka Sink的使用方式,关于Flink写入Kafka at-least-once和exactly-once的原理,可以参考后续状态章节介绍。

在使用exactly-once语义向Kafka中写入数据时,需要调整transaction.timeout.ms参数值,该参数值表示生产者向Kafka写入数据时的事务超时时间,该值在Flink写入Kafka时默认为3600000ms=1小时。但在Kafka broker中producer生产者事务超时最大时间transaction.max.timeout.ms)不允许超过15分钟,所以需要在代码中设置transaction.timeout.ms值在15分钟以下,需要否则会报错: Unexpected error in InitProducerIdResponse; The transaction timeout is larger than the maximum value allowed by the broker (as configured by transaction.max.timeout.ms)

在编写Java或者Scala代码时,需要在项目中引入如下依赖:

```xml
 <!-- Kafka 依赖包 -->
<dependency>
  <groupId>org.apache.kafka</groupId>
  <artifactId>kafka_2.12</artifactId>
  <version>${kafka.version}</version>
</dependency>

 <!-- Flink Kafka Connector 依赖包 -->
<dependency>
  <groupId>org.apache.flink</groupId>
  <artifactId>flink-connector-kafka</artifactId>
  <version>${flink.version}</version>
</dependency>
```

## 案例：读取Socket中数据实时统计WordCount, 将结果写出到kafka中。

### 1) 启动Kafka, 并创建topic

```
#创建kafka topic
[root@node1 ~]# kafka-topics.sh --bootstrap-server node1:9092,node2:9092,node3:9092 --create --topic flink
```

```
#查看kafka topic 数据
[root@node1 ~]# kafka-console-consumer.sh --bootstrap-server node1:9092,node2:9092,node3:9092 --topic flink
```

### 2) 编写代码