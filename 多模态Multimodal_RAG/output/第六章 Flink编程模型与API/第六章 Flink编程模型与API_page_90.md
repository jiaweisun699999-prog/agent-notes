```groovy
//创建 JDBCClient 共享对象, 多个 Vertx 客户端可以共享一个 JDBCClient 实例
mysqlClient = JDBCClient.createShared(vertx, config)
}

//实现异步IO的方法,第一个参数是输入,第二个参数是异步IO返回的结果
override def asyncInvoke(input: Int, resultFuture: ResultFuture String): Unit = {
    //获取MySQL连接
    mysqlClient.getConnection(new Handler[AsyncResult[SQLConnection]] {
        override def handle/sqlConnectionAsyncResult: AsyncResult[SQLConnection]): Unit = {
            if(!sqlConnectionAsyncResult failed()) {
                //获取连接
                val connection: SQLConnection = sqlConnectionAsyncResult.result()

                //执行查询
                connection.query("select id,name,age from async_tbl where id = " + input, new Handler[AsyncResult[ResultFuture<
                    Unit]] {
                        override def handle(resultSetAsyncResult: AsyncResult[ ResultSet]): Unit = {
                            if(!resultSetAsyncResult failed()) {
                                //获取查询结果
                                val ResultSet: ResultSet = ResultSetAsyncResult.result()
                                ResultSet.getRows().asScala.forEach(row => {
                                    //返回结果
                                    resultFuture(complete(List(row.encode()))
```