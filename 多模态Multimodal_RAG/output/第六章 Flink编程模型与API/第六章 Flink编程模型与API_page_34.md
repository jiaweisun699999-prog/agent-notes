```groovy
ds.map(new MyMapFunction()).print()

env.execute()
}

private class MyMapFunction extends MapFunction(String, String) {
    override def map(value: String): String = {
        //value格式: 001,186,187,busy,1000,10
        val split: Array String = value.split(",")
        //获取通话时间,并转换成yyyy-MM-dd HH:mm:ss格式
        val sdf = new SimpleFormat("yyyy-MM-dd HH:mm:ss")
        valtempsdf = sdf.format split(4).toLong)

        //获取通话时长,通话时间加上通话时长,得到通话结束时间,转换成yyyy-MM-dd HH:mm:ss格式
        valduration = split(5)
        valtempsdf = sdf.format split(4).toLong + duration.toLong)

        "基站ID:" + split(0) + ",主叫号码:" + split(1) + "," +
        "被叫号码:" + split(2) + ",通话类型:" + split(3) + "," +
        "通话开始时间:" + tempsdf + ",通话结束时间:" + tempsdf
    }
}
}
}
```

## 6.5.2 富函数类

Flink中除了有函数接口之外还有功能更强大的富函数接口,富函数接口与其他常规函数接口的不同在于:可以获取运行环境的上下文,在上下文环境中可以管理状态(状态内容后续章节介绍),并拥有一些生命周期方法,所以可以实现更复杂的功能。常见的富函数接口有:RichMapFunction、RichFlatMapFunction、RichFilterFunction等。

所有RichFunction中有一个生命周期的概念,典型的生命周期方法有:

* open()方法是rich function的初始化方法,当一个算子例如map或者filter被调用之前open()会被调用,一般用于初始化资源。
* close()方法是生命周期中的最后一个调用的方法,做一些清理工作。
* getRuntimeContext()方法提供了函数的RuntimeContext的一些信息,例如函数执行的并行度,任务的名字,以及state状态

下面通过案例来演示富函数接口的使用。

**案例：**读取Socket中数据,结合MySQL中电话对应的姓名来输出信息。

1) 准备mysql数据