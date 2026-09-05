```java
public void onTimer(long timestamp, ProcessFunction<对象类型, 返回对象类型, >.OnTimerContext ctx, Collector<...>
}
```

onTimer()方法有三个参数:时间戳(timestamp)、上下文(ctx)和收集器(out)。
timestamp 是设定好的触发时间,通常与水位线(watermark)相关。方法中可以使用上下文和收集器执行相应的操作,包括使用定时服务(TimerService)和输出处理后的数据。

总而言之,Flink 的 ProcessFunction 提供了强大的灵活性,可以实现各种自定义的业务逻辑,可以实现各种基本转换操作,如 flatMap、map 和 filter,通过获取上下文的方法还可以自定义状态进行聚合操作。同时,ProcessFunction 也支持定时触发操作,可以根据时间来分组数据,并在指定的时间触发计算和输出结果,实现窗口 window的功能。

**案例:** Flink读取Socket中通话数据,如果被叫手机连续5s呼叫失败生成告警信息。(注意:该案例涉及到状态编程,这里我们只需要了解状态意思即可,后续章节会详细讲解状态)

## Java代码实现

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
//必须设置checkpoint,否则数据不能正常写出到mysql
env.enableCheckpointing(5000);
/*
 * socket 中输入数据如下:
 * 001,186,187,fail,1000,10
 * 002,186,187,success,2000,20
 * 003,187,188,fail,3000,30
 * 004,187,188,fail,4000,40
 * 005,188,187,busy,5000,50
 */
SingleOutputStreamOperator<StationLog> ds = env.socketTextStream("node5", 9999)
    .map(one -> {
        String[] arr = one.split(",");
        return new StationLog(arr[0], arr[1], arr[2], arr[3], Long.valueOf(arr[4]), Long.valueOf(arr[5]));
    });

//按照被叫号码分组
KeyedStream<StationLog, String> keyedStream = ds.keyBystationLog -> stationLog.getCallIn());

//使用ProcessFunction实现通话时长超过5秒的告警
keyedStream.process(new KeyedProcessFunction<String, StationLog, String>() {
    //使用状态记录上一次通话时间
    ValueState(Long) timeState = null;

    //在open方法中初始化记录时间的状态
```