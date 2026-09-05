```xml
</dependency>

 <!-- slf4j&log4j 日志相关包 -->
<dependency>
  <groupId>org.slf4j</groupId>
  < artifactId>slf4j-log4j12 </ artifactId>
  <version> ${slf4j.version} </ version>
</dependency>
<dependency>
  <groupId>org.apache.logging.log4j</groupId>
  < artifactId>log4j-to-slf4j </ artifactId>
  <version> ${log4j.version} </ version>
</dependency>
</dependencies>
```

"FlinkScalaCode" 模块导入Flink Maven依赖如下：

```xml
<properties>
  <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  <maven.compiler.source>1.8</maven.compiler.source>
  <maven.compiler.target>1.8</maven.compiler.target>
  <flink.version>1.16.0</flink.version>
  <slf4j.version>1.7.31</slf4j.version>
  <log4j.version>2.17.1</log4j.version>
  <scala.version>2.12.10</scala.version>
  <scala.binary.version>2.12</scala.binary.version>
</properties>

<dependencies>
  <!-- Flink批和流开发依赖包 -->
  <dependency>
    <groupId>org.apache.flink</groupId>
    < artifactId>flink-scala_${scala.binary.version} </ artifactId>
    <version> ${flink.version} </ version>
  </dependency>
  <dependency>
    <groupId>org.apache.flink</groupId>
    < artifactId>flink-streaming-scala_${scala.binary.version} </ artifactId>
    <version> ${flink.version} </ version>
  </dependency>
  <dependency>
    <groupId>org.apache.flink</groupId>
    < artifactId>flink-clients </ artifactId>
    <version> ${flink.version} </ version>
  </dependency>
</dependencies>
```