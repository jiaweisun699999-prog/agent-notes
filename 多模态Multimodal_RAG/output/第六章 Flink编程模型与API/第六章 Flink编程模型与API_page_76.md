```groovy
}
});

result.print();
env.execute();
```

## Scala代码实现

```groovy
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
//导入隐式转换
import org.apacheフlinkKAstreaming.apia scaledot_
val ds1: DataStream[(String, Int)] = env.socketTextStream("node5", 9999)
val ds2: DataStream[(String, Int)] = ds1.map(one => {
  val arr: Array[(String)] = one.split(",")
  (arr(0), arr(1). Int)
})
val result: DataStream[(String, Int)] = ds2itecton custom (new Partitionerform String) {
  override def partition(key: String, numPartitions: Int): Int = {
    keyeft Code % numPartitions
  }
}, _ _ 1)
result.print()
env.execute()
```

以上Java或者Scala代码执行时可以在Socket中输入如下数据：

```
a,1
b,2
a,3
b,4
c,5
```

## 6.8 Side Output侧输出

在Flink处理数据流时,常常会面临这样的情况:需要对一个数据源进行处理,该数据源包含不同类型的数据,我们需要将其分割处理。使用filter算子对数据源进行筛选分割会导致数据流的多次复制,从而造成不必要的性能浪费。为了解决这个问题,Flink引入了侧输出(Side Output)机制,该机制可以将数据流进行分割,而无需对流进行复制。使用侧输出时,用户可以通过定义输出标签(Output Tag)来标识不同的侧输出流。在处理数据流时,通过适当的操作符和条件,可以将特定类型的数据发送到相应的侧输出流。