```java
//返回tuple,第一个参数是哪些数据流继续迭代,第二个参数是哪些数据流进行输出
(stillGreatorThanZero, lessThanZero)
})

//打印最后结果
result.print()

env.execute()
```

# 6.5 函数接口与富函数类

## 6.5.1 函数接口

上一小节中学习过的Flink算子方法都有对应的接口来完成业务逻辑处理,我们可以自定义类来实现这些接口完成业务逻辑编写,然后将这些类作为参数传递给Flink算子。这些实现接口在Flink中我们通常称为函数接口,常见的Flink函数接口有:MapFunction、FlatMapFunction、ReduceFunction、FilterFunction等。

无论是Java代码还是Scala代码编写都可以单独实现对应函数接口后当做参数传递给Flink算子,下面举例说明。

**案例：向Socket中输入通话数据，按照指定格式输出每个通话的拨号时间和结束时间。**

向Socket中输入数据格式如下：

```
001,186,187,busy,1000,10
002,187,186,fail,2000,20
003,186,188,busy,3000,30
004,188,186,busy,4000,40
005,188,187,busy,5000,50
```

* **Java代码**

```java
public class CommonFunctionTest {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        /**
         * Socket中的数据格式如下:
         * 001,186,187,busy,1000,10
         * 002,187,186,fail,2000,20
         * 003,186,188,busy,3000,30
         * 004,188,186,busy,4000,40
         * 005,188,187,busy,5000,50
         */
    }
}
```