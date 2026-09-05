## 2) 编写代码

* **(Java代码实现)**

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

/**
 * socket 中输入数据如下:
 * 001,186,187,busy,1000,10
 * 002,187,186,fail,2000,20
 * 003,186,188,busy,3000,30
 * 004,188,186,busy,4000,40
 * 005,188,187,busy,5000,50
 */
SingleOutputStreamOperator<StationLog> ds = env.socketTextStream("node5", 9999)
    .map(one -> {
        String[] arr = one.split(",");
        return new StationLog(arr[0], arr[1], arr[2], arr[3], Long
        return new StationLog(arr[0], arr[1], arr[2], arr[3], Long
    });

/**
 * mysql中创建的station_log 表结构如下;
 *
 * CREATE TABLE `station_log` (
 *   `sid` varchar(255) DEFAULT NULL,
 *   `call_out` varchar(255) DEFAULT NULL,
 *   `call_in` varchar(255) DEFAULT NULL,
 *   `call_type` varchar(255) DEFAULT NULL,
 *   `call_time` bigint(20) DEFAULT NULL,
 *   `duration` bigint(20) DEFAULT NULL
 * );
 */
//准备JDBC Sink对象
// SinkFunction<StationLog> jdbcSink = JdbcSink.sink(
//     "insert into station_log
//     new JdbcStatementBuilder<StationLog>() {
//         @Override
//         public void accept(aris, StationLog stationLog) throws Exception {
//             pst.setString(1, stationLog.getSid());
//             pst.setString(2, stationLog.getCallOut());
//             pst.setString(3, stationLog.getCallIn());
//             pst.setString(4, stationLog.getCallType());
//             pst.setLong(5, stationLog.getCallTime());
//             pst.setLong(6, stationLoggetDuration());
//         }
```