env.execute();

以上代码运行完成之后结果如下，可以看到结果与批处理结果类似，只是多了对应的处理线程号。

```
3> (hello,15)
8> (Flink,9)
8> (Spark,1)
7> (Java,2)
7> (Scala,2)
7> (MapReduce,1)
```

此外, Stream API 中除了可以设置Batch批处理模式之外, 还可以设置 AUTOMATIC、STREAMING模式, STREAMING 模式是流模式, AUTOMATIC模式会根据数据是有界流/无界流自动决定采用BATCH/STREAMING模式来读取数据, 设置方式如下:

```
//BATCH 设置批处理模式
env.setRuntimeModeigkeitMode.BATCH);
//AUTOMATIC 会根据有界流/无界流自动决定采用BATCH/STREAMING模式
env.setRuntimeModeigkeitMode.AUTOMATIC);
//STREAMING 设置流处理模式
env.setRuntimeModeigkeitMode.STREAMING);
```

除了在代码中设置处理模式外, 还可以在Flink配置文件(flink-conf.yaml)中设置execution焉
runtime-mode参数来指定对应的模式, 也可以在集群中提交Flink任务时指定executionOXJTI
mode来指定, Flink官方建议在提交Flink任务时指定执行模式, 这样减少了代码配置给Flink
Application提供了更大的灵活性, 提交任务指定参数如下:

$FLINK_HOME/bin/flink run -DexecutionXAUtIme=DATAC -c xxx xxx.jar

关于Flink集群提交任务及Flink flink-conf.yaml配置文件在下个章节集群搭建会进行介绍。