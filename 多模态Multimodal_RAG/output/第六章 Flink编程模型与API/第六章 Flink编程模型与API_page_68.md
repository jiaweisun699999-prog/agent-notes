```java
int indexOfThisSubtask = getRuntimeContext().getIndexOfThisSubtask();
if (1 == getRuntimeContext().getIndexOfThisSubtask()) {
    ctx.collect(elem);
}
}
}

@Override
public void cancel() {

}
});

//比较rescale和rebalance的区别
ds.rescale().print("rescale").setParallelism(3);
// ds.rebalance().print("rebalance").setParallelism(4);
env.execute();
```

## • Scala代码实现

```scala
val env = StreamExecutionEnvironment.getExecutionEnvironment
env.setParallelism(2)
```

//导入隐式转换
import org.apache flink api scala._

```scala
val ds: DataStream[Object] = env.addSource[Object](new RichParallelSourceFunction[Object] {
  var isRunning = true

  override def run(ctx: SourceFunction SourceContext[Object]): Unit = {
    val list1 = List[IString]("a", "b", "c", "d", "e", "f")
    val list2 = List[Integer](1, 2, 3, 4, 5, 6)
    list1.forEach(one => {
      if (0 == getRuntimeContext.getIndexOfThisSubtask) {
        ctx.collect(one)
      }
    })
    list2.forEach(one => {
      if (1 == getRuntimeContext.getIndexOfThisSubtask) {
        ctx.collect(one)
      }
    })
  }

  override def cancel(): Unit = {
```