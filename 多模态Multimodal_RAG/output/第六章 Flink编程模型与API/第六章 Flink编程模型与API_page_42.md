```java
JdbcSink.sink(
    sqlDmlStatement, // 必须指定, SQL语句
    jdbcStatementBuilder, // 必须指定, 给SQL语句设置参数
    jdbca執行Option, // 可选, 指定写出参数, 如: 提交周期、提交批次大小、重试时间, 建议指定。
    jdbcconnectionOptions // 必须指定, 数据库连接参数
);
```

在编写Scala代码时, `JdbcStatementBuilder`参数必须通过`new JdbcStatementBuilder`方式创建,
不能使用Scala匿名函数Lambda方式编写, 否则代码报序列化错误不能正常运行, 该错误与Scala编译器版本有关。

在编写Java和Scala代码之前需要导入项目依赖：

```xml
 <!-- Flink JdbcSink依赖jar包 -->
<dependency>
    <groupId>org.apache flink</groupId>
    <artifactId>flink-connector-jdbc</ artifactId>
    <version> ${flink-connector-jdbc.version}</version>
</dependency>
 <!-- MySQL驱动依赖jar包 -->
<dependency>
    <groupId>mysql</groupId>
    < artifactId>mysql-connector-java</ artifactId>
    <version> ${mysql.version}</version>
</dependency>
```

案例:Flink读取Socket中通话数据通过转换写入到MySQL中。

## 1) 在MySQL中需要数据库表

```sql
#登录mysql创建数据库及表
[root@node2 ~]# mysql -u root -p123456
mysql> create database mydb;
mysql> use mydb;
```

```sql
#建表语句如下
CREATE TABLE `station_log` (
  `sid` varchar(255) DEFAULT NULL,
  `call_out` varchar(255) DEFAULT NULL,
  `call_in` varchar(255) DEFAULT NULL,
  `call_type` varchar(255) DEFAULT NULL,
  `call_time` bigint(20) DEFAULT NULL,
  `duration` bigint(20) DEFAULT NULL
);
```