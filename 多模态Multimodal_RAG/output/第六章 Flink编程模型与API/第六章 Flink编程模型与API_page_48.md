```java
        * 003,186,188,busy,3000,30
        * 004,188,186,busy,4000,40
        * 005,188,187,busy,5000,50
    */
SingleOutputStreamOperator<StationLog> ds = env.socketTextStream("node5", 9999)
    .map(one -> {
        String[] arr = one.split(",");
        return new StationLog(arr[0], arr[1], arr[2], arr[3], Long valueOf(arr[4]), Long.of
        ).of(arr[5]);
    });
```

```java
//设置JdbcSink ExactlyOnce 对象
SinkFunction<StationLog> jdbcExactlyOnceSink = JdbcSink.exactlyOnceSink(
    "insert into station_log sid,call_out,call_in,call_type,call_time,duration
    ) values(?,?,?,?,?,?)",
    ( href, stationLog ) -> {
        href.setString(1, stationLog.getSid());
        href.setString(2, stationLog.getCallOut());
        href.setString(3, stationLog.getCallIn());
        href.setString(4, stationLog.getCallType());
        href.setLong(5, stationLog.getCallTime());
        href.setLong(6, stationLoggetDuration());
    },
    JdbcExecutionOptions builder()
        //批次提交大小,默认500
        .withBatchSize(1000)
        //批次提交间隔间隔时间,默认0,即批次大小满足后提交
        .withBatchIntervalMs(1000)
        //最大重试次数,默认3,JDBC XA接收器要求maxRetries等于0,否则可能导致重复。
        .withMaxRetries(0)
        .build(),
    JdbcExactlyOnceOptions builder()
        //只允许每个连接有一个XA事务
        .withTransactionPerConnection(true)
        .build(),
    // //创建XA parcer
    // new SerializableSupplier<XADatasource>() {
    //     @Override
    //     public XADatasource get() {
    //         MysqlXADataSource xaDataSource = new com.mysql.jdbc.jdbc2Paym
    //                 xaDataSource.setUrl("jdbc:mysql://node2:3306/mydb?useS
    //                 xaDataSource.setUser("root");
    //                 xaDataSource抛密码("123456");
    //                 return xaDataSource;
    //             }
    //         }
    //     }
    //创建XA parcer对象也可以使用lambda表达式
    () -> {
        MysqlXADataSource xaDataSource = new MysqlXADataSource();
```