为了方便查看项目运行过程中的日志,需要在两个项目模块中配置log4j.properties配置文件,并放在各自项目src/main/resources资源目录下,没有resources资源目录需要手动创建并设置成资源目录。log4j.properties配置文件内容如下:

log4j rootLogger=ERROR, console
log4j appender console=org.apache.log4j ConsoleAppender
log4j appender console.target=System.out
log4j appender consolelayout=org.apache.log4j PatternsLayout
log4j appender consolelayout.ConversionPattern=%d{HH:mm:ss} %p %c{2}: %m%n

并在两个项目中的Maven pom.xml中添加对应的log4j需要的依赖包,使代码运行时能正常打印结果:

<dependency>
  <groupId>org.slf4j</group Id>
  <artifactId>slf4j-log4j12</artifac Id>
  <version>1.7.36</version>
</dependency>
<dependency>
  <groupId>org.apache.logging.log4j</group Id>
  < artifactId>log4j-to-slf4j</artifac Id>
  <version>2.17.2</version>
</dependency>

## 5. 分别在两个项目模块中导入Flink Maven依赖

"FlinkJavaCode" 模块导入Flink Maven依赖如下:

<properties>
  <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  <maven.compiler.source>1.8</maven.compiler.source>
  <maven.compiler.target>1.8</maven.compiler.target>
  <flink.version>1.16.0</flink.version>
  <slf4j.version>1.7.36</slf4j.version>
  <log4j.version>2.17.2</log4j.version>
</properties>
<dependencies>
  <!-- Flink批和流开发依赖包 -->
  <dependency>
    <group Id>org.apache flink</group Id>
    <artifac Id>flink-clients</artifac Id>
    <version>${flink.version}</version>
  </dependency>
</dependencies>