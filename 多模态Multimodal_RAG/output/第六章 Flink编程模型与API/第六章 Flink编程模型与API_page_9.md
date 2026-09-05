```java
this callTime = callTime;
this duration = duration;
}

@Override
public String toString() {
    return "StationLog{
        "sid=" + sid + '"' +
        "callOut=" + callOut + '"' +
        "callIn=" + callIn + '"' +
        "callType=" + callType + '"' +
        "callTime=" + callTime +
        "duration=" + duration +
        '}";
}
}
```

* 读取集合Source Java代码如下：

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
ArrayList<StationLog> stationLogArrayList = new ArrayList<StationLog>();
stationLogArrayList.add(new StationLog("001", "186", "187", "busy", 1000L, 0L));
stationLogArrayList.add(new StationLog("002", "187", "186", "fail", 2000L, 0L));
stationLogArrayList.add(new StationLog("003", "186", "188", "busy", 3000L, 0L));
stationLogArrayList.add(new StationLog("004", "188", "186", "busy", 4000L, 0L));
stationLogArrayList.add(new StationLog("005", "188", "187", "busy", 5000L, 0L));
ibiStreamSource<StationLog> dataStreamSource = env.fromCollectionstationLogArrayList;
dataStreamSource.print();
env.execute();
```

* StationLog对象Scala代码如下：

```scala
/**
 * StationLog基站日志类
 * sid:基站ID
 * callOut: 主叫号码
 * callIn: 被叫号码
 * callType: 通话类型, 失败(fail) / 占线(busy) / 拒接(barring) / 接通 success
 * callTime: 呼叫时间戳, 毫秒
 * duration: 通话时长, 秒
 */
case class StationLog不太String, callOut: String, callIn: String, callType: String, callTime: Long, duration: Long)
```

* 读取集合Source Scala代码如下: