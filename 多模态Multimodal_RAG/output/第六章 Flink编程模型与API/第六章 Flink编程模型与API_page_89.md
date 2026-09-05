```kotlin
/**
 * 实现Flink异步IO方式一:使用 Vert.x 实现异步 IO
 * 案例:读取MySQL中的数据
 */
object AsyncIOTest1 {
    def main(args: Array String): Unit = {
        val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
        //为了测试效果,这里设置并行度为1
        env.setParallelism(1)

        //导入隐式转换
        import org.apache.flink streaming api scala._

        //准备数据流
        val idDS: DataStream [Int] = env.fromCollection (List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10))

        AsyncStream. unorderedWait (idDS, new AsyncDatabaseRequest1(), 5000, java.util.concurrentTimeUnit print ()

        env.execute ()
    }
}

class AsyncDatabaseRequest1 extends RichAsyncFunction [Int, String]() {

    //定义JDBCClient对象
    var mysqlClient: JDBCClient = null

    //初始化资源,连接MySQL
    override def open (parameters: Configuration): Unit = {
        //创建连接MySQL的配置信息
        val config: JsonObject = new JsonObject ()
            .put("url", "jdbc:mysql://node2:3306/mydb?useSSL=false")
            .put("driver_class", "com.mysql.jdbc.Driver")
            .put("user", "root")
            .put("password", "123456")

        //创建VertxOptions对象
        val vo = new VertxOptions ()
        //设置Vertx要使用的事件循环线程数
        vo.setEventLoopPoolSize (10)
        //设置Vertx要使用的最大工作线程数
        vo.setWorkerPoolSize (20)

        //创建Vertx对象
        val vertx = io vertx core Vertx vertx (vo)
```