```groovy
//初始化资源,准备线程池
override def open parameters: Configuration): Unit = {
    //初始化线程池,第一个参数是线程池中线程的数量,第二个参数是线程池中线程的最大数量,第三个参数是线程池中
    executorService = new ThreadPoolExecutor(10,10,0L,java.util.concurrentTimeUnit.MICROSECONDS,
            new java.util.concurrent LinkedBlockingQueue[Runnable]())
}

//多线程方式处理数据
override def asyncInvoke(input: Int, resultFuture: ResultFuture String): Unit = {
    //使用线程池执行异步任务
    executorService.submit(new Runnable {
        override def run(): Unit = {
            /**
             * 以下两个方法不能设置在open方法中,因为多线程共用数据库连接和pst对象,这样会导致线程不安全
             */
            val conn: Connection =DriverManager.getConnection("jdbc:mysql://node2:3306/mydb?useSSL=false",
                    val pst: PreparedStatement = conn Cry prepareStatement("select id,name,age from async_tbl where id = ?")
            //设置参数
            pst.setInt(1, input)
            //执行查询并获取结果
            val rs = pst executeQuery()
            while(rs!=null && rs.next()) {
                val id: Int = rs.getInt("id")
                val name: String = rs.getString("name")
                val age: Int = rs.getInt("age")
                //将结果返回给Flink
                resultFuture complete(List("id = " +id +",name = " +name +",age = " +age))
            }

            //关闭资源
            pst.close();
            conn.close();
        }
    })
}

/**
 * 异步IO超时处理逻辑,主要避免程序出错。参数如下:
 * 第一个参数是输入数据
 * 第二个参数是异步IO返回的结果
 */
override def timeout(input: Int, resultFuture: ResultFuture String): Unit = {
    resultFuture complete(List("异步IO超时了！！！"))
}
```