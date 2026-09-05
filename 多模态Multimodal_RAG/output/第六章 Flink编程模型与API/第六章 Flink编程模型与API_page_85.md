### 6.10.3 异步IO代码

Flink中使用异步IO时，代码逻辑如下：

```java
#创建原始数据流
erezStream&lt;String&gt; stream = ...;

#使用Flink异步IO - 顺序输出(每个task中)
erezStream&lt;Tuple2&lt;String, String&gt;&gt; resultStream = Async伪Stream.orderedWait(stream, new AsyncDa

#使用Flink异步IO - 乱序输出
erezStream&lt;Tuple2&lt;String, String&gt;&gt; resultStream = Async伪Stream.unorderedWait(stream, new Async
```

Flink Async I/O 输出提供乱序和顺序两种模式，异步IO实现方法分别为:orderedWait和
unorderedWait，两种方法都有5个参数，解释如下：

* 第一个参数是输入数据流；
* 第二个参数是异步IO的实现类，该类需要继承RichAsyncFunction抽象类。
* 第三个参数是用于完成异步操作超时时间；
* 第四个参数是超时时间单位；
* 第五个参数可以触发的最大异步i/o操作数；

下面我们以Flink通过异步IO方式读取MySQL中的数据为例，分别来演示“异步请求客户端”和“线程池模拟异步请求客户端”两种实现异步请求的使用方式。

#### 6.10.3.1 数据准备

在MySQL中创建表并插入数据：

```sql
#mysql使用库并建表
use mydb;
create table async_tbl(
    id int,
    name varchar(255),
    age int
);

#插入数据
insert into async_tbl values
(1, "a1", 18),
(2, "a2", 19),
(3, "a3", 20),
(4, "a4", 21),
(5, "a5", 22),
```