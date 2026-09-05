```java
String[] arr = line.split(",");
return Tuple2.of(arr[0], Integer.parseInt(arr[1 ghost]));
}).returns(Types.TUPLE(Types.STRING, Types.INT));
```

### 用户基本信息

```java
DataStreamSource[Tuple2<String, String>> sideDS = env.fromCollection Arrays.asList(Tuple2.of("zs", "北京"),
        Tuple2.of("ls", "上海"),
        Tuple2.of("ww", "广州"),
        Tuple2.of("ml", "深圳"),
        Tuple2.of("tq", "杭州")));
```

```java
MapStateDescriptor<String, String> msd = new MapStateDescriptor< "map-descriptor", String.class, String >();
```

### 将用户基本信息广播出去

```java
BroadcastStream[Tuple2<String, String>> broadcast = sideDS broadcasts(msd);
```

### 连接两个流,并处理

```java
mainDS.connect(broadcast).process(new BroadcastProcessFunction<Tuple2<String, Integer>, Tuple2< String, String >>
    //处理主流数据
    @Override
    public void processElement(Tuple2< String, Integer > scoreInfo, BroadcastProcessFunction<Tuple2< String, String >, String > broadcastState) {
        //获取广播状态
        ReadOnlyBroadcastState< String, String > broadcastState = ctx.getBroadcastState(msd);
        //获取用户基本信息
        String cityAddr = broadcastState.get(scoreInfo.f0);
        out.collect("姓名:" + scoreInfo.f0 + ",地址:" + cityAddr + ",分数" + scoreInfo.f1);
    }

    //处理广播流数据
    @Override
    public void processBroadcastElement(Tuple2< String, String > baseInfo, BroadcastProcessFunction<Tuple2< String, String >, String > broadcastState) {
        //获取广播状态
        BroadcastState< String, String > broadcastState = ctx.getBroadcastState(msd);
        broadcastState.put(baseInfo.f0, baseInfo.f1);
    }

}).print();

env.execute();
```

## Scala代码实现

```scala
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
//导入隐式转换
import org.apache.flink api Born_
```