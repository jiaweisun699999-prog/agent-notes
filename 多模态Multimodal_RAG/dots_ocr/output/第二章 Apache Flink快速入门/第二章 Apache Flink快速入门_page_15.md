```java
//指定并行度创建本地环境
LocalStreamEnvironment localEnv = StreamExecutionEnvironment.createLocalEnvironment(5);

//指定远程JobManagerIp 和RPC 端口以及运行程序所在Jar包及其依赖包
StreamExecutionEnvironment remoteEnv = StreamExecutionEnvironment.createRemoteEnvironment("JobMa-
```

同样在Scala api 中批和流创建Flink 上下文环境也有以上三种方式,在实际开发中建议批处理使用"
ExecutionEnvironment.getExecutionEnvironment()"方式创建。流处理使用"
StreamExecutionEnvironment.getExecutionEnvironment()"方式创建。

### 3. Flink批和流 Java 和 Scala导入包不同

在编写Flink Java api代码和Flink Scala api代码处理批或者流数据时,引入的
ExecutionEnvironment或StreamExecutionEnvironment包不同,在编写代码时导入错误的包会导致编程有问题。

批处理不同API引入ExecutionEnvironment如下:

```java
//Flink Java api 引入的包
import org.apache.flink api.java ExecutionEnvironment;
//Flink Scala api 引入的包
import org.apache.flink api scala ExecutionEnvironment
```

流处理不同API引入StreamExecutionEnvironment如下:

```java
//Flink Java api 引入的包
import org.apache.flink streaming api environment.StreamExecutionEnvironment;
//Flink Scala api 引入的包
import org.apache.flink streaming api scala.StreamExecutionEnvironment
```

### 4. Flink Java Api中创建Tuple方式

在Flink Java api中创建Tuple2时,可以通过newTuple2方式也可以通过Tuple2.of方式,两者本质
一样。

### 5. Flink Scala api需要导入隐式转换

在Flink Scala api中批处理和流处理代码编写过程中需要导入对应的隐式转换来推断函数操作后的类型,在批和流中导入隐式转换不同,具体如下:

```java
//Scala 批处理导入隐式转换, 使用Scala API 时需要隐式转换来推断函数操作后的类型
import org.apache.flink api scala._
//Scala 流处理导入隐式转换, 使用Scala API 时需要隐式转换来推断函数操作后的类型
import org.apache.flink streaming api scala._
```