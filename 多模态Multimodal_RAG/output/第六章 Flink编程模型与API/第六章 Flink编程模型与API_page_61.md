```java
p.addColumn Bytes.toBytes("cf"), Bytes.toBytes("duration"), Bytes.toBytes(duration));

//插入数据
table.put(p);

//关闭表对象
table.close();
}

//在Sink 关闭时调用一次, 这里关闭HBase连接
@Override
public void close() throws Exception {
    //关闭连接
    conn.close();
}

});

env.execute();
```

## • Scala代码实现

```scala
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment

/**
 * socket 中输入数据如下:
 * 001,186,187,busy,1000,10
 * 002,187,186,fail,2000,20
 * 003,186,188,busy,3000,30
 * 004,188,186,busy,4000,40
 * 005,188,187,busy,5000,50
 */
val ds: DataStream String = env.socketTextStream("node5", 9999)

ds.addSink(new RichSinkFunction String) {
    var conn: Connection = _

    // open方法在sink的生命周期内只会执行一次
    override def open parameters: Configuration): Unit = {
        val conf: org.apache.hadoop.conf Configuration = HBaseConfiguration.create()
        conf.set("hbase.zookeeper.quorum", "node3,node4,node5")
        conf.set("hbase.zookeeper property.clientPort", "2181")
    }

    //创建连接
    conn = ConnectionFactory.createConnection(conf)
```