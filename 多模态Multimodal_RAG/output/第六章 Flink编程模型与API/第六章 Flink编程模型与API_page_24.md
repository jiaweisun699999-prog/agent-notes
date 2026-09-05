* `maxBy`: 同`max`类似, 对指定的字段进行max最大值操作, `maxBy`返回的是最大值对应的整个对象。

## Java代码实现

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
//准备集合数据
List<StationLog> list = Arrays.asList(
    new StationLog("sid1", "18600000000", "18600000001", "success", System.currentTimeMillis(), 120L),
    new StationLog("sid1", "18600000001", "18600000002", "fail", System currentTimeMillis(), 30L),
    new StationLog("sid1", "18600000002", "18600000003", "busy", System currentTimeMillis(), 50L),
    new StationLog("sid1", "18600000003", "18600000004", "barring", System currentTimeMillis(), 90L),
    new StationLog("sid1", "18600000004", "18600000005", "success", System currentTimeMillis(), 300L)
);

KeyedStream<StationLog, String> keyedStream = env.fromCollection(list)
    .keyBystationLog -> stationLog sid;
//统计duration的总和
keyedStream.sum("duration").print();
//统计duration的最小值, min返回该列最小值, 其他列与第一条数据保持一致
keyedStream.min("duration").print();
//统计duration的最小值, minBy返回的是最小值对应的整个对象
keyedStream.minBy("duration").print();
//统计duration的最大值, max返回该列最大值, 其他列与第一条数据保持一致
keyedStream.max("duration").print();
//统计duration的最大值, maxBy返回的是最大值对应的整个对象
keyedStream.maxBy("duration").print();

env.execute();
```

## Scala代码实现

```scala
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
// 导入隐式转换
import org.apache.flink api Play

val list: List[StationLog] = List(StationLog("sid1", "18600000000", "18600000001", "success", System.currentTi
    StationLog("sid1", "18600000001", "18600000002", "fail", System currentTimeMillis, 30L),
    StationLog("sid1", "18600000002", "18600000003", "busy", System.currentTimeMillis, 50L),
    StationLog("sid1", "18600000003", "18600000004", "barring", System.currentTimeMillis, 90L),
    StationLog("sid1", "18600000004", "18600000005", "success", System.currentTimeMillis, 300L))

val ds: DataStream[StationLog] = env.fromCollection(list)
val keyedStream: KeyedStream[StationLog, String] = ds.keyBystationLog => stationLog sid

//统计duration的总和
```