# Python高级编程总结

## 一、时间与日期

Python 处理时间日期主要依靠两大模块：**time 模块（底层时间戳、系统时间）**、**datetime 模块（面向对象日期计算）**。整体学习顺序：time基础 → 时间格式化 → date日期对象 → datetime时间对象 → timedelta时间差计算。

### 1. time 时间库介绍

#### 1.1 time模块作用

time 是 Python 内置底层时间模块，主要用于：获取时间戳、程序休眠、获取系统原始时间、秒级时间统计。

#### 1.2 三大核心时间形式

- 
- **结构化时间（struct_time）**：元组形式，年、月、日、时、分、秒、星期等
- **格式化时间字符串**：人类可读时间 2025-01-01 12:00:00

#### 1.3 常用基础代码

```python
import time

# 1. 获取当前时间戳
print(time.time())

# 2. 获取本地结构化时间
print(time.localtime())

# 3. 获取UTC结构化时间
print(time.gmtime())

# 4. 程序休眠
time.sleep(1)
```

#### 1.4 特点与使用场景

- 适合：计时、程序休眠、时间戳存储、日志时间
- 不适合：日期加减、跨天计算、日期对象操作

### 2. time 时间格式化（重点必考）

#### 2.1 两种核心转换

- **strftime**：结构化时间 → 格式化字符串（机器时间转人类时间）
- **strptime**：字符串时间 → 结构化时间（人类时间转机器时间）

#### 2.2 常用时间格式符

- %Y 年  %m 月  %d 日
- %H 时  %M 分  %S 秒
- %w 星期（0周日-6周六）

#### 2.3 格式化代码示例

```python
import time

# 结构化时间转字符串
t = time.localtime()
res = time.strftime("%Y-%m-%d %H:%M:%S", t)
print(res)

# 字符串转结构化时间
str_time = "2025-01-01 10:10:10"
t2 = time.strptime(str_time, "%Y-%m-%d %H:%M:%S")
print(t2)
```

### 3. date 对象操作（仅日期）

datetime.date：只处理 **年、月、日**，没有时分秒，适合日期筛选、生日判断、天数统计。

```python
from datetime import date

# 获取今日日期
today = date.today()
print(today)

# 手动构造日期
d = date(2025, 8, 4)
print(d.year, d.month, d.day)
```

#### 3.1 基础用法

#### 3.2 常用操作

- 日期对象可以直接比较大小（前后日期判断）
- 可以配合 timedelta 做日期加减
- 无法处理时分秒

### 4. datetime 对象操作（日期+时间）

datetime.datetime：最常用！包含 **年、月、日、时、分、秒、微秒**，项目开发90%场景使用它。

#### 4.1 基础使用

```python
from datetime import datetime

# 获取当前完整时间
now = datetime.now()
print(now)

# 手动构造时间对象
dt = datetime(2025, 8, 4, 14, 30, 0)
print(dt)

# 时间对象格式化
print(dt.strftime("%Y-%m-%d %H:%M:%S"))
```

#### 4.2 时间字符串转 datetime 对象

```python
from datetime import datetime

s = "2025-08-04 14:30:00"
dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
print(dt, type(dt))
```

### 5. timedelta 时间差对象（重难点+实战最多）

timedelta 用于做 **时间加减、日期偏移、倒计时、天数推算**，是项目最实用功能。

支持：days 天、seconds 秒、microseconds 微秒、weeks 周

#### 5.1 常用案例：昨天、明天、前后几天

```python
from datetime import datetime, timedelta

now = datetime.now()

# 明天
tomorrow = now + timedelta(days=1)
# 昨天
yesterday = now - timedelta(days=1)
# 两小时后
hour_later = now + timedelta(hours=2)

print("昨天：", yesterday.strftime("%Y-%m-%d"))
print("明天：", tomorrow.strftime("%Y-%m-%d"))
```

#### 5.2 计算两个时间间隔

```python
from datetime import datetime

t1 = datetime(2025, 1, 1)
t2 = datetime(2025, 8, 4)

diff = t2 - t1
print("间隔天数：", diff.days)
```

### 6.使用场景

- **单纯计时、休眠、时间戳** → 使用 time 模块
- **只需要年月日** → date 对象
- **日常开发、日志、时间格式化** → datetime 对象
- **时间加减、日期推算、间隔计算** → timedelta

## 二、迭代器与生成器

迭代器与生成器是Python数据遍历的底层核心，是for循环、数据批量处理的底层原理，主打**惰性加载、节省内存**，是高阶函数、数据流处理的必备基础。学习顺序：可迭代对象 → 迭代器 → 生成器，层层递进。

### Python for 循环的本质

Python 的 `for` 是**迭代器协议的语法糖**，和 C 语言基于下标遍历的 for 完全不一样。

```python
for item in obj:
    循环体
```

底层等价伪代码：

```python
# 1.调用iter()，触发obj.__iter__()，拿到迭代器
iterator = iter(obj)
while True:
    try:
        # 2.调用next()，触发迭代器的__next__()
        item = next(iterator)
        # 3.执行循环体
        循环体
    except StopIteration:
        # 4.捕获终止异常，结束循环
        break
```

### 完整可运行对照示例

```python
my_list = [11,22,33]

# 普通for循环
for i in my_list:
    print(i)

print("====底层等价代码====")
it = iter(my_list)
while True:
    try:
        i = next(it)
        print(i)
    except StopIteration:
        break
```

### 关键知识点（面试高频）

1. `iter(obj)`

   ：调用对象的 

   ```python
   __iter__()
   ```

    方法，返回一个迭代器。

   - list、字符串、元组是**可迭代对象**，不是迭代器；经过`iter()`转换之后才得到迭代器。

2. **`next(iterator)`**：调用迭代器的 `__next__()`，返回下一个元素；没有数据抛出`StopIteration`。

3. for 循环**依靠捕获异常结束循环**，不是判断返回 None。

4. 迭代器是一次性消费：迭代器取完数据，再次 for 循环直接结束，不会输出内容。

```python
lst = [1,2,3]
it = iter(lst)
for x in it:
    print(x)
print("再次遍历")
for x in it:
    print(x) # 无任何输出，迭代器已经耗尽
```

1. 只要对象支持迭代器协议，就可以被 for 循环遍历：列表、字符串、元组、字典、range、生成器、文件对象。

### 一句话面试背诵版

> Python for 循环本质：对可迭代对象调用`iter()`获取迭代器，循环调用`next()`取值，捕获`StopIteration`异常结束循环。

### 1、可迭代对象（Iterable）

#### 1.1 定义与判断标准

凡是**实现了 __iter__() 方法**的对象，都是可迭代对象，支持for循环遍历。可迭代对象是数据容器，存储完整数据，不具备迭代能力，需要转换为迭代器才能逐个取值。

#### 1.2 常见可迭代对象

list、tuple、str、dict、set、range、生成器、迭代器等，均为可迭代对象。

#### 1.3 代码判断是否可迭代

```python
from collections.abc import Iterable

lst = [1, 2, 3]
print(isinstance(lst, Iterable))  # True
```

### 2、迭代器（Iterator）

#### 2.1 迭代器定义与判断标准

同时实现 **__iter__() + __next__()** 两个方法的对象，称为迭代器。迭代器是真正的“数据取值工具”，具备逐个获取数据的能力。

- **__iter__()**：返回迭代器自身
- **__next__()**：返回下一个数据，无数据则抛出异常

#### 2.2 可迭代对象与迭代器的核心关系

**可迭代对象 ≠ 迭代器**

可迭代对象是原材料，迭代器是取值工具；所有迭代器都是可迭代对象，但可迭代对象不一定是迭代器。

转换规则：通过 `iter(可迭代对象)` 可以生成迭代器。

```python
lst = [10, 20, 30]
# 可迭代对象转迭代器
it = iter(lst)
print(type(it))  # <class 'list_iterator'>
```

#### 2.3 核心方法：iter() 与 next()

**iter(obj)**：将可迭代对象转为迭代器

**next(iterator)**：从迭代器中取出下一个元素

#### 2.4 next() 无数据的返回规则与异常处理

迭代器数据取完后，继续调用next()**不会返回None**，直接抛出 **StopIteration** 终止迭代异常。

两种标准处理方案：

##### 方案1：try-except 捕获异常（底层原生写法）

```python
lst = [1, 2, 3]
it = iter(lst)

while True:
    try:
        res = next(it)
        print(res)
    except StopIteration:
        # 无数据时退出循环
        break
```

##### 方案2：for循环自动处理（工程常用）

for循环内部自动完成：**获取迭代器 → 不断next取值 → 自动捕获StopIteration并终止**，无需手动处理异常。

```python
lst = [1, 2, 3]
for i in lst:
    print(i)
```

#### 2.5 自定义迭代器类

手动实现 __iter__ 和 __next__，自定义迭代取值规则。

```python
# 自定义1~n数字迭代器
class MyIterator:
    def __init__(self, n):
        self.n = n
        self.count = 0

    # 迭代器必须实现iter方法，返回自身
    def __iter__(self):
        return self

    # 取值核心方法
    def __next__(self):
        self.count += 1
        if self.count <= self.n:
            return self.count
        else:
            # 数据取完，抛出终止异常
            raise StopIteration

# 调用
it = MyIterator(3)
for num in it:
    print(num)
```

#### 2.6 迭代器优缺点

##### 优点

- **极度节省内存**：不一次性加载全部数据，惰性取值，用一个取一个
- 适合超大文件、海量数据遍历，不会内存溢出
- 统一遍历接口，所有可迭代对象均可通用遍历逻辑

##### 缺点

- **一次性消费**：迭代器数据取完即空，无法重复遍历
- 不支持下标索引取值，不能切片、反向取值

### 3、生成器（特殊迭代器）

#### 3.1 生成器定义

生成器是**简化版的迭代器**，无需手动编写 __iter__、__next__ 方法，通过 **yield** 关键字快速创建迭代器，语法极简、开发效率极高。

本质：生成器 = 自动实现迭代器协议的惰性数据生成工具

#### 3.2 两种生成器创建方式

##### 方式1：生成器函数（yield关键字）

yield作用：暂停函数执行、返回数据、保留当前状态，下次取值从暂停位置继续执行。

```python
def gen_demo():
    yield 1
    yield 2
    yield 3

# 创建生成器对象
g = gen_demo()
print(next(g))  # 1
print(next(g))  # 2
```

##### 方式2：生成器表达式

语法：`(表达式 for 变量 in 可迭代对象)`，区别列表推导式：小括号、惰性加载

```python
# 列表推导式：一次性生成所有数据，占内存
lst = [i**2 for i in range(5)]

# 生成器表达式：惰性生成，节省内存
gen = (i**2 for i in range(5))
print(next(gen))
print(next(gen))
```

#### 3.3 生成器调用方式

- next() 逐个取值
- for 循环遍历取值（最常用）
- 强制转换列表：list(生成器)，一次性取出所有数据

#### 3.4 实战案例：质数生成器

```python
# 质数生成器：惰性生成指定范围内的所有质数
def prime_gen(max_num):
    for num in range(2, max_num + 1):
        flag = True
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                flag = False
                break
        if flag:
            yield num

# 调用生成器
g = prime_gen(30)
# 遍历获取所有质数
for p in g:
    print(p, end=" ")
```

## 三、闭包与装饰器

闭包是高阶函数的进阶形态，装饰器是**闭包+高阶函数**的工程产物，是Python代码解耦、功能拓展、切面编程的核心，是面试和项目高频考点。

### 1、闭包

#### 1.1 闭包定义

嵌套函数中，**内部函数引用了外部函数的局部变量，且外部函数返回内部函数**，形成闭包。闭包可以保留外层函数的变量状态，延长变量生命周期。

#### 1.2 闭包三大必备形成条件（缺一不可）

1. 函数嵌套（内层函数、外层函数）
2. 内层函数 **引用外层函数局部变量**
3. 外层函数 **返回内层函数对象**

#### 1.3 基础闭包案例

```python
def outer(x):
    # 外层局部变量
    num = x
    def inner():
        # 内层引用外层变量
        print(num + 10)
    return inner

# 接收内层函数，变量num被保留
f = outer(5)
f()  # 15
```

#### 1.4 闭包修改外层局部变量（nonlocal）

内层函数默认只能读取外层变量，**无法直接修改**，修改需使用 `nonlocal` 关键字声明。

```python
def outer():
    count = 0
    def inner():
        # 声明修改外层局部变量
        nonlocal count
        count += 1
        print(count)
    return inner

f = outer()
f()  # 1
f()  # 2
```

### 2、装饰器核心详解

#### 2.1 装饰器定义与本质

装饰器是**特殊的闭包+高阶函数**，专门用于**在不修改原函数代码、不修改原函数调用方式**的前提下，动态拓展函数功能。

#### 2.2 装饰器核心特点（开闭原则）

- ✅ 对扩展开放：可以无限新增功能
- ✅ 对修改关闭：不改动原有业务代码
- 动态增强函数：日志、计时、权限校验、异常捕获通用场景

#### 2.3 基础无参装饰器（标准写法）

```python
# 定义装饰器
def timer(func):
    def wrapper():
        print("函数执行前")
        func()
        print("函数执行后")
    return wrapper

# 使用装饰器语法糖 @  test() = timer(test)
@timer
def test():
    print("原函数执行")

test()
```

#### 2.4 被装饰函数带返回值处理

```python
def timer(func):
    def wrapper():
        print("执行前")
        # 接收原函数返回值并返回
        res = func()
        print("执行后")
        return res
    return wrapper

@timer
def add():
    return 10 + 20

print(add())
```

#### 2.5 带参数装饰器（双层嵌套传参）

装饰器本身需要传参时，外层再多嵌套一层函数接收参数。

```python
# 装饰器接收参数level
def log_level(level):
    def decorator(func):
        def wrapper():
            print(f"日志级别：{level}")
            func()
        return wrapper
    return decorator

# 给装饰器传参
@log_level(level="INFO")
def business():
    print("执行业务逻辑")

business()
```

#### 2.6解决装饰器适配不同参数数量函数：可变参数 `*args, **kwargs`

##### 问题根源

普通装饰器的 wrapper 写死固定参数，只能装饰无参 / 固定参数函数，参数数量不一致会直接报错。

```python
# 错误写法：只能装饰无参函数
def timer(func):
    def wrapper():
        print("执行前")
        res = func()
        print("执行后")
        return res
    return wrapper

@timer
def add(a,b):
    return a + b

add(1,2)  # 报错 wrapper() takes 0 positional arguments but 2 were given
```

##### 标准通用写法（万能兼容任意参数）

内层 wrapper 使用 `*args` 接收所有位置参数，`**kwargs` 接收所有关键字参数，再完整传给原函数。

```python
def timer(func):
    # *args 任意个位置参数，**kwargs任意个关键字参数
    def wrapper(*args, **kwargs):
        print("函数执行前置逻辑")
        # 把所有参数原封不动传给原函数
        result = func(*args, **kwargs)
        print("函数执行后置逻辑")
        return result
    return wrapper

# 1. 无参函数
@timer
def func1():
    print("无参数函数")
    return 100

# 2. 两个位置参数
@timer
def func2(a, b):
    return a + b

# 3. 多个参数+关键字参数
@timer
def func3(x, y, z=10):
    return x * y + z

# 全部正常调用
func1()
print(func2(3,5))
print(func3(2, 4, z=20))
```

##### 参数说明

1. `*args`：打包所有传入的**位置参数**，元组形式；
2. `**kwargs`：打包所有传入的**关键字参数**，字典形式；
3. 调用 `func(*args,**kwargs)` 代表解包，完整把参数传递给原函数；
4. 不管被装饰函数有 0/1 / 多个参数、有无默认关键字参数，全部兼容。

##### 补充：保留原函数信息（进阶优化）

多层装饰后原函数名字、文档注释会变成 wrapper，用`functools.wraps`修复，搭配可变参数一起写标准工程模板：

```python
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("开始执行")
        res = func(*args, **kwargs)
        print("执行结束")
        return res
    return wrapper

@timer
def demo(a, b, c=0):
    """测试函数"""
    return a + b + c

print(demo.__name__)  # 输出demo，不会变成wrapper
```

#### 2.7 类装饰器写法（通过__call__魔法方法）

通过类实现装饰器，依靠 **__call__** 魔法方法，让类实例可被调用。

```python
class MyDecorator:
    def __call__(self, func):
        def wrapper():
            print("类装饰器执行前")
            func()
            print("类装饰器执行后")
        return wrapper

@MyDecorator()
def hello():
    print("hello world")

hello()
```

### 3、property 面向对象专属装饰器

#### 3.1 作用

将类的方法伪装成属性调用，用于**私有属性的取值、赋值校验**，简化封装代码，隐藏方法调用痕迹。

#### 3.2 完整取值+赋值标准案例

```python
class Person:
    def __init__(self, age):
        self.__age = age

    # 取值装饰器
    @property
    def age(self):
        return self.__age

    # 赋值装饰器
    @age.setter
    def age(self, new_age):
        if 0 < new_age < 150:
            self.__age = new_age
        else:
            print("年龄不合法")

p = Person(18)
print(p.age)    # 像属性一样取值
p.age = 30      # 像属性一样赋值
print(p.age)
```

## 四、re模块

re 是 Python 内置字符串处理模块，核心用于**模糊匹配、提取、替换、分割文本**，常用于数据清洗、表单校验、简单文本筛选，属于轻量级工具模块，掌握核心函数即可满足绝大多数场景。

```python
# 全局导入（所有方法通用）
import re
```

### 1、核心重点：re.match() 函数

#### 1.1 语法规则

```python
re.match(正则规则, 目标字符串, 修饰符)
```

**核心特性（必考）**：仅从**字符串开头**匹配，开头不满足规则直接返回 None，不会向后检索匹配。

#### 1.2 返回值说明

- 匹配成功：返回 Match 匹配对象，通过 `.group()` 获取匹配内容
- 匹配失败：返回 None（直接调用 group() 会报错，需先判空）

#### 1.3 实战案例

```python
import re

# 开头匹配数字，匹配成功
res1 = re.match(r"\d+", "123abc456")
print(res1.group())  # 输出：123

# 开头无数字，匹配失败
res2 = re.match(r"\d+", "abc123456")
print(res2)  # 输出：None

# 安全写法（避免报错）
if res2:
    print(res2.group())
else:
    print("未匹配到内容")
```

### 2、re 模块其余常用核心函数

除 match 外，日常开发高频使用 5 个函数，分工明确、覆盖所有正则场景。

#### 2.1 re.search() 全局匹配首个内容

遍历整个字符串，匹配**第一个符合规则**的内容，不限开头、结尾，比 match 适用场景更广。

```python
import re
res = re.search(r"\d+", "abc789def123")
print(res.group())  # 输出：789
```

#### 2.2 re.findall() 匹配全部内容

查找字符串中**所有符合规则**的内容，返回列表，无匹配则返回空列表，是最常用的提取方法。

```python
import re
text = "学生成绩：95分、88分、100分"
result = re.findall(r"\d+", text)
print(result)  # 输出：['95', '88', '100']
```

#### 2.3 re.finditer() 迭代器匹配（省内存）

匹配全部内容，返回迭代器而非列表，适合**超长文本、大批量数据**，节省内存空间。

```python
import re
text = "a1b2c3d4"
it = re.finditer(r"\d", text)
for item in it:
    print(item.group())  # 逐个输出：1、2、3、4
```

#### 2.4 re.sub() 正则替换

语法：`re.sub(正则, 替换内容, 原字符串)`，批量替换文本中符合规则的内容。

```python
import re
text = "2025年08月04日"
# 将所有数字替换为*
new_text = re.sub(r"\d", "*", text)
print(new_text)  # 输出：****年**月**日
```

#### 2.5 re.split() 正则分割

按照正则规则匹配到的字符，分割字符串，返回分割后的列表，支持多符号分割。

```python
import re
s = "苹果,香蕉;橘子|葡萄"
res = re.split(r"[,;|]", s)
print(res)  # 输出：['苹果', '香蕉', '橘子', '葡萄']
```

### 3、通用拓展知识点（刚需）

#### 3.1 正则分组取值

通过`()` 对正则规则分组，用 `group(序号)` 提取对应分组内容，适用于精准提取指定字段。

```python
import re
res = re.match(r"(\d{4})-(\d{2})", "2025-08")
print(res.group(0))  # 完整匹配：2025-08
print(res.group(1))  # 第一分组：2025
print(res.group(2))  # 第二分组：08
```

#### 3.2 常用修饰符

- `re.I`：忽略大小写匹配
- `re.S`：让 `.` 匹配换行符（默认不匹配换行）

```python
import re
res = re.match(r"python", "Python123", flags=re.I)
print(res.group())  # 输出：Python
```

### 4、核心函数极简对比（必背）

- **match**：只匹配开头，精准校验前缀
- **search**：全局匹配，取第一个结果
- **findall**：全局匹配，取所有结果（列表）
- **finditer**：全局匹配，取所有结果（迭代器，省内存）
- **sub**：批量替换文本内容
- **split**：按规则分割字符串

### 5、极简避坑总结

- 正则建议加原始字符串 `r""`，避免转义字符冲突
- match 仅匹配开头，不要用于提取文本中间内容
- match/search 可能返回 None，必须判空后再调用 group()
- 大数据量优先用 finditer，避免 findall 占用过多内存

## 五、正则表达式

前文已总结 re 模块函数（match、search、findall、sub、split），本章专注**正则核心语法、匹配规则、面试重点**，是数据清洗、文本校验、爬虫的核心基础。

### 1、正则基础元字符（必背）

元字符是正则的基础匹配符号，用于模糊匹配文本内容。

- `.`：匹配任意单个字符（默认不匹配换行）
- `^`：匹配字符串**开头**
- `$`：匹配字符串**结尾**
- `\d`：匹配任意数字 0-9
- `\w`：匹配字母、数字、下划线
- `\s`：匹配空白字符（空格、制表符、换行）
- `[]`：匹配括号内任意单个字符
- `|`：或逻辑，匹配左右任意一个规则

### 2、重复匹配符号

- `*`：匹配前一个字符 0次或多次
- `+`：匹配前一个字符 1次或多次
- `?`：匹配前一个字符 0次或1次
- `{m}`：精准匹配 m 次
- `{m,n}`：匹配 m~n 次

### 3、贪婪匹配与非贪婪匹配（面试重点）

默认所有重复匹配符号都是**贪婪匹配**：尽可能匹配最长内容。

在匹配符号后加 `?` 转为**非贪婪匹配**：尽可能匹配最短内容。

```python
import re

text = "<html>内容<body>"

# 贪婪匹配（匹配最长）
res1 = re.findall(r"<.*>", text)
print(res1)  # ['<html>内容<body>']

# 非贪婪匹配（匹配最短）
res2 = re.findall(r"<.*?>", text)
print(res2)  # ['<html>', '<body>']
```

### 4、分组捕获

使用 `()` 可以对正则规则分组，精准提取指定片段内容。

```python
import re

res = re.search(r"(\d{4})-(\d{2})-(\d{2})", "2025-08-05")
print(res.group(0))  # 完整匹配：2025-08-05
print(res.group(1))  # 第一组：2025
print(res.group(2))  # 第二组：08
```

### 5、原始字符串 r"" 作用

正则中大量使用 `\` 转义符，Python 默认会解析转义字符，导致正则失效。

加 `r""` 原始字符串：**不解析转义符，原样传递给正则引擎**，写正则统一推荐使用。

```python
import re

# 推荐写法
res = re.findall(r"\d+", "abc123def456")
print(res)
```

### 6、正则核心总结与避坑

- 正则优先使用原始字符串 `r""`
- 默认贪婪匹配，截取标签、括号内容必须用非贪婪 `.*?`
- `^` 和 `$` 可精准限制整体字符串格式
- 分组用于精准提取局部数据，是正则最常用高级功能

## 六、Python一切皆对象

本章内容**纯面试导向**，日常业务开发几乎不用，仅用于应对面试问答、看懂框架底层原理。

### 1、一切皆对象 核心定义

Python 中**所有数据都是对象**：数字、字符串、列表、函数、实例、类，全部是对象。

核心层级关系（面试必背）：

- 实例对象 → 由 **自定义类** 创建
- 自定义类 → 由 **元类（type）** 创建

```python
class Person:
    pass

p = Person()
print(type(p))      # <class '__main__.Person'> 实例由Person创建
print(type(Person)) # <class 'type'> 类本身由type元类创建
```

### 2、type 元类核心作用

**元类：用来创建类的类，Python 默认元类是 type**。

type 两种核心用法：

#### 用法1：查看对象类型

```python
print(type(123))
print(type("abc"))
```

#### 用法2：动态创建类（type(类名, 父类元组, 属性字典)）

```python
# 动态创建一个空类
Student = type("Student", (), {"name": "小明"})
s = Student()
print(s.name)
```

### 3、函数方式定义元类（旧式写法、了解即可）

老式、淘汰写法，面试极少考、工作不用，仅做认知了解。

```python
def my_meta(class_name, parents, attrs):
    print("元类执行")
    return type(class_name, parents, attrs)

class Dog(metaclass=my_meta):
    pass
```

### 4、类继承type自定义元类（面试重点）

主流标准元类写法：继承 `type`，重写 `__new__` 方法。

关键区别（必考）：

- 类的 `__new__`：**创建实例对象时执行**
- 元类的 `__new__`：**定义类的瞬间就执行**

```python
# 自定义元类
class MyMeta(type):
    def __new__(cls, name, bases, attrs):
        print("元类干预类的创建")
        # 必须调用父类__new__完成类的创建
        return super().__new__(cls, name, bases, attrs)

# 使用自定义元类
class Cat(metaclass=MyMeta):
    pass
```

元类核心用途：**干预、校验、修改类的创建过程**，框架底层大量使用。

### 5、单例模式设计（面试高频压轴）

单例模式定义：**一个类无论实例化多少次，始终只返回唯一一个实例对象**。

适用场景：全局配置类、数据库连接、日志对象。

#### 方式1：重写 __new__ 实现单例（简单常用）

```python
class Singleton:
    # 保存唯一实例
    __instance = None

    def __new__(cls, *args, **kwargs):
        # 没有实例则创建，有则直接返回
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

a = Singleton()
b = Singleton()
print(a == b)  # True
```

#### 方式2：元类实现单例（面试必问高阶写法）

```python
class SingletonMeta(type):
    __instance = None
    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance

# 通过元类控制单例
class Config(metaclass=SingletonMeta):
    pass

c1 = Config()
c2 = Config()
print(c1 == c2)  # True
```

### 6、元类与单例 面试总结（背诵版）

- Python 一切皆对象，类是 type 元类的实例
- 元类是创建类的类，默认元类是 type
- 自定义元类通过继承 type、重写 __new__ 实现，在类定义阶段生效
- 单例模式保证类全局唯一实例，常用 __new__、自定义元类两种实现
- 元类仅用于框架底层，业务开发禁止随意使用，可读性差、维护成本高

