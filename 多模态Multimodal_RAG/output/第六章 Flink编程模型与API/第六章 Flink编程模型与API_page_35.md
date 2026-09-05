```sql
create database mydb;
use mydb;
create table person_info (
phone_num varchar(255),
name varchar(255),
city varchar(255)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into person_info values (186, "张三", "北京"), (187, "李四", "上海"), (188, "王五", "深圳");
```

## 2) 编写代码

* **Java代码**

```java
public class RichFunctionTest {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        /**
         * Socket中的数据格式如下:
         * 001,186,187,busy,1000,10
         * 002,187,186,fail,2000,20
         * 003,186,188,busy,3000,30
         * 004,188,186,busy,4000,40
         * 005,188,187,busy,5000,50
        */
        DataStreamSource<String> ds = env.socketTextStream("node5", 9999);
        ds.map(new MyRichMapFunction()).print();

        env.execute();
    }

    private static class MyRichMapFunction extends RichMapFunction<String, String> {
        Connection conn = null;
        PreparedStatement pst = null;
        ResultSet rst = null;

        // open()方法在map方法之前执行,用于初始化
        @Override
        public void open(Configration parameters) throws Exception {
            conn = DriverManager.getConnection("jdbc:mysql://node2:3306/mydb?useSSL=false", "root", "123456
pst = conn preparestatement("select * from person_info where phone_num = ?");
        }
    }
}
```