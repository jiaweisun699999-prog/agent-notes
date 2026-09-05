```kotlin
val kafkaSink: KafkaSink[(String, Int)] = KafkaSink builder[(String, Int)]()
.setBootstrapServers("node1:9092,node2:9092,node3:9092")
 PROPERTY("transaction.timeout.ms", 15 * 60 * 1000L + "")
.setRecord(
    KafkaRecord serializationSchema builder()
    .setTopic("flink-topic-2")
    .setKey serializationSchema(new MyKey serializationSchema())
    . value serializationSchema(new MyValue serializationSchema())
    .build()
).setDeliveryGuarantee(DeliveryGuarantee.EXACTLY ONCE)
.build()

result.sinkTo(kafkaSink)

env.execute()
}
}

class MyKey serializationSchema() extends SerializationSchema[(String,Int)]{
    override def serialize(t: (String, Int)): Array[Byte] = t_1_bytes
}

class MyValue serializationSchema() extends SerializationSchema[(String,Int)]{
    override def serialize(t: (String, Int)): Array[Byte] = t_2.toStringurgi
}
```

### 3) 向Socket中输入以下数据，查看Kafka中结果

```
hello,flink
hello,spark
hello,hadoop
hello,java
```

## 6.6.4 RedisSink

Flink官方没有直接提供RedisSink连接器而是通过Apache Bahir项目提供的一个附加的流式连接器: Redis Connector,该连接器用于Apache Flink和Redis之间的数据交互。

注: Apache Bahir是一个扩展项目,旨在为Apache Flink提供额外的流式连接器。这些连接器可以扩展Flink的功能,使其能够与不同的数据源和数据接收器进行无缝集成,其中之一就是Flink RedisConnector。