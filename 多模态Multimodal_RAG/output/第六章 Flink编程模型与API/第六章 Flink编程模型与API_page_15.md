```java
    @Override
    public void cancel() {
        flag = false;
    }
}

/**
 * Flink读取自定义Source，并行度为1
 */
public class NoParallelSource {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        DataStreamSource<StationLog> dataStream = env.addSource(new MyDefinedNoParallelSource());
        dataStream.print();
        env.execute();
    }
}
```

## Scala 代码

```scala
/**
 * Flink读取自定义Source，并行度为1
 */
class MyDefinedNoParallelSource extends SourceFunction[StationLog] {
    var flag = true

/**
 * 主要方法:启动一个Source,大部分情况下都需要在run方法中实现一个循环产生数据
 * 这里计划每次产生10条基站数据
 */
override def run(ctx: SourceFunction SourceContext[StationLog]): Unit = {
    val random = new Random()
    val callTypes = Array[String]("fail", "success", "busy", "barring")

    while (flag) {
        val sid = "sid_" + random.nextInt(10)
        val callOut = "1811234" + (random.nextInt(9000) + 1000)
        val callIn = "1915678" + (random.nextInt(9000) + 1000)
        val callType = callTypes(random.nextInt(4))
        val callTime = System.currentTimeMillis()
        val durations = random.nextInt(50).toLong
        ctx.collect(StationLog sid, callOut, callIn, callType, callTime, durations))
    }
    Thread.sleep(1000) //每条数据暂停1s
}
```