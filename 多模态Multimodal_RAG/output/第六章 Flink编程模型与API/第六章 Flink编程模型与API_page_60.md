```
* 002,187,186,fail,2000,20
* 003,186,188,busy,3000,30
* 004,188,186,busy,4000,40
* 005,188,187,busy,5000,50
*/
DataStreamSource<String> ds = env.socketTextStream("node5", 9999);

ds.addSink(new RichSinkFunction<String>() {

    org.apache.hadoop.hbase.client.Connection conn = null;

    //在Sink 初始化时调用一次,这里创建 HBase连接
    @Override
    public void open(Configuration parameters) throws Exception {
        org.apache.hadoop.conf Configuration conf = HBaseConfiguration.create();
        conf.set("hbase.zookeeper.quorum","node3,node4,node5");
        conf.set("hbase.zookeeper property.clientPort ", "2181");
        //创建连接
        conn = ConnectionFactory.createConnection(conf);
    }

    //Sink数据时,每条数据插入时调用一次
    @Override
    public void invoke(String currentOne, Context context) throws Exception {
        //解析 currentOne 数据, 001,186,187,busy,1000,10
        String[] split = currentOne.split(",");

        //准备rowkey
        String rowKey = split[0];

        //获取列
        String callOut = split[1];
        String callIn = split[2];
        String callType = split[3];
        String callTime = split[4];
        String duration = split[5];

        //获取表对象
        Table table = conn.getTable(TableName.valueOf("flink-sink-hbase"));

        //创建Put对象
        Put p = new Put Bytes.toBytes(rowKey));

        //添加列
        p.addColumn Bytes.toBytes("cf"), Bytes.toBytes("callOut"), Bytes.toBytes(callOut));
        p.addColumn Bytes.toBytes("cf"), Bytes.toBytes("callIn"), Bytes.toBytes(callIn));
        p.addColumn Bytes.toBytes("cf"), Bytes.toBytes("callType"), Bytes.toBytes(callType));
        p.addColumn Bytes.toBytes("cf"), Bytes.toBytes("callTime"), Bytes.toBytes(callTime));
```