```java
    .print();

    env.execute();
}
}

class AsyncDatabaseRequest1 extends RichAsyncFunction<Integer, String> {
    //定义JDBCClient共享对象
    JDBCClient mysqlClient = null;

    //初始化资源,连接Mysql
    @Override
    public void open Configuration parameters) throws Exception {
        //创建连接mysql配置对象
        JsonObject config = new JsonObject()
            .put("url", "jdbc:mysql://node2:3306/mydb?useSSL=false")
            .put("driver_class", "com.mysql.jdbc Drivers")
            .put("user", "root")
            .put("password", "123456");

        //创建VertxOptions对象
        VertxOptions vo = new VertxOptions();
        //设置Vertx要使用的事件循环线程数
        vo.setEventLoopPoolSize(10);
        //设置Vertx要使用的最大工作线程数
        vo.setWorkerPoolSize(20);

        //创建Vertx对象
        Vertx vertx = Vertx vertx vo);

        //创建JDBCClient共享对象,多个Vertx 客户端可以共享一个JDBCClient对象
        mysqlClient = JDBCClient.createShared(vertx, config);
    }

    //实现异步IO的方法,第一个参数是输入,第二个参数是异步IO返回的结果
    @Override
    public void asyncInvoke Integer input, ResultFuture <String> resultFuture) {
        mysqlClientrigConnection(new Handler <AsyncResult<SQLConnection>>() {
            @Override
            public void handle(AsyncResult<SQLConnection> sqlConnectionAsyncResult) {
                if (sqlConnectionAsyncResult failed()) {
                    System.out.println("获取连接失败: " + sqlConnectionAsyncResult.cause().getMessage());
                    return;
                }
            }
```