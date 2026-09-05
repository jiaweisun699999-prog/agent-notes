关于Flink状态和容错内容参考后续状态和容错章节。

## 6.6.1 FileSink

Flink1.12版本之前将数据流实时写入到文件中可以通过StreamFileSink对象来完成，Flink1.12版本之后官方建议使用FileSink对象批或者流数据写出到文件，该对象实现了两阶段提交，可以保证数据以exactly-once语义写出到外部文件。

将Flink 处理后的数据写入文件目录中,需注意：

* Flink数据写入HDFS中会以 "yyyy-MM-dd--HH" 的时间格式给每个目录命名,每个目录也叫一个桶。默认每小时产生一个桶,目录下包含了一些文件,每个 sink 的并发实例都会创建一个属于自己的部分文件,当这些文件太大的时候,sink 会根据设置产生新的部分文件。当一个桶不再活跃时,打开的部分文件会刷盘并且关闭(即:将sink数据写入磁盘,并关闭文件),当再次写入数据会创建新的文件。
* 生成新的桶目录及桶内文件检查周期是 withBucketCheckInterval(1000) 默认是一分钟。
* 在桶内生成新的文件规则,以下条件满足一个就会生成新的文件
  * withInactivityInterval : 桶不活跃的间隔时长,如果一个桶最近一段时间都没有写入,那么这个桶被认为是不活跃的,sink 默认会每分钟检查不活跃的桶、关闭那些超过一分钟没有数据写入的桶。【即:桶内的当下文件如果一分钟没有写入数据就会自动关闭,再次写入数据时,生成新的文件】
  * withMaxPartSize : 设置文件多大后生成新的文件,默认128M。
  * withRolloverInterval : 每隔多长时间生成一个新的文件,默认1分钟。
* 在Flink流数据写出到文件时需要开启checkpoint,否则不能保证数据exactly-once写出语义。Flink checkpoint主要用于状态存储和容错,关于checkpoint更多细节参考状态章节。

**案例：读取socket数据写入到本地文件。**

* 在项目中导入如下依赖:

```xml
 <!-- DataStream files connector -->
<dependency>
  <groupId>org.apache.flink</GROUPID>
  <artifactId>flink-connector-files</ARTIFACTID>
  <version>${flink.version}</VERSION>
</dependency>
```

* **Java代码实现**

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
//开启Checkpoint
env.enableCheckpointing(1000);
```