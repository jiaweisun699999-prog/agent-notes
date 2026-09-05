```groovy
override def getCommandDescription: RedisCommandDescription = {
    new RedisCommandDescription(RedisCommand.HSET, "fink-scala-redis")
}

//指定写入Redis的Key
override def getKeyFromData(t: (String, Int)): String = t._1

//指定写入Redis的Value
override def值ValueFromData(t: (String, Int)): String = t._2.toString
})

//将结果写入Redis
result.addSink CompanySink)
env.execute("CompanySinkTest")
```

注意：以上代码执行过程中连接Reids报错：Could not get a resource from the pool，可能是没有配置Redis允许外部节点远程连接，配置参考Redis搭建部分。

以上代码执行后可以向Socket中输入如下数据进行测试：

```
hello,flink
hello,spark
hello,hadoop
hello,java
```

查询Redis中的数据存储结果：

```
[root@node4 ~]# redis-cli
127.0.0.1:6379> select 1
OK
127.0.0.1:6379[1]> keys *
1) "flink-scala-redis"
127.0.0.1:6379[1]> hgetall flink-scala-redis
1) "hello"
2) "4"
3) "flink"
4) "1"
5) "hadoop"
6) "1"
7) "spark"
8) "1"
9) "java"
10) "1"
```

### 6.6.5 自定义Sink输出