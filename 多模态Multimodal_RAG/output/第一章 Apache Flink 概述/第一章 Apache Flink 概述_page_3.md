* 2014-08-26:Flink 0.6发布;
* 2014-11-04:Flink 0.7.0发布,推出最重要的特性:Streaming API;
* 2016-03-08:Flink 1.0.0,流处理基础功能完善,支持Scala;
* 2016-08-08:Flink 1.1.0版本发布,流处理基础功能完善;
* 2017-02-06:Flink 1.2.0版本发布,流处理基础功能完善;
* 2017-06-01:Flink 1.3.0版本发布,流处理基础功能完善;
* 2017-11-29:Flink 1.4.0版本发布,流处理基础功能完善;
* 2018-05-25:Flink 1.5.0版本发布,流处理基础功能完善;
* 2018-08-08:Flink 1.6.0版本发布,流处理基础功能完善,状态TTL支持;增强SQL和Table API;
* 2018-11-30:Flink 1.7.0版本发布,Scala2.12支持;支持S3文件处理;支持Kafka 2.0 connector;
* 2019-01:阿里巴巴以9000万欧元价格收购Data Artisans公司,并开发内部版本Blink;
* 2019-04-09:Flink 1.8.0版本发布,支持TTL清除旧状态;不再支持hadoop二进制文件;
* 2019年8月阿里巴巴开源Blink。
* 2019-08-22:Flink 1.9.0版本发布,主要特性如下:
  * 合并阿里内部Blink;
  * 重构Flink WebUI;
  * Hive集成;
  * Python Table API支持;
* 2020-02-11:Flink 1.10.0版本发布【重要版本】,主要特性如下:
  * 整合Blink全部完成;
  * 集成K8S;
  * PyFlink优化;
  * 内存管理配置优化;
* 2020-07-06:Flink 1.11.0版本发布【重要版本】,主要特性如下:
  * 从Flink1.11开始,Blink planner是Table API/SQL中的默认设置,仍支持旧的Flink planner;
  * Flink CDC支持;
  * 支持Hadoop3.x版本,不提供任何更新的flink-shaded-hadoop-x jars,用户需要通过HADOOP_CLASSPATH环境变量(推荐)或lib/folder 提供 Hadoop 依赖项。
* 2020-12-08:Flink 1.12.0版本发布【重要版本】,主要特性如下:
  * DataStream API上添加了高效的批执行模式的支持,批处理和流处理实现真正统一的运行时的一个重要里程碑;