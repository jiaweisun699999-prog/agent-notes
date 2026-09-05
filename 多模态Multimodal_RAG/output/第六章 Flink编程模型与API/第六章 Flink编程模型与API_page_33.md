```groovy
def env = env.socketTextStream("node5", 9999);
ds.map(new MyMapFunction()).print();

env.execute();
}

private static class MyMapFunction implements MapFunction<String, String> {
    @Override
    public String map(String value) throws Exception {
        //value格式: 001,186,187,busy,1000,10
        String[] split = value.split(",");
        //获取通话时间,并转换成yyyy-MM-dd HH:mm:ss格式
       SimpleirkFormat sdf = new SimpleirkFormat("yyyy-MM-dd HH:mm:ss");
        String beginTime = sdf.format(Long
```

## Scala代码

```groovy
object CommonFunctionTest {
    def main(args: Array String): Unit = {
        val env = StreamExecutionEnvironment.getExecutionEnvironment

        //导入隐式转换
        import org.apache flink api Play

        /**
         * Socket中的数据格式如下:
         * 001,186,187,busy,1000,10
         * 002,187,186,fail,2000,20
         * 003,186,188,busy,3000,30
         * 004,188,186,busy,4000,40
         * 005,188,187,busy,5000,50
         */
        val ds: DataStream [String] = env.socketTextStream("node5", 9999)
```