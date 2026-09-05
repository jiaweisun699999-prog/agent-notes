(6,"a6",23),
(7,"a7",24),
(8,"a8",25),
(9,"a9",26),
(10,"a10",27);

### 6.10.3.2 异步请求客户端

这里使用Java Vertx来异步连接MySQL,需要在项目依赖包中导入如下依赖:

```xml
 <!-- Flink 异步IO 需要的 Vertx 依赖包 -->
<dependency>
  <groupId>io vertx</groupId>
  <artifactId>vertx-jdbc-client</ artifactId>
  <version> ${vertx.version}</version>
</dependency>
<dependency>
  <groupId>io vertx</groupId>
  < artifactId>vertx-core</ artifactId>
  <version> ${vertx.version}</version>
</dependency>
```

* **Java代码实现:**

```java
yi/**
 * 实现Flink异步IO方式一:使用 Vert.x 实现异步 IO
 * 案例:读取MySQL中的数据
*/
public class AsyncIOTest1 {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        //为了测试效果,这里设置并行度为1
        env.setParallelism(1);
        //准备数据流
        DataStreamSource<Integer> idDS = env.fromCollection Cárrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10));

        /**
         * 使用异步IO,参数解释如下:
         * 第一个参数是输入数据流,
         * 第二个参数是异步IO的实现类,
         * 第三个参数是用于完成异步操作超时时间,
         * 第四个参数是超时时间单位,
         * 第五个参数可以触发的最大异步i/o操作数
         */
        AsyncDataStream.unorderedWait(idDS, new AsyncDatabaseRequest1(), 5000, TimeUnit.MICROSECONDS,
```