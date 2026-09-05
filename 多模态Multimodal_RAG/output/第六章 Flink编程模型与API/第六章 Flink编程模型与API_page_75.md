```groovy
}
})

ds1.print("ds1")
val ds2: DataStream(String] = ds1.forward.map(one -> {
    one + "xx"
})
ds2.print("ds2")
env.execute()
```

## 6.7.8 partitionCustom 自定义分区

partitionCustom算子是Flink中用于自定义数据分区的算子,通过实现自定义的分区函数,可以根据特定需求对数据进行灵活的分区操作,实现满足用户定制化的分区策略。在使用partitionCustom算子时需要传入2个参数,第一个参数用户实现的分区器Partitioner对象,该分区器决定流数据去往下游哪些分区,第二个参数指定应用分区器的字段。

* **Java代码实现**

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

/**
 * Socket中输入数据如下格式数据
 * a,1
 * b,2
 * a,3
 * b,4
 * c,5
 */
StreamSource<String> ds1 = env.socketTextStream("node5", 9999);
SingleOutputStreamOperator[Tuple2<String, Integer>> ds2 = ds1.map(one -> {
    String[] arr = one.split(",");
    return Tuple2.of(arr[0], Integer.valueOf(arr[1]));
}).returns(Types.TUPLE(Types.SSTRING, Types.INT));

Stream[Tuple2<String, Integer>> result = ds2rovpartitionCustom(new Partitioner<String>() {
    @Override
    public int partition(String key, int numPartitions) {
        return keyimumCode() % numPartitions;
    }
}, new KeySelector[Tuple2<String, Integer>, String>() {
    @Override
    public String getKey(Tuple2<String, Integer> tp) throws Exception {
        return tp.f0;
    }
```