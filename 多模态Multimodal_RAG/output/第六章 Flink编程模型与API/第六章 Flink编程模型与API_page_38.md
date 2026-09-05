```kotlin
rst = pst.executeQuery()
while (rst.next()) {
    callOutName = rst.getString("name")
}

pst.setString(1, callIn)
rst = pst.executeQuery()
while (rst.next()) {
    callInName = rst.getString("name")
}

s"基站ID:$sid,主叫号码:$callOut,主叫姓名:$callOutName," +
  s"被叫号码:$callIn,被叫姓名:$callInName,通话类型:$callType," +
  s"通话时间:$callTime,通话时长:$duration"
}

// close()方法在map方法之后执行,用于清理
override def close(): Unit = {
    if (rst != null) rst.close()
    if (pst != null) pst.close()
    if (conn != null) conn.close()
}
}
}
```

### 3) 启动代码,向Socket中输入如下数据

```
001,186,187,busy,1000,10
002,187,186,fail,2000,20
003,186,188,busy,3000,30
004,188,186,busy,4000,40
005,188,187,busy,5000,50
```

## 6.6 Flink Sink

Flink Sink负责将通过Transformation转换的数据流进行输出, Flink官方提供了内置的Sink连接器, 例如: FileSink Connector、JDBCSink Connector、KafkaSink Connector等, 同时也支持自定义Sink输出, 简而言之, Flink的Sink模块让用户能够轻松地将计算结果输出到各种目标位置, 满足不同的业务需求。

Flink提供了容错机制,可以在各种故障情况下恢复程序执行,并通过快照机制和检查点机制实现了一致性状态更新和记录传递的保证, Flink 官方提供的Sink Connector连接器至少支持at-least-once写出语义保证,具体的保证语义取决于所使用的Sink Connector连接器,例如FileSink、KafkaSink都支持exactly-once写出语义。