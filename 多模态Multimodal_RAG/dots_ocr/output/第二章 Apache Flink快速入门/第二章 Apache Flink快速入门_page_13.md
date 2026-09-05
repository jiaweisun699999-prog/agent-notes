## Java 版本WordCount

使用Flink Java DataStream api实现WordCount具体代码如下：

```java
//1.创建流式处理环境
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

//2.读取文件数据
DataStreamSource<String> lines = env.readTextFile("./data/words.txt");

//3.切分单词,设置KV格式数据
SingleOutputStreamOperator[Tuple2<String, Long>> kvWordsDS =
    linesurerse((String line, Collector[Tuple2<String, Long>> collector) -> {
        String[] words = line.split(" ");
        for (String word : words) {
            collector.collect(Tuple2.of(word, 1L));
        }
    }).returns(Types.TUPLE(Types.STRING, Types.LONG));

//4.分组统计获取 WordCount 结果
kvWordsDS.keyBy.tp->tp.f0).sum(1).print();

//5.流式计算中需要最后执行execute方法
env.execute();
```

## Scala 版本WordCount

使用Flink Scala DataStream api实现WordCount具体代码如下：

```scala
//1.创建环境
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment

//2.导入隐式转换,使用Scala API时需要隐式转换来推断函数操作后的类型
import org.apache.flink._

//3.读取文件
val ds: DataStream String = env.readTextFile("./data/words.txt")

//4.进行wordCount统计
ds.map(line => (line.split(" ")))
  .map((_, 1))
  .keyBy._1
  .sum(1)
  .print()
```