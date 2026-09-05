```java
keyedStream.sum("duration").print
//统计duration的最小值, min返回该列最小值, 其他列与第一条数据保持一致
keyedStream.min("duration").print
//统计duration的最小值, minBy返回的是最小值对应的整个对象
keyedStream.minBy("duration").print
//统计duration的最大值, max返回该列最大值, 其他列与第一条数据保持一致
keyedStream.max("duration").print
//统计duration的最大值, maxBy返回的是最大值对应的整个对象
keyedStream.maxBy("duration").print
```

```java
env.execute()
```

## Java代码和Scala代码执行后结果如下：

### sum执行结果

```
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853430}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853430}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853430}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853430}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853430}
```

### min 执行结果

```
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853434}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853434}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853434}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853434}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853434}
```

### minBy 执行结果

```
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853434}
StationLog{sid='sid1', callOut='18600000001', callIn='1860000002', callType='fail', callTime=168534347490}
StationLog{sid='sid1', callOut='18600000001', callIn='1860000002', callType='fail', callTime=168534347490}
StationLog{sid='sid1', callOut='18600000001', callIn='1860000002', callType='fail', callTime=168534347490}
StationLog{sid='sid1', callOut='18600000001', callIn='1860000002', callType='fail', callTime=168534347490}
```

### max 执行结果

```
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853435}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853435}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853435}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853435}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853435}
```

### maxBy 执行结果

```
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853435}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853435}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853435}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853435}
StationLog{sid='sid1', callOut='18600000000', callIn='1860000001', callType='success', callTime=16853435}
```