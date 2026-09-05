```java
public Student() {
}

public Student(Integer id, String name, Integer age) {
    this.id = id;
    this.name = name;
    this.age = age;
}

@Override
public String toString() {
    return "Student{
        "id=" + id +
        ", name="" + name + '\" +
        ", age=" + age +
        '}";
}

}

public class StudentSerializer extends Simulator {
    @Override
    public void write(Kryo kryo, Output output, Object o) {
        Student student = (Student) o;
        output.writeInt(student.id);
        output.writeString(student.name);
        output.writeInt(student.age);
    }

    @Override
    public Object read(Kryo kryo, Input input, Class aClass) {
        Student student = new Student();
        student.id = input.readInt();
        student.name = input.readString();
        student.age = input.readInt();
        return student;
    }

}
```

## Java代码

```java
/**
 * 用户自定义Kryo序列化测试
*/
public class KryoSerTest {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
```