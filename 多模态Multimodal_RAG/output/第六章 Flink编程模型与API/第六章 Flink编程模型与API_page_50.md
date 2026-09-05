pst.setLong(5, stationLog callTime)
pst.setLong(6, stationLog duration)
}
},
JdbcExecutionOptions builder
//批次提交大小,默认500
.withBatchSize(1000)
//批次提交间隔间隔时间,默认0,即批次大小满足后提交
.withBatchIntervalMs(1000)
//最大重试次数,默认3,JDBC XA接收器要求maxRetries等于0,否则可能导致重复。
withMaxRetries(0)
.build(),
JdbcExactlyOnceOptions builder
//只允许每个连接有一个XA事务
.withTransactionPerConnection(true)
.build(),
//该方法必须new方式,否则会报错The implementation of the XaFacade is not serializable. The object probak
new SerializableSupplier[XADatasource] {
override def get(): XADatasource = {
val xaDataSource = new MysqlXADatasource
xaDataSource.setUrl("jdbc:mysql://node2:3306/mydb?useSSL=false")
xaDataSource.setUser("root")
xaDataSource.setPassword("123456")
xaDataSource
}
}
)
//将数据写入到JdbcSink
ds.addSink(JdbcExactlyOnceSink)
env.execute()

3) 向Socket中输入以下数据查询mysql结果

001,186,187,busy,1000,10
002,187,186,fail,2000,20
003,186,188,busy,3000,30
004,188,186,busy,4000,40
005,188,187,busy,5000,50

6.6.3 KafkaSink