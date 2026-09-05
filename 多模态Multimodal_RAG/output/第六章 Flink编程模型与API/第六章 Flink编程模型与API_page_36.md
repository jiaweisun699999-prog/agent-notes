```java
// map方法,输入一个元素,返回一个元素
@Override
public String map(String value) throws Exception {
    //value 格式: 001,186,187,busy,1000,10
    String[] split = value.split(",");
    String sid = split[0];
    String callOut = split[1]; //主叫
    String callIn = split[2]; //被叫
    String callType = split[3]; //通话类型
    String callTime = split[4]; //通话时间
    String duration = split[5]; //通话时长

    //mysql中获取主叫和被叫的姓名
    String callOutName = "";
    String callInName = "";

    pst.setString(1,callOut);
    rst = pst.executeQuery();
    while (rst.next()) {
        callOutName = rst.getString("name");
    }
    pst.setString(1,callIn);
    rst = pst.executeQuery();
    while (rst.next()) {
        callInName = rst.getString("name");
    }

    return "基站ID:" + sid + ",主叫号码:" + callOut + ",主叫姓名:" + callOutName + "," +
        "被叫号码:" + callIn + ",被叫姓名:" + callInName + ",通话类型:" + callType + "," +
        "通话时间:" + callTime + ",通话时长:" + duration + "s";
}

// close()方法在map方法之后执行,用于清理
@Override
public void close() throws Exception {
    rst.close();
    pst.close();
    conn.close();
}
}
}
```

## Scala代码