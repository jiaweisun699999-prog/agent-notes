# Python面向对象\+模块\+异常总结

本套文档按照**零基础循序渐进、无逻辑断层、贴合工程开发**的顺序编写，统一Python标准术语、配套可运行实战代码、高频坑点总结。学习主线：OOP基础 → 类成员详解 → 封装 → 继承 → 多态 → OOP三大特征汇总 → 模块与包工程化 → 异常处理，完全适配新手进阶、面试、项目开发需求。

# 第一章 面向对象基础（OOP核心入门）

## 1\. 面向过程 vs 面向对象

### 1\.1 面向过程

核心思想：步骤化、流水线式编程，聚焦**怎么做**，按顺序执行代码，适合简单小程序。缺点：代码冗余、复用性差、维护困难，复杂业务无法适配。

### 1\.2 面向对象（OOP）

核心思想：模块化、封装化编程，聚焦**谁来做**，将**属性（数据）和方法（行为）**封装为整体，适合复杂项目、业务逻辑开发。核心优势：代码复用、扩展性强、维护成本低、逻辑清晰。

## 2\. 类与对象核心概念

- **类（class）**：抽象模板，定义一类事物的公共属性和行为，本身不存储具体数据

- **对象（实例）**：根据类模板创建的具体个体，拥有独立的属性数据和方法，是类的具象化产物

核心逻辑：**先定义类，再创建对象**（所有OOP代码的基础规则）

## 3\. 类的定义与对象创建

```python
# 1. 定义类（模板）
class Person:
    # 自定义方法
    def speak(self):
        print("人类可以说话")

# 2. 创建对象（实例化）
p1 = Person()
p2 = Person()

# 3. 调用对象方法
p1.speak()
p2.speak()
```

## 4\. 核心魔法方法：\_\_init\_\_ 构造方法

魔法方法：以双下划线 `__` 包裹的内置方法，无需手动调用，满足条件自动触发。`__init__` 是**最核心、最常用**的构造方法。

### 特性

- 创建对象时**自动执行**，无需手动调用

- 用于初始化对象属性，为每个对象绑定独立数据

- 第一个参数固定为 `self`，代表当前对象本身

```python
class Person:
    # 构造方法：初始化对象属性
    def __init__(self, name, age):
        # self.属性 = 形参  绑定对象独有属性
        self.name = name
        self.age = age

    # 对象方法
    def info(self):
        print(f"姓名：{self.name}，年龄：{self.age}")

# 创建不同对象，传入不同属性值
p1 = Person("张三", 18)
p2 = Person("李四", 20)

p1.info()
p2.info()

# 直接访问对象属性
print(p1.name)
print(p2.age)
```

## 5\. 常用通用魔法方法

### 5\.1 \_\_str\_\_：对象打印自定义输出

默认打印对象会输出内存地址，重写 `__str__` 可自定义打印内容，提升可读性。

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    # 自定义打印对象内容
    def __str__(self):
        return f"Person[{self.name}, {self.age}]"

p1 = Person("王五", 22)
print(p1)  # 不再输出内存地址，输出自定义内容
```

### 5\.2 \_\_del\_\_：析构方法

对象被销毁、释放内存时自动执行，用于收尾操作（关闭文件、释放资源等）。

```python
class Person:
    def __init__(self, name):
        self.name = name
        print(f"创建对象：{self.name}")

    def __del__(self):
        print(f"销毁对象：{self.name}")

p1 = Person("赵六")
# 程序结束/对象无引用时自动触发__del__
```

# 第二章 类的成员详解（属性 \+ 三大方法）

## 1\. 类属性 vs 对象（实例）属性

### 1\.1 对象属性（实例属性）

在 `__init__` 中通过 `self.xxx` 定义，**每个对象独有**，对象之间互不影响。

### 1\.2 类属性

直接在类内部、方法外部定义，**所有对象共享**，统一维护公共数据，节省内存。

### 1\.3 核心区别与实战案例

```python
class Person:
    # 类属性：所有对象共享
    species = "人类"

    # 对象属性：每个对象独有
    def __init__(self, name, age):
        self.name = name
        self.age = age

# 访问类属性（类名/对象均可访问）
print(Person.species)

# 创建对象
p1 = Person("张三", 18)
p2 = Person("李四", 20)
print(p1.species)
print(p2.species)

# 修改类属性：所有对象同步生效
Person.species = "高级人类"
print(p1.species)
print(p2.species)

# 修改对象属性：仅当前对象生效
p1.name = "张三三"
print(p1.name)
print(p2.name)
```

### 高频坑点

通过 **对象\.类属性 = 值** 不会修改全局类属性，只会给当前对象新增一个同名对象属性，屏蔽类属性。修改类属性必须用 **类名\.类属性**。

## 2\. 三大方法详解（实例/类/静态）

### 2\.1 实例方法（最常用）

默认定义的普通方法，第一个参数为 `self`，只能通过对象调用，可操作对象属性和类属性。

### 2\.2 类方法 @classmethod

通过装饰器声明，第一个参数为 `cls`（代表当前类），可通过类名/对象调用，**只能操作类属性，不能操作对象属性**。

### 2\.3 静态方法 @staticmethod

通过装饰器声明，**无self、无cls参数**，属于工具方法，不依赖类和对象属性，仅做独立逻辑处理。

### 2\.4 三者对比案例

```python
class Person:
    # 类属性
    count = 0

    def __init__(self, name):
        self.name = name
        Person.count += 1

    # 1. 实例方法
    def show_name(self):
        print(f"对象姓名：{self.name}")

    # 2. 类方法
    @classmethod
    def show_count(cls):
        print(f"总人数：{cls.count}")

    # 3. 静态方法
    @staticmethod
    def help():
        print("这是人类工具类，提供基础功能")

# 调用
p1 = Person("张三")
p1.show_name()    # 实例方法：对象调用
Person.show_count() # 类方法：类名调用
Person.help()      # 静态方法：类名/对象均可调用
```

# 第三章 面向对象三大特征一：封装

## 1\. 封装核心思想

将类的属性和方法私有化，隐藏内部实现细节，**仅对外提供指定访问接口**，保证数据安全，避免外部随意篡改。

## 2\. 私有属性与私有方法

- **单下划线 \_xxx**：约定私有，外部可访问，但工程上默认不主动调用

- **双下划线 \_\_xxx**：强制私有，Python自动名称改写，**外部无法直接访问**

### 实战案例

```python
class Person:
    def __init__(self, name, age):
        self.name = name      # 公共属性
        self.__age = age      # 私有属性

    # 私有方法
    def __secret(self):
        print("这是私有方法，外部不可调用")

    # 对外提供取值接口
    def get_age(self):
        return self.__age

    # 对外提供修改接口（可做数据校验）
    def set_age(self, new_age):
        if 0 < new_age < 150:
            self.__age = new_age
        else:
            print("年龄输入不合法")

p1 = Person("李四", 20)
# print(p1.__age)  # 报错：无法直接访问私有属性
# p1.__secret()    # 报错：无法直接调用私有方法

# 通过接口访问、修改
print(p1.get_age())
p1.set_age(25)
print(p1.get_age())
p1.set_age(200)  # 校验不通过，修改失败
```

## 3\. property 装饰器（简化私有属性读写）

替代手动写get/set方法，像访问普通属性一样操作私有属性，代码更简洁。

```python
class Person:
    def __init__(self, age):
        self.__age = age

    # 取值
    @property
    def age(self):
        return self.__age

    # 赋值
    @age.setter
    def age(self, new_age):
        if 0 < new_age < 150:
            self.__age = new_age

p1 = Person(18)
print(p1.age)    # 直接取值
p1.age = 30      # 直接赋值
print(p1.age)
```

# 第四章 面向对象三大特征二：继承

## 1\. 继承核心概念

子类（派生类）自动拥有父类（基类）的所有公共属性和方法，核心价值：**代码复用、减少冗余、拓展功能**。

语法：`class 子类名(父类名):`

## 2\. 单继承实战

```python
# 父类
class Animal:
    def eat(self):
        print("动物需要进食")

# 子类：继承父类
class Dog(Animal):
    # 子类拓展自己的方法
    def bark(self):
        print("狗狗会汪汪叫")

# 子类对象可调用父类+自身方法
dog = Dog()
dog.eat()   # 继承父类方法
dog.bark()  # 自身拓展方法
```

## 3\. 方法重写（核心考点）

子类定义与父类**同名的方法**，覆盖父类原有逻辑，实现子类个性化功能，是多态的基础。

```python
class Animal:
    def eat(self):
        print("动物进食")

class Cat(Animal):
    # 重写父类方法
    def eat(self):
        print("猫咪吃鱼")

cat = Cat()
cat.eat()  # 执行子类重写后的方法
```

## 4\. super\(\) 用法（调用父类功能）

子类重写方法后，可通过 `super()` 调用父类的构造方法、普通方法，保留父类逻辑并拓展。

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def eat(self):
        print(f"{self.name}进食")

class Pig(Animal):
    def __init__(self, name, color):
        # 调用父类构造方法，继承父类属性
        super().__init__(name)
        self.color = color  # 拓展子类独有属性

    # 重写方法并保留父类逻辑
    def eat(self):
        super().eat()
        print(f"{self.color}的{self.name}吃野菜")

pig = Pig("小猪", "粉色")
pig.eat()
```

## 5\. 多继承

Python支持一个子类同时继承多个父类，语法：`class 子类(父类1,父类2...):`

查找规则（MRO）：**从左到右依次查找**，找到即停止，避免冲突。

```python
class A:
    def func(self):
        print("A类方法")

class B:
    def func(self):
        print("B类方法")

# 多继承
class C(A, B):
    pass

c = C()
c.func()  # 优先执行左侧父类A的方法
```

MRO 顺序 `C → A → B`；

在 A 中找到了 `func` 同名方法，停止查找，不会去看 B；

调用时参数不匹配，直接抛出参数数量错误，**不会自动切换到右边 B 的同名方法**。

#### MRO 核心规则（关键）

MRO（方法解析顺序）检索逻辑只判断**方法名是否相等**，不校验函数签名（参数个数、参数名）：

1. 按照继承书写顺序从左到右遍历父类；
2. 只要当前父类存在同名方法，立刻取用；
3. 参数不匹配属于调用层面报错，不会触发 “继续找下一个父类” 的逻辑。

#### 子类重写，手动指定调用 B 的方法

```python
class C(A, B):
    def func(self, x, y):
        # 主动调用父类B的func
        B.func(self, x, y)

c = C()
c.func(10, 20)
```

## 6\. 类型判断

```python
class Animal: pass
class Dog(Animal): pass

d = Dog()

# 1. isinstance：判断对象是否属于某个类/子类（推荐）
print(isinstance(d, Dog))    # True
print(isinstance(d, Animal)) # True

# 2. type：精准判断对象所属类，不识别继承
print(type(d) == Dog)    # True
print(type(d) == Animal) # False

# 3. issubclass：判断是否为子类
print(issubclass(Dog, Animal)) # True
```

# 第五章 面向对象三大特征三：多态

## 1\. 多态核心概念

**同一个方法，不同对象执行不同逻辑**。实现条件：继承 \+ 方法重写，核心价值：统一调用接口，适配不同子类对象。

## 2\. 多态实战案例

```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        print("汪汪汪")

class Cat(Animal):
    def speak(self):
        print("喵喵喵")

# 统一调用函数，适配所有子类
def animal_speak(animal: Animal):
    animal.speak()

# 不同对象，同一方法，不同效果
animal_speak(Dog())
animal_speak(Cat())
```

# 第六章 面向对象三大特征总结

- **封装**：隐藏内部细节、保护数据安全、对外提供统一接口（私有化属性方法）

- **继承**：代码复用、拓展功能、构建类的层级关系（子类复用父类）

- **多态**：统一调用入口、兼容不同子类、提升代码扩展性（同方法不同实现）

# 第七章 模块与包

## 1\. 模块基础概念

模块就是**单个\.py文件**，用于拆分代码、功能解耦、复用代码，避免单文件代码臃肿。

## 2\. 四种模块导入写法

```python
# 1. 导入整个模块
import math
print(math.sqrt(16))

# 2. 导入模块指定功能
from math import pi, pow
print(pi)

# 3. 导入模块所有功能（不推荐）
from math import *

# 4. 别名导入（简化名称）
import math as m
print(m.sqrt(25))
```

## 3\. 自定义模块 \& 测试入口

`if __name__ == '__main__'`：模块专属测试入口，**当前文件直接运行生效，被其他文件导入不执行**，是自定义模块核心语法。

### 自定义模块 demo\.py

```python
# demo.py 自定义模块
def add(a, b):
    return a + b

# 模块测试代码
if __name__ == '__main__':
    print(add(10, 20))

```

### 导入使用模块

```python
import demo
print(demo.add(5, 6))

```

## 4\. 自定义模块注意事项

- 模块名必须遵循标识符规范：小写、下划线，**禁止中文、数字开头、与内置模块重名**

- 模块搜索顺序：当前目录 → sys\.path 系统路径 → 内置模块

- 禁止循环导入（A导入B，B又导入A），会直接报错

## 5\. 包与第三方库

- **包**：包含 `__init__.py` 的文件夹，用于管理多个模块，实现功能分类

- **第三方库**：Python官方/开源社区提供的拓展库，通过pip工具安装

```python
# 终端安装第三方库命令
# pip install 库名
# 示例：pip install requests

```

# 第八章 异常处理

## 1\. 异常概念

程序运行中出现的错误（语法错误、逻辑错误、数据错误），默认会终止程序，异常处理可捕获错误、保证程序持续运行。

## 2\. try\-except 完整捕获语法

```python
try:
    # 可能出错的代码
    num = int(input("请输入数字："))
except ValueError:
    # 捕获指定异常
    print("输入格式错误，请输入整数！")
except Exception as e:
    # 捕获所有未知异常
    print(f"程序出错：{e}")
else:
    # 无异常时执行
    print(f"输入成功，数字为：{num}")
finally:
    # 无论是否出错，最终都会执行
    print("程序执行结束")
```

## 3\. 主动抛出异常 raise

手动触发指定异常，用于主动校验数据、终止非法逻辑。

```python
def check_age(age):
    if age < 0:
        # 主动抛出异常
        raise ValueError("年龄不能为负数")
    print(f"年龄合法：{age}")

check_age(-5)
```

## 4\. 自定义异常

继承内置 `Exception` 类，自定义专属异常类型，适配业务场景报错。

```python
# 自定义异常类
class AgeError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

# 使用自定义异常
def check_age(age):
    if age > 150:
        raise AgeError("年龄超出合理范围")
    print("年龄正常")

check_age(200)
```
