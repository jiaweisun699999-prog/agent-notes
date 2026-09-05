hbase:034:0> scan 'flink-sink-hbase'

+---+-----------+----------+-------+
| row | column    | timestamp | value |
+---+-----------+----------+-------+
| 001 | cf:callIn | timestamp | 187   |
| 001 | cf:callOut| timestamp | 186   |
| 001 | cf:callTime| timestamp | 1000  |
| 001 | cf:callType| timestamp | busy  |
| 001 | cf:duration| timestamp | 10    |
| 002 | cf:callIn | timestamp | 186   |
| 002 | cf:callOut| timestamp | 187   |
| 002 | cf:callTime| timestamp | 2000  |
| 002 | cf:callType| timestamp | fail  |
| 002 | cf:duration| timestamp | 20    |
| 003 | cf:callIn | timestamp | 188   |
| 003 | cf:callOut| timestamp | 186   |
| 003 | cf:callTime| timestamp | 3000  |
| 003 | cf:callType| timestamp | busy  |
| 003 | cf:duration| timestamp | 30    |
| 004 | cf:callIn | timestamp | 186   |
| 004 | cf:callOut| timestamp | 188   |
| 004 | cf:callTime| timestamp | 4000  |
| 004 | cf:callType| timestamp | busy  |
| 004 | cf:duration| timestamp | 40    |
| 005 | cf:callIn | timestamp | 187   |
| 005 | cf:callOut| timestamp | 188   |
| 005 | cf:callTime| timestamp | 5000  |
| 005 | cf:callType| timestamp | busy  |
| 005 | cf:duration| timestamp | 50    |

6.7 DataStream分区操作

Flink中的分区操作是将数据流根据指定的分区策略重新分配到不同节点上,由不同任务执行。默认情况下,Flink使用轮询方式(rebalance partitioner)将数据从上游分发到下游算子。然而,在某些情况下,用户可能希望自己控制分区,例如在数据倾斜的场景中,为了实现这种控制,可以使用预定义的分区策略或自定义分区策略来决定数据的流转和处理方式。

Flink内部提供了常见的分区策略有如下8种:哈希分区(Hash partitioner)、随机分区(shuffle partitioner)、轮询分区(rebalance partitioner)、重缩放分区(rescale partitioner)、广播分区(broadcast partitioner)、全局分区(global partitioner)、并行分区(forward partitioner)、自定义分区。使用以上各类分区策略时需要使用不同的ibiStream 方法进行操作,下面分别进行演示。

6.7.1 keyBy哈希分区