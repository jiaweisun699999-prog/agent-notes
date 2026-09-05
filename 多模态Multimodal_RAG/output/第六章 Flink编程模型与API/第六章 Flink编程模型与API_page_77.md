侧输出适合Flink中流分割处理、异常数据处理、延迟数据处理场景，例如常见的延迟数据处理场景中可以通过侧输出避免丢弃延迟到达的数据。关于Flink中延迟到达的数据在后续章节介绍。

案例：Flink读取Socket中通话数据，将成功和不成功的数据信息分别输出。

## Java代码实现

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

/**
 * Socket中的数据格式如下:
 * 001,186,187,success,1000,10
 * 002,187,186,fail,2000,20
 * 003,186,188,success,3000,30
 * 004,188,186,success,4000,40
 * 005,188,187,busy,5000,50
 */
uloStreamSource�ation<St
//定义侧输出流的标签
outpuTag = new OutputTag
SingleOutputStreamOperator
@Override
public void processElement(String value, ProcessFunction
//value 格式: 001,186,187,success,1000,10
String[] split = value.split(",");
String callType = split[3]; //通话类型
//判断通话类型
if ("success".equals(callType)) {
    //成功类型,输出到主流
    out.collect(value);
} else {
    //其他类型,输出到侧输出流
    ctx.output(outputTag, value);
}
}
});

//获取主流
mainStream.print("主流");

//获取侧输出流
mainStream.getSideOutput(outputTag).print("侧输出流");

env.execute();
```