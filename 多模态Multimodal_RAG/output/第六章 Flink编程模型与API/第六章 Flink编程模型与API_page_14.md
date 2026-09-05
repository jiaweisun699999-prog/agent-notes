* 通过实现SourceFunction接口来自定义无并行度（也就是并行度只能为1）的Source。
* 通过实现ParallelSourceFunction 接口或者继承RichParallelSourceFunction 来自定义有并行度的数据源。

无论是那种接口实现方式都需要重写以下两个方法：

1. run():大部分情况下都需要在run方法中实现一个循环产生数据,通过Flink上下文对象传递到下游。
2. cancel():当取消对应的Flink任务时被调用。

### 6.3.5.1 SourceFunction接口实现

实现SourceFunction 接口实现无并行度的自定义Source,java代码和Scala代码分别如下：

* Java代码

```java
/**
 * 自定义非并行Source
*/
class MyDefinedNoParallelSource implements SourceFunction<StationLog> {
    Boolean flag = true;

/**
 * 主要方法:启动一个Source,大部分情况下都需要在run方法中实现一个循环产生数据
 * 这里计划每秒产生1条基站数据
*/
@Override
public void run(SourceContext<StationLog> ctx) throws Exception {
    Random random = new Random();
    String[] callTypes = {"fail", "success", "busy", "barring"};
    while flag{
        String sid = "sid_" + random.nextInt(10);
        String callOut = "1811234" + (random.nextInt(9000) + 1000);
        String callIn = "1915678" + (random.nextInt(9000) + 1000);
        String callType = callTypesrand.nextInt(4);
        Long callTime = System.currentTimeMillis();
        Long durations = Long.valueOf(random.nextInt(50) + "");
        ctx.collect(new StationLog sid, callOut, callIn, callType, callTime, durations));
        Thread.sleep(1000); //1s 产生一个事件
    }
}

//当取消对应的Flink任务时被调用
```