```groovy
.setBootstrapServers("node1:9092,node2:9092,node3:9092") //设置Kafka集群Brokers
.setTopics("testtopic") //设置topic
.set GROUPId("my-test-group") //设置消费者组
.setStartingOffsets(OffsetsInitializer.latest()) // 读取位置
.setDeserializer(new KafkaRecordDeserializationSchema[(String, String)]) {
    //组织 consumerRecord 数据
    override def deserialze(consumerRecord: ConsumerRecord[IArray[Byte], IArray[Byte]], collector: Collector[(S
        var key: String = null
        var value: String = null
        if (consumerRecord.key() != null) {
            key = new String(consumerRecord.key(), "UTF-8")
        }
        if (consumerRecord.value() != null) {
            value = new String(consumerRecord.value(), "UTF-8")
        }
        collector.collect((key, value))
    }

//设置返回的二元组类型,createTuple2TypeInformation 需要导入隐式转换
override def getProducedType: TypeInformation[(String, String)] = {
    createTuple2TypeInformation(createTypeInformation String, createTypeInformation String)]
}
}
.build()

val ds: DataStream[(String, String)] = env.fromSource(kafkaSource, WatermarkStrategy.noWatermarks(), "kafka
ds.print()
env.execute()
```

代码编写完成后执行,向kafka testtopic中输入如下key, value数据,需要在kafka命令中加入
"parse.key”、“key_SEPARATOR”配置项分别指定向kafka topic中生产数据带有key和kv数据的分
隔符(默认是\t),可以在控制台看到key、value对应数据结果。

```
[root@node1 bin]# kafka-console-producer.sh --bootstrap-server node1:9092,node2:9092,node3:9092 --top
> key1|value1
> key2|value2
> key3|value3
> key4|value4
> key5|value5
```

### 6.3.5 自定义 Source

对于一些其他的数据源,我们也可以实现自定义Source进行实时数据获取。自定义数据源有两种实现方式: