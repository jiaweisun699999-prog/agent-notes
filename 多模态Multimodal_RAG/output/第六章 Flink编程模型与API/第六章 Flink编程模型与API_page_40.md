//方便看到结果设置并行度为2
env.setParallelism(2);

/*

* socket 中输入数据如下：

* 001,186,187,busy,1000,10

* 002,187,186,fail,2000,20

* 003,186,188,busy,3000,30

* 004,188,186,busy,4000,40

* 005,188,187,busy,5000,50

*/

uloader = new DataStreamSource < String > ( "node5" , 9999);

//准备FileSink对象

FileSink < String > fileSink = FileSink .forRowFormat( new Path ( ". / output / java-file-result" ), new SimpleStringEncoder < String > ( "UTF-8" )) //生成新桶目录的检查周期,默认1分钟 .withBucketCheckInterval( 1000) //设置文件滚动策略 .withRollingPolicy( DefaultRollingPolicy .builder() //桶不活跃的间隔时长,默认1分钟 .withInactivityInterval( Duration .ofSeconds(30)) //设置文件多大后生成新的文件,默认128M .withMaxPartSize(MemorySize .ofMebiBytes(1024)) //设置每隔多长时间生成一个新的文件,默认1分钟 .withRolloverInterval( Duration .ofSeconds(10)) .build()).build();

//写出数据到文件
ds.sinkTo(fileSink);

env.execute();

• Scala代码实现

val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
//设置并行度为2,方便测试
env.setParallelism(2)

/*

* Socket中输入数据如下：

* 001,186,187,busy,1000,10

* 002,187,186,fail,2000,20

* 003,186,188,busy,3000,30