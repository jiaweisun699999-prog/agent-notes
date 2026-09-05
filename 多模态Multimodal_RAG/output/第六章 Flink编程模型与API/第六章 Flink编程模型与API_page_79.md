```
001,186,187,success,1000,10
002,187,186,fail,2000,20
003,186,188,success,3000,30
004,188,186,success,4000,40
005,188,187,busy,5000,50
```

## 6.9 ProcessFunction

Flink 的 ProcessFunction 是 DataStream API 中的一个重要组成部分, 它允许用户为流数据定义自定义的处理逻辑。ProcessFunction 提供了一种强大的机制, 用于低级别的流转换, 并完全控制数据事件、状态和时间。

ProcessFunction 是一个抽象类, 继承自 AbstractRichFunction富函数抽象类, 并有两个泛型类型参数: I (输入) 和 O (输出), 表示输入和输出的数据类型, 富函数类中拥有的方法 ProcessFunction 中都可以使用。

ProcessFunction 中有两个核心方法, 如下:

* `processElement()` 方法

这个方法用于处理每个元素, 对于流中的每个元素, 都会调用一次。它的参数包括输入数据值 value、上下文 `ctx` 和收集器 `out`。方法没有返回值, 处理后的输出数据是通过收集器 `out` 定义的。

```java
public void processElement(对象类型 value, ProcessFunction<对象类型, 返回对象类型, >.Context ctx, Collector<...>
)
```

* `value`: 表示当前流中正在处理的输入元素, 类型与流中数据类型一致。

* `ctx`: 表示当前运行的上下文, 可以获取当前的时间戳, 并提供了定时服务 (TimerService), 用于查询时间和注册定时器, 还可以将数据发送到侧输出流 (side output)。

* `out`: 表示输出数据的收集器, 使用 `out.collect()` 方法可以向下游发出一个数据。

* `onTimer()` 方法

这个方法用于定义定时触发的操作, 只有在注册的定时器触发时才会调用。定时器是通过 TimerService 注册的, 相当于设定了一个闹钟, 到达设定的时间就会触发。

注册定时器方法如下:

```java
ctx[timerService().registerProcessingTimeTimer(定时器触发时间)];
```

定时器触发后调用`onTimer`方法如下: