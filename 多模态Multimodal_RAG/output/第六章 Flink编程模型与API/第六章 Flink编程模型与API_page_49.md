```groovy
xaDataSource.setUrl("jdbc:mysql://node2:3306/mydb?useSSL=false");
xaDataSource.setUser("root");
xaDataSource.setPassword("123456");
return xaDataSource;
}

);

//数据写出到mysql
ds.addSink(jdbcExactlyOnceSink);

env.execute();
```

## • Scala代码实现