```java
}
});

// keyedStream.reduce((v1, v2) -> Tuple2.of(v1.f0, v1.f1 + v2.f1)).print();
keyedStream.reduce(new ReduceFunction[Tuple2<String, Integer]]() {
    @Override
    public Tuple2<String, Integer> reduce(Tuple2<String, Integer> v1, Tuple2<String, Integer> v2) throws
            return Tuple2.of(v1.f0, v1.f1 + v2.f1);
}
}).print();

env.execute();
```

## • Scala代码实现

```groovy
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
//导入隐式转换
import org.apacheECTLFLINKSCALA

val ds: DataStream[(String, Int)] = env.fromCollection(List("a", 1),
    ("b", 2),
    ("c", 3),
    ("a", 4),
    ("b", 5)))

ds.keyBy.tp->{tp._1})
  .reduce((v1,v2)->{(v1._1,v1._2+v2._2)}).print()

env.execute()
```

## 6.4.7 union

union算子是Flink流处理框架中数据流合并算子,可以将多个输入的EUR流多个数据流进行合并,并输出一个新的EUR流数据流作为结果,适用于需要将多个数据流合并为一个流的场景。

需要注意的是union合并的数据流类型必须相同,合并之后的数据流包含两个或多个流中所有元素,并且数据类型不变。下图表示将两个流进行合并得到合并后的结果流,并将结果输出到下游。