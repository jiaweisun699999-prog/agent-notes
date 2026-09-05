```groovy
)).map(one -> {
    val split = one.split(",")
    new Student split(0).etoInt, split(1), split(2).etoInt
}).filter _.id > 1
.print()

env.execute()
}
}
```

## 6.3 Flink Source

Sources模块定义了Stream API中数据输入操作,Flink中内置了很多数据源Source,例如:文件数据源、Socket数据源、集合数据源,同时也支持第三方数据源,例如:Kafka数据源、自定义数据源,下面分别使用Stream API进行演示。

### 6.3.1 File Source

在Flink早先版本读取文本数据我们可以使用`env.readTextFile`方法来实现,在后续版本中该方法被标记过时,建议使用Stream Connectors来完成。这里以读取HDFS中的文件进行演示。

在linux中创建`data.txt`文件,写入如下内容:

```
hello,a
hello,b
hello,c
```

将以上文件上传至HDFS `/flinkdata`目录中:

```sh
#创建HDFS 目录
hdfs dfs -mkdir /flinkdata
#上传数据
hdfs dfs -put ./data.txt /flinkdata/
```

编写Flink读取文件Source代码前,无论是Java API还是Scala API都需要在项目中导入如下依赖:

```xml
 <!-- DataStream files connector -->
<dependency>
<groupId>org.apache.flink</groupId>
<artifactId>flink-connector-files</artifactId>
<version>${flink.version}</version>
```