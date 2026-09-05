```groovy
* Socket中输入数据如下:
* hello,flink
* hello,spark
* hello,hadoop
* hello,java
*/
uloStreamSource <String> ds1 = env.socketTextStream("node5", 9999);

//统计wordcount
SingleOutputStreamOperator <String> result = ds1.map((FlatMapFunction <String, String>) (s, collector) -
    String[] arr = s.split(",");
    for (String word : arr) {
        collector.collect(word);
    }
).returns(Types.STRING)
.map(one -> Tuple2.of(one, 1)).returns(Types.TUPLE(Types.STRING, Types.INT))
.keyBy.tp -> tp.f0)
.sum(1)
.map(one -> one.f0 + "-" + one.f1).returns(Types.STRING);

//准备Flink KafkaSink对象
KafkaSink <String> kafkaSink = KafkaSink . <String> builder()
    .setBootstrapServers("node1:9092, node2:9092, node3:9092")
    //设置事务超时时间,最大不超过kafka broker的事务最大超时时间限制: max.transaction.timeout.ms
    .setProperty("transaction.timeout.ms", 15 * 60 * 1000L + "")
    .setRecord(KafkaRecord serializationSchema . builder()
        .setTopic("flink-topic")
        . sou
        .build()
    )
    .setDeliveryGuarantee(DeliveryGuarantee .EXACTLY_ONCE)
    .build();

//将结果写出到Kafka
result.sinkTo(kafkaSink);

env.execute();
```

## Scala代码实现-只有key

```groovy
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
//设置隐式转换
import org.apache flink api Play
/*
 * Socket 中输入数据格式:
```