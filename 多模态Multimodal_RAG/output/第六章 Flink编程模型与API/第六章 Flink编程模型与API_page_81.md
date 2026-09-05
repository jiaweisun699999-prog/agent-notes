```java
    @Override
    public void open(Configuration parameters) throws Exception {
        ValueStateDescriptor<Long> time = new ValueStateDescriptor("time", Long.class);
        timeState = getRuntimeContext(). state(time);
    }

    //每来一条数据,调用一次
    @Override
    public void processElement(StationLog value, KeyedProcessFunction<String, StationLog, String>.Context context) {
        //从状态中获取上次状态存储时间
        Long time = timeState.value();
        //如果时间为null,说明是第一条数据,注册定时器
        if("fail".equals(value callType) && time == null) {
            //获取当前时间
            long nowTime = ctx/timerService().currentProcessingTime();
            //注册定时器,5秒后触发
            long onTime = nowTime + 5000;
            ctx/timerService().registerProcessingTimeTimer(onTime);
            //更新状态
            timeState.update(onTime);
        }

        // 表示有呼叫成功了,可以取消触发器
        if (!value callType.equals("fail") && time != null) {
            ctx/timerService().deleteProcessingTimeTimer(time);
            timeState.clear();
        }

    }

    //定时器触发时调用,执行触发器,发出告警
    @Override
    public void onTimer(long timestamp, KeyedProcessFunction<String, StationLog, String>.OnTimerContext out) {
        out.collect("触发时间:" + timestamp + " 被叫手机号:" + ctx.getCurrentKey() + " 连续5秒呼叫失败!");
        //清空时间状态
        timeState.clear();
    }

}).print();

env.execute();
```

## • Scala代码实现

```groovy
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
//导入隐式转换
import org.apache.flink_api scala._
```