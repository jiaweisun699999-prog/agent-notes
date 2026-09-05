```java
// },
// JdbcExecutionOptions builder()
//     //批次提交大小, 默认500
//     .withBatchSize(1000)
//     //批次提交间隔间隔时间, 默认0, 即批次大小满足后提交
//     .withBatchIntervalMs(1000)
//     //最大重试次数, 默认3
//     .withMaxRetries(5)
//     .build()
// },
// new JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
//     //mysql8.0版本使用com.mysql.cj.jdbc Drivers
//     .withUrl("jdbc:mysql://node2:3306/mydb?useSSL=false")
//     .withDriverName("com.mysql.jdbc Drivers")
//     .withUsername("root")
//     .withPassword("123456")
//     .build()
// );

SinkFunction<StationLog> jdbcSink = JdbcSink.sink(
    "insert into station_log sid, call_out, call_in, call_type, call_time, duration
    (PreparedStatement pst, StationLog stationLog) -> {
        pst.setString(1, stationLog.getSid());
        pst.setString(2, stationLog.getCallOut());
        pst.setString(3, stationLog.getCallIn());
        pst.setString(4, stationLog.getCallType());
        pst.setLong(5, stationLog.getCallTime());
        pst.setLong(6, stationLoggetDuration());
    },

    JdbcExecutionOptions builder()
        //批次提交大小, 默认500
        .withBatchSize(1000)
        //批次提交间隔间隔时间, 默认0, 即批次大小满足后提交
        .withBatchIntervalMs(0)
        //最大重试次数, 默认3
        .withMaxRetries(5)
        .build(),
    new JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
        //mysql8.0版本使用com.mysql.cj.jdbc Drivers
        .withUrl("jdbc:mysql://node2:3306/mydb?useSSL=false")
        .withDriverName("com.mysql.jdbc Drivers")
        .withUsername("root")
        .withPassword("123456")
        .build()
);
```