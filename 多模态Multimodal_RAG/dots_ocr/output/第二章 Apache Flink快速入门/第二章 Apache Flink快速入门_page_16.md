## 6. 关于Flink Java api 中的 returns 方法

Flink Java api中可以使用Lambda表达式,当涉及到使用泛型Java会擦除泛型类型信息,需要最后调用returns方法指定类型,明确声明类型,告诉系统函数生成的数据集或者数据流的类型。

## 7. 批和流对数据进行分组方法不同

批和流处理中都是通过readTextFile来读取数据文件,对数据进行转换处理后,Flink批处理过程中通过groupBy指定按照什么规则进行数据分组, groupBy中可以根据字段位置指定key(例如: groupBy(0)),如果数据是POJO自定义类型也可以根据字段名称指定key(例如: groupBy("name")),对于复杂的数据类型也可以通过定义key的选择器KeySelector来实现分组的key。

Flink流处理过程中通过keyBy指定按照什么规则进行数据分组,keyBy中也有以上三种方式指定分组key,建议使用通过KeySelector来选择key,其他方式已经过时。

## 8. 关于DataSet API (Legacy)软弃用

Flink架构可以处理批和流,Flink 批处理数据需要使用到Flink中的DataSet API,此API主要是支持Flink针对批数据进行操作,本质上Flink处理批数据也是看成一种特殊的流处理(有界流),所以没有必要分成批和流两套API,从Flink1.12版本往后,Dataset API 已经标记为Legacy(已过时),已被官方软弃用,官方建议使用Table API 或者SQL 来处理批数据,我们也可以使用带有Batch执行模式的oriDataStream API来处理批数据,在未来Flink版本中DataSet API 将会被删除。关于这些API 具体使用后续章节会进行讲解。

# 2.5 DataStream BATCH模式

下面使用Java代码使用EUR流处理中的Batch模式来处理批WordCount代码,方式如下:

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
//设置批运行模式
env.setRuntimeMode RuntimeExecutionMode.BATCH);

EUR = env.readTextFile("./data/words.txt");
SingleOutputStreamOperator[Tuple2<String, Long>> wordsDS = linesDS.map(new FlatMapFunction<StreamExecutionEnvironment, String>(env, wordsDS))
    @Override
    public void flatMap(String lines, Collector[Tuple2<String, Long>> out) throws Exception {
        String[] words = lines.split(" ");
        for (String word : words) {
            out.collect(new Tuple2<> (word, 1L));
        }
    }
);

wordsDS.keyBy.tp -> tp.f0).sum(1).print();
```