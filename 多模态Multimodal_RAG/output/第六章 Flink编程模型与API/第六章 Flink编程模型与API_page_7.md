```xml
</dependency>

 <!--读取HDFS 数据需要的依赖 -->
<dependency>
<groupId>org.apache hadoop</groupId>
<artifactId>hadoop-client</ artifactId>
<version> ${hadoop.version}</version>
</dependency>
```

* **Java代码如下：**

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

/**
 * Flink1.14版本之前读取文件写法
 */
// DataStreamSource<String> dataStream = env.readTextFile("hdfs://mycluster/flinkdata/data.txt");
// dataStream.print();

/**
 * Flink 读取文件最新写法
 */
FileSource<String> fileSource = FileSource.forRecordStreamFormat(
    new TextLineInputFormat(),
    new Path("hdfs://mycluster/flinkdata/data.txt")).build();

ibiStreamSource = env.fromSource(fileSource, WatermarkStrategy.noWatermark

dataStream.print();

env.execute();
```

* **Scala代码如下：**

```scala
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment

import org.apache flink api Play

val fileSource: FileSource [String] = FileSource.forRecordStreamFormat(
    new TextLineInputFormat(),
    new Path("hdfs://mycluster/flinkdata/data.txt")
).build()

val dataStream: DataStream [String] = env.fromSource(fileSource, WatermarkStrategy.noWatermarks(), "file-s")

dataStream.print()
```