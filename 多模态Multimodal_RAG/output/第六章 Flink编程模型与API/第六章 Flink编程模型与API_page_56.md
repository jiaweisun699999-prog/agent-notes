目前Flink RedisConnector仅支持at-least-once语义,我们可以借助Redis数据存储特性可以实现exactly-once语义,例如:利用Redis的Hash结构key不能重复的特性来实现exactly-once语义,将Flink处理的数据流写入到Redis中,在编写代码之前需要在项目中导入如下依赖:

```xml
<dependency>
  <groupId>org.apache.bahir</groupId>
  < artifactId>flink-connector-redis_2.12 </ artifactId>
  <version>1.1.0</ version>
</dependency>
```

## 案例:读取Socket数据统计WordCount实时写入Redis。

* **Java代码实现**

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
/*
 * Socket中输入数据如下:
 * hello,flink
 * hello,spark
 * hello,hadoop
 * hello,java
 */
uloadSource <String> ds1 = env.socketTextStream("node5", 9999);

//统计wordcount
SingleOutputStreamOperator<Tuple2<String, Integer>> result = ds1.map((FlatMapFunction <String, String>)
    String[] arr = s.split(",");
    for (String word : arr) {
        collector.collect(word);
    }
).returns(Types.STRING)
.map(one -> Tuple2.of(one, 1)).returns(Types.TUPLE(Types.STRING, Types.INT))
.keyBy.tp -> tp.f0)
.sum(1);

//准备RedisSink对象
FlinkJedisPoolConfig conf = new FlinkJedisPoolConfig.Builder()
    .setHost("node4")
    .setPort(6379)
    .setDatabase(1)
    .build();

RedisSink<Tuple2<String, Integer>> redisSink = new RedisSink <>(conf, new RedisMapper<Tuple2<String, I
    @Override
    public RedisCommandDescription getCommandDescription()
        //指定Redis命令描述,不需预先创建Redis表
```