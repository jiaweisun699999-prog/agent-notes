如果我们想将Flink处理后的数据输出到外部系统或者其他数据库,但是Flink官方没有提供对应的 Sink输出,这时我们可以使用自定义Sink输出,可以实现SinkFunction接口或者继承 RichSinkFunction类并在其中编写处理数据的逻辑即可完成自定义Sink输出,两者区别是后者增加了生命周期的管理功能。通过自定义Sink函数可以将数据发送到任意选择的目标,非常灵活。

目前在Flink DataStream API中没有提供HBaseSink,下面以读取Socket数据写入HBase为例来介绍自定义Sink输出,实现数据输出到HBase中。在编写代码之前需要在项目中引入如下Maven依赖。

```xml
 <!-- HBase Client 依赖包 -->
<dependency>
  <groupId>org.apache.hbase</groupId>
  <artifactId>hbase-client</ artifactId>
  <version> ${hbase.version}</version>
</dependency>

 <!-- HBase操作HDFS需要依赖包 -->
<dependency>
  <groupId>org.apache.hadoop</groupId>
  <artifactId>hadoop-auth</ artifactId>
  <version> ${hadoop.version}</version>
</dependency>
```

## 1) 在HBase中创建对应的表

```sh
#启动Zookeeper并启动HDFS
#启动HBase
[root@node4 ~]# start-hbase.sh

#进入hbase中创建表 flink-sink-hbase
hbase:006:0> create 'flink-sink-hbase','cf';
Created table flink-sink-hbase
hbase:007:0> list
...
flink-sink-hbase
...
```

## 2) 编写代码

### Java代码实现

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
/*
 * socket 中输入数据如下:
 * 001,186,187,busy,1000,10
 */
```