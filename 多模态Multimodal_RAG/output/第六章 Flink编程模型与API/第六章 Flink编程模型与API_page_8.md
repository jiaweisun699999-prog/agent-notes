env.execute()

以上文件Source除了读取Text数据之外，还可以读取avro、csv、json、parquet格式对应文件，具体API可以参照官网：https://nightlies.apache.org/flink/flink-docs-release-1.16/docs/connectors/datastream/formats/overview/。

## 6.3.2 Socket Source

Flink读取Socket数据在前几个小节中已经演示过，这里不再读取Socket中的数据。Socket Source 常用于程序测试。

## 6.3.3 集合 Source

Flink可以读取集合中的数据得到Stream，这里我们自定义POJO创建StationLog对象来形成集合数据。

* StationLog对象Java代码如下：

```java
/**
 * StationLog基站日志类
 * sid:基站ID
 * callOut: 主叫号码
 * callIn: 被叫号码
 * callType: 通话类型, 失败(fail)/占线(busy)/拒接(barring)/接通 success)
 * callTime: 呼叫时间戳, 毫秒
 * duration: 通话时长, 秒
 */
public class StationLog {
    public String sid;
    public String callOut;
    public String callIn;
    public String callType;
    public Long callTime;
    public Long duration;

    public StationLog() {
    }

    public StationLog(String sid, String callOut, String callIn, String callType, Long callTime, Long duration) {
        this sid = sid;
        this callOut = callOut;
        this callIn = callIn;
        this callType = callType;
    }
}
```