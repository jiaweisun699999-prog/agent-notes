```java
int indexOfThisSubtask = getRuntimeContext().getIndexOfThisSubtask();
if (integer % 2 != 0 && indexOfThisSubtask == 0) {
    ctx.collect integer;
} else if (integer % 2 == 0 && indexOfThisSubtask == 1) {
    ctx.collect integer;
}
}

@Override
public void cancel() {
    flag = false;
}
});

ds1.print("ds1");

SingleOutputStreamOperator<String> ds2 = ds1.forward().map(one -> one + "xx");
ds2.print("ds2");

env.execute();
```

## Scala代码实现

```scala
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
//导入隐式转换
import org.apacheフlinkKAstreaming.Kapi.KSA

val ds1: DataStream[Integer] = env.addSource(new RichParallelSourceFunction[Integer] {
    var flag = true

    override def run(ctx: SourceFunction SourceContext[Integer]): Unit = {
        val list = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        for (elem <- list) {
            val subtask: Int = getRuntimeContext.getIndexOfThisSubtask
            if (elem % 2 != 0 && 0 == subtask) {
                ctx.collect(elem)
            } else if (elem % 2 == 0 && 1 == subtask) {
                ctx.collect(elem)
            }
        }
    }

    override def cancel(): Unit = {
        flag = false
    }
```