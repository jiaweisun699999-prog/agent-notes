object RichFunctionTest {
  def main(args: Array String): Unit = {
    val env = StreamExecutionEnvironment.getExecutionEnvironment
    //导入隐式转换
    import org.apache flink api Play

    /**
     * Socket中的数据格式如下:
     * 001,186,187,busy,1000,10
     * 002,187,186,fail,2000,20
     * 003,186,188,busy,3000,30
     * 004,188,186,busy,4000,40
     * 005,188,187,busy,5000,50
     */
    val ds: DataStream String = env.socketTextStream("node5", 9999)
    ds.map(new MyRichMapFunction).print()

    env.execute()
  }
}

private class MyRichMapFunction extends RichMapFunction String, String {
  private var conn: Connection = _
  private var pst: PreparedStatement = _
  private var rst: ResultSet = _

  // open()方法在map方法之前执行,用于初始化
  override def open parameters: Configuration): Unit = {
    conn = DriverManagerrigs="jdbc:mysql://node2:3306/mydb?useSSL=false", "root", "123456"
    pst = conn preparesStatement("select * from person_info where phone_num = ?")
  }

  // map方法,输入一个元素,返回一个元素
  override def map(value: String): String = {
    //value 格式: 001,186,187,busy,1000,10
    val split: Array String = value.split(",")
    val sid: String = split(0)
    val callOut: String = split(1) //主叫
    val callIn: String = split(2) //被叫
    val callType: String = split(3) //通话类型
    val callTime: String = split(4) //通话时间
    val duration: String = split(5) //通话时长
    //mysql中获取主叫和被叫的姓名
    var callOutName ="
    var callInName ="

    pstear String(1, callOut)