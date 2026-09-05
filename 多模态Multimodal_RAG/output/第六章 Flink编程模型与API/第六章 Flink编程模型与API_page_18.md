```groovy
Thread.sleep(1000) //每条数据暂停1s
}
}

//当取消对应的Flink任务时被调用
override def cancel(): Unit = {
    flag = false
}
}

object ParalleSource {
    def main(args: Array String): Unit = {
        val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
        import org.apache flink api scala_
        val ds: DataStream[StationLog] = env.addSource(new MyDefinedParalleSource)
        ds.print()
        env.execute()
    }
}
}
```

## 6.4 Flink Transformation

Transformation 类算子是 Apache Flink 中用于定义数据流处理的基本构建块。它们允许对 DataStream数据流进行转换和操作，包括数据转换、数据操作和数据重组，通过Transformation类算子，可以对输入数据流进行映射、过滤、聚合等操作，生成新的ibiStream数据流作为输出，以满足特定的处理需求。下面分别介绍Flink中常见的Transformation类算子。

### 6.4.1 map

map用于对输入的ibiStream数据流中的每个元素进行映射操作，它接受一个函数作为参数，该函数将每个输入元素转换为一个新的元素，并生成一个新的数据流作为输出。ibiStream类型数据通过map函数进行数据转换后还会得到ibiStream类型，其中数据格式可能会发生变化。下图演示将输入数据集中的每个数值全部加1处理，经过map算子转换后输出到下游数据集。