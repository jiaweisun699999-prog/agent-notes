```java
//定义迭代体:在迭代流 iterate 上进行映射转换,将每个整数元素减去1,并返回一个新的数据流
SingleOutputStreamOperator<Integer> minusOne = iterate.map(new MapFunction<Integer, Integer>() {
    @Override
    public Integer map Integer value) throws Exception {
        System.out.println("迭代体中输入的数据为:" + value);
        return value - 1;
    }
});

//定义迭代条件,满足迭代条件的继续进入迭代体进行迭代,否则不迭代
SingleOutputStreamOperator<Integer> stillGreatorThanZero = minusOne.filter(new FilterFunction<Integer>
    @Override
    public boolean filter Integer value) throws Exception {
        return value > 0;
    }
});

//对迭代流应用迭代条件
iterate.closeWith(stillGreatorThanZero);

//迭代流数据输出,无论是否满足迭代条件都会输出
iterate.print();
env.execute();
```

## • Scala代码实现

```scala
val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
//导入隐式转换
import org.apacheECTL_api.scaLA_

val ds1: DataStream� String] = env.socketTextStream("node5", 9999)

//转换数据流
val ds2: DataStream Int] = ds1.map(v => v.toInt)
//定义迭代流,并指定迭代体和迭代条件
val result: DataStream Int] = ds2.iterate(
    iteration => {
        //定义迭代体
        val minusOne: DataStream Int] = iteration.map(v => {printIn("迭代体中value值为:" + v); v - 1})

        //定义迭代条件,满足的继续迭代
        val stillGreatorThanZero: DataStream Int] = minusOne.filter(_ > 0)

        //定义哪些数据最后进行输出
        val lessThanZero: DataStream Int] = minusOne.filter(_ <= 0)
    }
)
```