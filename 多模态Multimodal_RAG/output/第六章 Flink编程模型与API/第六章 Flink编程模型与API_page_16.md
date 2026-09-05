```groovy
//当取消对应的Flink任务时被调用
override def cancel(): Unit = {
    flag = false
}

object NoParallelSource {
    def main(args: Array String): Unit = {
        val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
        import org.apache.flink api Playful._
        val ds: DataStream[StationLog] = env.addSource(new MyDefinedNoParallelSource)
        ds.print()
        env.execute()
    }
}
```

### 6.3.5.2 ParallelSourceFunction接口实现

实现ParallelSourceFunction 接口实现有并行度的自定义Source, Java代码和Scala代码分别如下:

* Java代码

```java
/**
 * Flink读取自定义有并行度的Source,自定义Source实现 ParallelSourceFunction
 */
class MyDefinedParallelSource implements ParallelSourceFunction<StationLog> {
    Boolean flag = true;

    /**
     * 主要方法:启动一个Source,大部分情况下都需要在run方法中实现一个循环产生数据
     * 这里计划1s 产生1条基站数据,由于是并行,当前节点有几个core就会有几条数据
     */
    @Override
    public void run(SourceContext<StationLog> ctx) throws Exception {
        Random random = new Random();
        String[] callTypes = {"fail", "success", "busy", "barring"};
        while flag{
            String sid = "sid_" + random.nextInt(10);
            String callOut = "1811234" + (random.nextInt(9000)+1000);
            String callIn = "1915678" + (random.nextInt(9000)+1000);
            String callType = callTypesrand.nextInt(4);
            Long callTime = System.currentTimeMillis();
            Long durations = Long.valueOf(random.nextInt(50) + "");
            ctx.collect(new StationLog sid, callOut, callIn, callType, callTime, durations));
```