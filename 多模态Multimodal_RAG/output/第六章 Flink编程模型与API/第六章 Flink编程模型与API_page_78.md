## Scala代码实现

```scala
val env = StreamExecutionEnvironment.getExecutionEnvironment

//导入隐式转换
import org.apache flink api scala._

/**
 * Socket中的数据格式如下:
 * 001,186,187,success,1000,10
 * 002,187,186,fail,2000,20
 * 003,186,188,success,3000,30
 * 004,188,186,success,4000,40
 * 005,188,187,busy,5000,50
 */
val ds: DataStream [String] = env.socketTextStream("node5", 9999)

//定义侧输出流的标签
val outputTag: OutputTag [String] = OutputTag [String] ("side-output")

val mainStream: DataStream [String] = ds.process((value: String, ctx: ProcessFunction [String, String] #Context,
//value 格式: 001,186,187,success,1000,10
val split: Array [String] = value.split(",")
val callType: String = split(3) //通话类型
//判断通话类型
if ("success".equals(callType)) {
  //成功类型,输出到主流
  out.collect(value)
} else {
  //其他类型,输出到侧输出流
  ctx.output(outputTag, value)
}
})

//获取主流
mainStream.print("主流")

//获取侧输出流
mainStream.getSideOutput(outputTag).print("侧输出流")

env.execute()
```

以上代码执行后,向Socket中输入如下数据进行测试。