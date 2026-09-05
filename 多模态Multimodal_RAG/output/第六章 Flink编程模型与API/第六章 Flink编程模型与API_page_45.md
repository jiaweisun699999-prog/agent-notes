```java
//将数据写入到mysql中
ds.addSink(jdbcSink);

env.execute();
```

注意：以上Java代码StationLog对象需要对各属性实现getter、setter方法。

## • Scala代码实现

```scala
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
//导入隐式转换
import org.apache flink streaming api scala._
```

```scala
/**
 * Socket中输入数据如下：
 * 001,186,187,busy,1000,10
 * 002,187,186,fail,2000,20
 * 003,186,188,busy,3000,30
 * 004,188,186,busy,4000,40
 * 005,188,187,busy,5000,50
 */
val ds: DataStream[StationLog] = env.socketTextStream("node5", 9999)
.map(line => {
  val arr: Array String = line.split(",")
  StationLog(arr(0).trim, arr(1).trim, arr(2).trim, arr(3).trim, arr(4).trim.toLong, arr(5).trim.toLong)
})
```