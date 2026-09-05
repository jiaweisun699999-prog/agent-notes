```groovy
for (String word : arr) {
    collector.collect(word);
}
)).returns(Types.SSTRING);

//3.将单词转换成Tuple2 KV 类型
MapOperator&lt;String, Tuple2&lt;String, Long&gt; &gt; kvWordsDS =
    wordsDS.map(word -&gt; new Tuple2&lt;&gt;(word, 1L)).returns(Types.TUPLE(Types.SSTRING, Types.LONG));

//4.按照key 进行分组处理得到最后结果并打印
kvWordsDS.groupBy(0).sum(1).print();
```

## • Scala 版本WordCount

使用Flink Scala Dataset api实现WordCount具体代码如下：

```groovy
//1.准备环境,注意是Scala中对应的Flink环境
val env: ExecutionEnvironment = ExecutionEnvironment.getExecutionEnvironment

//2.导入隐式转换,使用Scala API 时需要隐式转换来推断函数操作后的类型
import org.apache flink api scala._

//3.读取数据文件
val linesDS: Dataset String = env.readTextFile("./data/words.txt")

//4.进行 WordCount 统计并打印
linesDS.map(line => {
    line.split(" ")
})
.map((_, 1))
.groupBy(0)
.sum(1)
.print()
```

以上无论是Java api 或者是Scala api 输出结果如下,显示的最终结果是统计好的单词个数。

```
(hello,15)
(Spark,1)
(Scala,2)
(Java,2)
(MapReduce,1)
(Flink,9)
```

## 2.3.2 Flink流式数据处理案例