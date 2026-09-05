```kotlin
}

// invoke方法在sink的生命周期内会执行多次,每条数据都会执行一次
override def invoke(currentOne: String, context: SinkFunction.Context): Unit = {
    //解析数据: 001,186,187,busy,1000,10
    val split: Array String] = currentOne.split(",")
    //准备rowkey
    val rowkey = split(0)
    //获取列
    val callOut = split(1)
    val callIn = split(2)
    val callType = split(3)
    val callTime = split(4)
    val duration = split(5)

    //获取表对象
    val table = conn.getTableorg.apache.hadoop.hbase TablesName valueOf("flink-sink-hbase"))
    //准备put对象
    val put = new Put(rowkey_bytes())
    //添加列
    put.addColumn("cf".bytes(), "callOut".bytes(), callOut_bytes())
    put.addColumn("cf".bytes(), "callIn".bytes(), callIn_bytes())
    put.addColumn("cf".bytes(), "callType".bytes(), callType_bytes())
    put.addColumn("cf".bytes(), "callTime".bytes(), callTime_bytes())
    put.addColumn("cf".bytes(), "duration".bytes(), duration_bytes())
    //插入数据
    table.put(put)
    //关闭表
    table.close()
}

// close方法在sink的生命周期内只会执行一次
override def close(): Unit = super.close()
})

denv.execute()
```

### 3) 向Socket中输出数据

```
001,186,187,busy,1000,10
002,187,186,fail,2000,20
003,186,188,busy,3000,30
004,188,186,busy,4000,40
005,188,187,busy,5000,50
```

### 4) 查看HBase中表数据