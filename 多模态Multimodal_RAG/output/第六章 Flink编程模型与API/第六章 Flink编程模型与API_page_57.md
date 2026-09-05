```java
return new RedisCommandDescription(RedisCommand.HSET, "flink-java-redis");
}

@Override
public String getKeyFromData(Tuple2<String, Integer> tp) {
    //指定Redis Key
    return tp.f0;
}

@Override
public StringzigValueFromData(Tuple2 <String, Integer> tp) {
    //指定Redis Value
    return tp.f1 + "";
}
});

//将结果写入Redis
result.addSink CompanySink);
env.execute();
```

## Scala代码实现

```scala
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
//设置隐式转换
import org.apache flink api scala_

/**
 * Socket 中输入数据格式:
 * hello,world
 * hello,flink
 * hello,scala
 * hello,spark
 * hello,hadoop
 */
val ds: DataStream [String] = env.socketTextStream("node5", 9999)

//统计wordCount
val result: DataStream[(String, Int)] = ds flatMap (.split (","))
.map( (x, 1))
.keyBy(._1)
.sum(1)

//准备RedisSink对象
val config: FlinkJedisPoolConfig = new FlinkJedisPoolConfig. Builder().setHost("node4").setPort(6379).build()
val redisSink = new RedisSink[(String, Int)] (config, new RedisMapper[(String, Int)] {
    //指定写入Redis的命令
```