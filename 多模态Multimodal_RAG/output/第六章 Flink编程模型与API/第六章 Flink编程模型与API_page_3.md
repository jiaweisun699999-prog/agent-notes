```java
for (String word : words) {
    collector.collect(Tuple2.of(word, 1L));
}
}).returns(Types.TUPLE(Types.SSTRING, Types.LONG));
```

在使用Scala API 开发Flink应用时, Scala API通过使用Manifest和类标签在编译器运行时获取类型信息, 即使在函数定义中使用了泛型, 也不会像Java API出现类型擦除问题, 但是在使用到Flink已经通过TypeInformation定义的数据类型时, TypeInformation类不会自动创建, 需要使用隐式参数的方式引入: `import org.apache.flink api scala._`, 否则在运行代码过程中会出现“could not find implicit value for evidence parameter of type TypeInformation”的错误。

### 6.2.3 Flink序列化机制

在两个进程进行远程通信时, 它们需要将各种类型的数据以二进制序列的形式在网络上传输, 数据发送方需要将对象转换为字节序列, 进行序列化, 而接收方则将字节序列恢复为各种对象, 进行反序列化。对象的序列化有两个主要用途: 一是将对象的字节序列永久保存到硬盘上, 通常存放在文件中; 二是在网络上传输对象的字节序列。序列化的好处包括减少数据在内存和硬盘中的占用空间, 减少网络传输开销, 精确推算内存使用情况, 降低垃圾回收的频率。

Flink序列化机制负责在节点之间传输数据时对数据对象进行序列化和反序列化, 确保数据的正确性和一致性。Flink提供了多种序列化器, 包括Kryo、Avro和Java序列化器等, 大多数情况下, 用户不用担心flink的序列化框架, Flink会通过TypeInfomation在数据处理之前推断数据类型, 进而使用对应的序列化器, 例如: 针对标准类型(`int`,`double`,`long`,`string`)直接由Flink自带的序列化器处理, 其他类型默认会交给Kryo处理。但是对于Kryo仍然无法处理的类型, 可以采取以下两种解决方案:

#### 1) 强制使用Avro替代Kryo序列化

```java
//设置flink序列化方式为avro
env.getConfig().enableForceAvro();
```

#### 2) 自定义注册Kryo序列化

```java
//注册kryo 自定义序列化器
env.getConfig().registerTypeWithKryoSerializer(Class<? extends Sanchezizer> deserializerClass)
```

下面给出Java和Scala自定义注册Kryo序列化器的方式, 代码如下:

* **Java代码自定义类及自定义序列化:**

```java
public class Student {
    public Integer id;
    public String name;
    public Integer age;
```