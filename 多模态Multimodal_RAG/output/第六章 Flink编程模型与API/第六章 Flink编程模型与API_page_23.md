```java
KeyedStream[Tuple2<String, Integer>, String> keyedStream = ds.keyBy(new KeySelector[Tuple2<String, Integer>>(
    @Override
    public String getKey(Tuple2<String, Integer> tp) throws Exception {
        return tp.f0;
    }
));

keyedStream.sum(1).print();

env.execute();
```

* **Scala代码实现**

```groovy
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
//导入隐式转换
import org.apache flink api scala_

val ds: DataStream[(String, Int)] = env.fromCollection(List(("a", 1),
    ("b", 2),
    ("c", 3),
    ("a", 4),
    ("b", 5)))

ds.keyBy.tp=>{tp._1}.sum(1).print()
env.execute()
```

## 6.4.5 Aggregations

Aggregations (聚合函数) 是Flink中用于对输入数据进行聚合操作的函数集合, 它们可以应用于 KeyedStream上, 将一组输入元素聚合为一个输出元素。

Flink提供了多种聚合函数, 包括sum、min、minBy、max、maxBy, 这些函数都是常见的聚合操作, 作用如下:

* sum：针对输入keyedStream对指定列进行sum求和操作。
* min：针对输入keyedStream对指定列进行min最小值操作，结果流中其他列保持最开始第一条数据的值。
* minBy：同min类似，对指定的字段进行min最小值操作minBy返回的是最小值对应的整个对象。
* max：针对输入keyedStream对指定列进行max最大值操作，结果流中其他列保持最开始第一条数据的值。