```scala
* hello,world
* hello,flink
* hello,scala
* hello,spark
* hello,hadoop
}

val ds: DataStream String = env.socketTextStream("node5", 9999)
//统计wordCount
val result: DataStream String = ds flatMap _.split(",")
.map((_, 1))
.keyBy(_._1)
.sum(1)
.map(t => {
  t._1 + "-" + t._2
})
```

//准备KafkaSink对象
val kafkaSink: KafkaSink String = KafkaSink builder()
.setBootstrapServers("node1:9092, node2:9092, node3:9092")
//设置事务超时时间,最大不超过kafka broker的事务最大超时时间限制: max.transaction.timeout.ms
 PROPERTY("transaction.timeout.ms", 15 * 60 * 1000L + "")
.setRecord(KafkaRecord serialization Schema builder()
.setTopic("flink-topic")
inzideValue serialization Schema(new SimpleStringSchema())
.build()
)
.setDeliveryGuarantee(DeliveryGuarantee EXACTLYONCE)
.build()
```

//将结果写入Kafka
result sinkTo(kafkaSink)
env.execute()

## Scala代码实现-写出有key和value

```scala
object KafkaSink With Key Value Test {
  def main(args: Array String): Unit = {
    val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
    import org.apache.flinkKAstreaming api Play
    val result: DataStream [(String, Int)] = env.socketTextStream("node5", 9999)
      flatMap_.split(",")
      .map((_, 1))
      .keyBy(_._1)
      .sum(1)

  //准备Kafka Sink 对象
}
```