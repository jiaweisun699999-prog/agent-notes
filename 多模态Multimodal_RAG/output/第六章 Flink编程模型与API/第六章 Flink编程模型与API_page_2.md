用不同语言编程导入的包也不同,在获取到对应的Environment后我们还可以进行外参数的配置,
例如:并行度、容错机制设置等。

DataSource部分主要定义了数据接入功能,主要是将外部数据接入到Flink系统中并转换成
erezStream对象供后续的转换使用。Transformation部分有各种各样的算子操作可以对
erezStream流进行转换操作,最终将转换结果数据通过DataSink写出到外部存储介质中,例如:文
件、数据库、Kafka消息系统等。

在erezStream编程中编写完成DataSink代码后并不意味着程序结束,由于Flink是基于事件驱动处
理的,有一条数据时就会进行处理,所以最后一定要使用Environment.execute()来触发程序执行。

6.2.2 Flink数据类型

在Flink内部处理数据时,涉及到数据的网络传输、数据的序列化及反序列化,Flink需要知道操作的
数据类型,为了能够在分布式计算过程中对数据的类型进行管理和判断,Flink中定义了
TypeInformation来对数据类型进行描述,通过TypeInfomation能够在数据处理之前将数据类型推
断出来,而不是真正在触发计算后才识别出,这样可以有效避免用户在编写Flink应用的过程出现数
据类型问题。

常用的TypeInformation有BasicTypeInfo、TupleyerTypeInfo、CaseClassyerTypeInfo、PojoyerTypeInfo
类等,针对这些常用TypeInformation介绍如下:

* Flink通过实现BasicTypeInfo数据类型,能够支持任意Java原生基本(或装箱)类型和String类型,例如:Integer,String,Double等,除了BasicTypeInfo外,类似的还有BasicArrayyerTypeInfo,支持Java中数组和集合类型;
* 通过定义TupleyerTypeInfo来支持Tuple类型的数据;
* 通过CaseClassTypeInfo支持Scala Case Class;
* PojoyerTypeInfo可以识别任意的POJOs类,包括Java和Scala类,POJOs可以完成复杂数据架构的定义,但是在Flink中使用POJOs数据类型需要满足以下要求:
  * POJOs类必须是Public修饰且独立定义,不能是内部类;
  * POJOs 类中必须含有默认空构造器;
  * POJOs类中所有的Fields必须是Public或者具有Public修饰的getter和 Setter方法;

在使用Java API开发Flink应用时,通常情况下Flink都能正常进行数据类型推断进而选择合适的
serializers以及comparators,但是在定义函数时如果使用到了泛型,JVM就会出现类型擦除的问
题,Flink就获取不到对应的类型信息,这就需要借助类型提示(Type Hints)来告诉系统函数中传
入的参数类型信息和输出类型,进而对数据类型进行推断处理。如:

SingleOutputStreamOperator[Tuple2oton, Long] kvWordsDS =
    linesurerseMap((String line, Collector[Tuple2 String, Long] collector) -> {
        String[] words = line.split(" ");