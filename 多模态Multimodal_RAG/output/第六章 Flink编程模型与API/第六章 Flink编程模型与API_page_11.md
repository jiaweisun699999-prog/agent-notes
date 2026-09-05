```groovy
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
KafkaSource&lt;String&gt; kafkaSource = KafkaSource.&lt;String&gt;builder()
    .setBootstrapServers("node1:9092,node2:9092,node3:9092") //设置Kafka 集群节点
    .setTopics("testtopic") //设置读取的topic
    .set GROUPId("my-test-group") //设置消费者组
    .setStartingOffsets(Offsets Initializer.latest()) //设置读取数据位置
    . valueOnly Deserializer(new SimpleStringSchema()) //设置value的反序列化格式
    .build();

uloaDS = env.fromSource(kafkaSource, WatermarkStrategy.noWatermarks(), "kafka");
kafkaDS.print();

env.execute();
```

### Scala代码如下：

```groovy
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment

import org.apacheECTL.ecap.ETCLap

val kafkaSource: KafkaSource[String] = KafkaSource builder [String] ()
    .setBootstrapServers("node1:9092,node2:9092,node3:9092") //设置Kafka集群Brokers
    .setTopics("testtopic") //设置topic
    .set GROUPId("my-test-group") //设置消费者组
    .setStartingOffsets(Offsets Initializer.latest()) // 读取位置
    . valueOnly Deserializer(new SimpleStringSchema()) //设置Value的反序列化格式
    .build()

val kafkaDS: DataStream [String] = env.fromSource(kafkaSource, WatermarkStrategy.noWatermarks(), "kafka");
kafkaDS.print()

env.execute()
```

代码编写完成后执行，向kafka testtopic中输入如下数据，可以在控制台看到对应数据结果。

```
[root@node1 bin]# kafka-console-producer.sh --bootstrap-server node1:9092,node2:9092,node3:9092--topic
>value1
>value2
>value3
>value4
>value5
```

## 6.3.4.2 读取Kafka中Key、Value数据