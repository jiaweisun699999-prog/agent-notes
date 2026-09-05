```java
//关闭资源
@Override
public void close() throws Exception {
    //关闭线程池
    executorService.shutdown();
}
}
```

## • Scala代码

```java
/**
 * 实现Flink异步IO方式二:线程池模拟异步客户端
 * 案例:读取MySQL中的数据
 */
object AsyncIOTest2 {
    def main(args: Array String): Unit = {
        val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
        //为了测试效果,这里设置并行度为1
        env.setParallelism(1)

        //导入隐式转换
        import org.apache flink streaming api scala._

        //准备数据流
        val idDS: DataStream [Int] = env.fromCollection (List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10))

    /**
     * 使用异步IO,参数解释如下:
     * 第一个参数是输入数据流,
     * 第二个参数是异步IO的实现类,
     * 第三个参数是用于完成异步操作超时时间,
     * 第四个参数是超时时间单位,
     * 第五个参数可以触发的最大异步i/o操作数
     */
        AsyncDataStream.unorderedWait (idDS, new AsyncDatabaseRequest2(), 5000, java.util.concurrentTimeUnit print ()

        env.execute()
    }
}

class AsyncDatabaseRequest2 extends RichAsyncFunction [Int, String]() {
    //准备线程池对象
    var executorService: ExecutorService = null
```