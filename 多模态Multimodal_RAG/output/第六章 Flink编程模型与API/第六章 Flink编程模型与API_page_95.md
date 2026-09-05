//关闭资源
override def close(): Unit = {
  //关闭线程池
  executorService.shutdown()
}