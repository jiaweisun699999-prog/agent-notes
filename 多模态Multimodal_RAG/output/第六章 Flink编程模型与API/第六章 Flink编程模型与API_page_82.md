```groovy
//必须设置checkpoint,否则数据不能写入mysql
env.enableCheckpointing(5000)
```

```groovy
/**
 * Socket中输入数据如下:
 * 001,186,187,fail,1000,10
 * 002,186,187,success,2000,20
 * 003,187,188,fail,3000,30
 * 004,187,188,fail,4000,40
 */
val ds: DataStream[StationLog] = env.socketTextStream("node5", 9999)
.map(line => {
    val arr: Array String] = line.split(",")
    StationLog(arr(0).trim, arr(1).trim, arr(2).trim, arr(3).trim, arr(4).trim.toLong, arr(5).trim.toLong)
})
```

```groovy
//设置 被叫号码为key
ds.keyBy(_.callIn).process(new KeyedProcessFunction [String,StationLog,String] {
    //定义一个状态,记录上次通话时间
    lazy val timeState = getRuntimeContext state (new ValueStateDescriptor [Long] "time", classOf [Long])
```

```groovy
//每条数据都会调用一次
override def processElement(value: StationLog, ctx: KeyedProcessFunction [String, StationLog, String] #Context
    //获取当前key对应的状态
    val time: Long = timeState.value()

    //如果该被叫手机号呼叫状态是fail且time为0,说明是第一条数据,注册定时器
    if("fail".equals(value callType) && time == 0) {
        //获取当前时间
        val nowTime: Long = ctx_TIMERService().currentProcessingTime()
        //触发定时器时间为当前时间+5s
        val onTime = nowTime + 5000

        //注册定时器
        ctx_TIMERService().registerProcessingTimeTimer(onTime)

        //更新定时器
        timeState.update(onTime)
    }
```

```groovy
//如果该被叫手机号呼叫状态不是fail且time不为0,表示有呼叫成功了,可以取消触发器
if(!value callType'.equals("fail") && time!=0) {
    //删除定时器
    ctx_TIMERService().deleteProcessingTimeTimer(time)
    //清空时间状态
    timeState.clear()
}
```