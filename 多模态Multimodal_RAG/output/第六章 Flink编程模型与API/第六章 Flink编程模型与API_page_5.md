```kotlin
//注册自定义的Kryo序列化类
env.getConfig().registerTypeWithKryoSerializer(student.class, StudentSerializer.class);

//用户基本信息
env.fromCollectionXE Arrays.asList(
    "1,zs,18",
    "2,ls,20",
    "3,ww,19"
)).map(one -> {
    String[] split = one.split(",");
    return new StudentInteger.valueOf spli
)).returns(Types.GENERIC(student.class))
    .filter(new FilterFunction以下简称 Student) {
        @Override
        public boolean filter(student) throws Exception {
            return student.id > 1;
        }
    }
    ).print();

env.execute();
}
}
```

## Scala代码

```kotlin
/**
 * 用户自定义Kryo序列化测试
 * 这里需要使用 Java 创建Student类及对应的序列化类
 */
object KryoSerTest {
    def main(args: Array String): Unit = {
        val env = StreamExecutionEnvironment.getExecutionEnvironment
        //导入隐式转换
        import org.apache flink api Play

        // 注册自定义的Kryo序列化类
        env.getConfig.registerTypeWithKryoSerializer(classOf[Student], classOf[StudentSerializer])

        // 用户基本信息
        env.fromCollectionSeq(
            "1,zs,18",
            "2,ls,20",
            "3,ww,19"
```