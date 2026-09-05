* 实现了基于Kubernetes的高可用性(HA)方案,作为生产环境中,ZooKeeper方案之外的另外一种选择;
* 扩展了 Kafka SQL connector,使其可以在 upsert 模式下工作,并且支持在 SQL DDL 中处理 connector 的 metadata;
* PyFlink 中添加了对于 DataStream API 的支持;
* 支持FlinkSink,不建议再使用StreamingFileSink;

* **2021-04-30:**
  * Flink 1.13.0版本发布,主要特性如下:
    * SQL和表接口改进;
    * 改进oriDataStream API和Table API/SQL之间的互操转换;
    * Hive查询语法兼容性;
    * PyFlink的改进;

* **2021-09-29:**
  * Flink 1.14.0 版本发布
    * 改进批和流的状态管理机制;
    * 优化checkpoint机制;
    * 不再支持Flink on Mesos资源调度;
    * 开始支持资源细粒度管理;

* **2022-05-05:**
  * Flink 1.15.0 版本发布,主要特性如下:
    * Per-job任务提交被弃用,未来版本会丢弃,改用Application Mode。
    * Flink依赖包不使用Scala的话可以排除Scala依赖项,依赖包不再包含后缀;
    * 持续改进Checkpoint和两阶段提交优化;
    * 对于Table / SQL用户,新的模块flink-table-planner取代了flink-Table-planner_xx,并且避免了Scala后缀的需要;
    * 添加对opting-out Scala的支持,DataSet/DataStream api独立于Scala,不再传递地依赖于它。
    * flink-table-runtime不再有Scala后缀了;
    * 支持JDK11,后续对JDK8的支持将会移除;
    * 不再支持Scala2.11,支持Scala2.12;
    * Table API & SQL优化,移除FlinkSQL upsert into支持;
    * 支持最低的Hadoop版本为2.8.5;
    * 不再支持zookeeper3.4 HA, zookeeper HA 版本需要升级到3.5/3.6;
    * Kafka Connector默认使用Kafka客户端2.8.1;

* **2022-10-28:**
  * Flink 1.16.0 版本发布,主要特性如下:
    * 弃用jobmanager.sh脚本中的host/web-api-port参数,支持动态配置;
    * 删除字符串表达式DSL;
    * 不再支持Hive1.x、2.1.x、2.2.x版本;