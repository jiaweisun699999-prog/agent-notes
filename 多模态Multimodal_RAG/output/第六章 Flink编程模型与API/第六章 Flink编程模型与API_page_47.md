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

## 2) 编写代码

### Java代码实现

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
//必须设置checkpoint,否则数据不能正常写出到mysql
env.enableCheckpointing(5000);
/**
 * socket 中输入数据如下:
 * 001,186,187,busy,1000,10
 * 002,187,186,fail,2000,20
```