```kotlin
* 004,188,186,busy,4000,40
* 005,188,187,busy,5000,50
*/
val ds: DataStream(String] = env.socketTextStream("node5", 9999)

//设置FlinkSink
val fileSink: FileSink(String] = FileSink.forRowFormat(new Path("./out/scala-file-out"), new SimpleStringEncoder{}
//设置桶目录检查间隔，默认1分钟
.withBucketCheckInterval(1000 * 60)
//设置滚动策略
.withRollingPolicy(
    DefaultRollingPolicy builder()
    //桶不活跃的间隔时长, 默认1分钟
    .withInactivityInterval Durations.ofSeconds(30))
    //设置文件多大后生成新的文件, 默认128M
    .withMaxPartSize(MemorySize.ofMebiBytes(1024))
    //设置每隔多长时间生成新的文件, 默认1分钟
    .withRolloverInterval(Durations.ofSeconds(10))
    .build()
)
.build()

//写出到文件
ds.sinkTo(fileSink)

env.execute()
```

## 6.6.2 JdbcSink

Flink的JdbcSink是用于将数据写入关系型数据库的输出组件, 它支持灵活的配置和可靠的事务处理, 包括批量写入和并行写入功能。用户可以自定义数据转换逻辑, 并通过提供数据库连接信息和SQL语句来指定目标表和插入操作。

JdbcSink提供了高性能和可靠的方式, 将流处理作业的结果或数据持久化到数据库中, 它支持at-least-once和exactly-once语义, 确保数据被准确写入数据库一次, 避免重复写入或数据丢失的问题。

### 6.6.2.1 at-least-once语义

Flink数据写出到JdbcSink提供了at-least-once写出语义, 如果业务允许可以通过编写upsert 更新 SQL 可以实现精准一次的写出语义。

在使用Flink JdbcSink时使用格式如下: