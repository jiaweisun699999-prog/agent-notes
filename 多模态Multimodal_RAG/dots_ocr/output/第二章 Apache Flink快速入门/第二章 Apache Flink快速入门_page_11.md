在项目"MyFlinkCode"中创建"data"目录,在目录中创建"words.txt"文件,向文件中写入以下内容,方便后续使用Flink编写WordCount实现代码。

```
hello Flink
hello MapReduce
hello Spark
hello Flink
hello Flink
hello Flink
hello Flink
hello Java
hello Scala
hello Flink
hello Java
hello Flink
hello Scala
hello Flink
hello Flink
```

## 2.3 Flink案例实现

数据源分为有界和无界之分,有界数据源可以编写批处理程序,无界数据源可以编写流式程序。
DataSet API用于批处理, DataStream API用于流式处理。

批处理使用ExecutionEnvironment和DataSet,流式处理使用StreamingExecutionEnvironment和ibiStream。DataSet和ibiStream是Flink中表示数据的特殊类,DataSet处理的数据是有界的,ibiStream处理的数据是无界的,这两个类都是不可变的,一旦创建出来就无法添加或者删除数据元。

### 2.3.1 Flink 批数据处理案例

* **Java 版本WordCount**

使用Flink Java Dataset api实现WordCount具体代码如下：

```
ExecutionEnvironment env = ExecutionEnvironment.getExecutionEnvironment();

//1.读取文件
DataSource<String> linesDS = env.readTextFile("./data/words.txt");

//2.切分单词
FlatMapOperator<String, String> wordsDS =
    linesDS.map((String lines, Collector<String> collector) -> {
        String[] arr = lines.split(" ");
```