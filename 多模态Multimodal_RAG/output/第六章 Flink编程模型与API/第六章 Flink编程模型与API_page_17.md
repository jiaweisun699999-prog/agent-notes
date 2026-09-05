```java
Thread.sleep(1000); //1s 产生一个事件
}
}

//当取消对应的Flink任务时被调用
@Override
public void cancel() {
    flag = false;
}
}

public class ParallelSource {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        DataStreamSource<StationLog> dataStream = env.addSource(new MyDefinedParallelSource());
        dataStream.print();
        env.execute();
    }
}
```

## • Scala代码

```java
/**
 * Flink读取自定义有并行度的Source,自定义Source实现 ParallelSourceFunction
 */
class MyDefinedParallelSource extends ParallelSourceFunction[StationLog] {
    var flag = true

/**
 * 主要方法:启动一个Source,大部分情况下都需要在run方法中实现一个循环产生数据
 * 这里计划每次产生10条基站数据
 */
override def run(ctx: SourceContext[StationLog]): Unit = {
    val random = new Random()
    val callTypes = Array String]("fail", "success", "busy", "barring")

    while (flag) {
        val sid = "sid_" + random.nextInt(10)
        val callOut = "1811234" + (random.nextInt(9000) + 1000)
        val callIn = "1915678" + (random.nextInt(9000) + 1000)
        val callType = callTypes(random.nextInt(4))
        val callTime = System.currentTimeMillis()
        val durations = random.nextInt(50).toLong
        ctx.collect(StationLog sid, callOut, callIn, callType, callTime, durations))
    }
}
```