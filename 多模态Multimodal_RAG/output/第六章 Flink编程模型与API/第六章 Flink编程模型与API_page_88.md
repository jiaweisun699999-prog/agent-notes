```java
        //获取连接
        SQLConnection connection = sqlConnectionAsyncResult.result();

        //执行查询
        connection.query("select id,name,age from async_tbl where id = " + input, new Handler<AsyncResult<io vertx ext sql ResultSet>> {
            @Override
            public void handle(AsyncResult<io vertx ext sql ResultSet> ResultSetAsyncResult) {
                if (resultSetAsyncResult failed()) {
                    System.out.println("查询失败: " + ResultSetAsyncResult.cause().getMessage());
                    return;
                }

                //获取查询结果
                io vertx ext sql ResultSet ResultSetAsyncResult.result();

                //打印查询的结果
                //将查询结果返回给Flink
                ResultSet.getRows().forEach(row -> {
                    resultFuture(complete(Collections
```

• Scala代码实现: