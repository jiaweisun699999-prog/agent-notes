```java
//设置最大重试次数，默认3
withMaxRetries(5)
.build(),
new JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
    .withUrl("jdbc:mysql://node2:3306/mydb?useSSL=false")
    .withDriverName("com.mysql.jdbc Drivers")
    .withUsername("root")
    .withPassword("123456")
    .build()
)

//数据写出到MySQL
ds.addSink(jdbcSink)
env.execute()
```

**注意**：在编写Scala JdbcSink代码时，JdbcSink.sink第二个参数不能使用Scala匿名函数写法，否则会报错：“ The implementation of the RichOutputFormat is not serializable. The object probably contains or references non serializable fields.”

### 3) 向Socket中输入以下数据查询mysql结果

```
001,186,187,busy,1000,10
002,187,186,fail,2000,20
003,186,188,busy,3000,30
004,188,186,busy,4000,40
005,188,187,busy,5000,50
```

## 6.6.2.2 exactly-once语义

从Flink1.13版本开始，Flink JDBC Sink支持exactly-once写出语义，该实现依赖于数据库支持支持XA标准规范，目前大多数数据库都支持XA，即如果数据库支持XA标准规范，就支持Flink JDBC Sink的Exactly-once的写出语义。

备注：XA标准是由 X/Open 组织提出的分布式事务规范。目前，Oracle、Informix、DB2和MySQL等各大数据库厂家都提供对XA标准的支持。XA标准规范采用两阶段提交方式来管理分布式事务。

使用Flink JdbcSink Exactly-once语义将数据写出到外部存储库时需要注意：

* Flink写出数据必须开启checkpoint否则不能正常将数据写出,checkpoint周期决定了写出数据的延迟大小。
* JDBC XA接收器要求maxRetries等于0，否则可能导致重复，代码中JdbcExecutionOptions需要设置maxRetries为0。