## java代码

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

KafkaSource[Tuple2<String, String>> kafkaSource = KafkaSource.<Tuple2<String, String>>builder()
    .setBootstrapServers("node1:9092,node2:9092,node3:9092") //设置Kafka 集群节点
    .setTopics("testtopic") //设置读取的topic
    .set GroupId("my-test-group") //设置消费者组
    .setStartingOffsets(Offsets Initializer.latest()) //设置读取数据位置
    .set Deserializer(new KafkaRecordDeserializationSchema[Tuple2<String, String>>() {
        //设置key,value 数据获取后如何处理
        @Override
        public void desynchronize(ConsumerRecord(byte[], byte[]) consumerRecord, Collector[Tuple2<String, String>>>
                String key = null;
                String value = null;
                if(consumerRecord.key() != null){
                    key = new String(consumerRecord.key(), "UTF-8");
                }
                if(consumerRecord.value() != null){
                    value = new String(consumerRecord.value(), "UTF-8");
                }
                collector.collect(Tuple2.of(key, value));
            }
        //设置置返回的二元组类型
        @Override
        public TypeInformation[Tuple2<String, String>> getProducedType() {
            return TypeInformation.of(new TypeHint[Tuple2<String, String>>() {
            });
        }
    })
    .build();

DataStreamSource[Tuple2<String, String>> kafkaDS = env.fromSource(kafkaSource, WatermarkStrategy.no
    kafkaDS.print();

env.execute();
```

## Scala代码如下

```scala
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
import org.apacheomatic.flink api.scala._

val kafkaSource: KafkaSource[(String, String)] = KafkaSource builder[(String, String)]()
```