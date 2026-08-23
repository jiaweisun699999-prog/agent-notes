> 📌 **[AI 大模型与云原生全栈知识库](./README.md)** / **模块二：Python 编程基础与进阶**
> 🏠 [返回主页 README](./README.md) \| ⚡ [面试 30 分钟速记](./interview/00_面试冲刺30分钟速记卡片.md) \| 🎓 [本模块面试题](./interview/01_云原生与Python高频面试题.md)

---

# Python基础

## 一、Python介绍

### 1、Python产生背景

创始人：吉多・范罗苏姆（Guido van Rossum），人称 “龟叔”

诞生时间：1991 年正式发布第一版

诞生初衷：解决 ABC 语言扩展性差、不易移植、仅能教学使用的痛点，打造一款简洁、易读、可拓展的通用编程语言

版本区分：

- Python2：2020 年停止官方维护，语法存在编码、打印语法缺陷，现已淘汰
- Python3：主流学习 / 工作版本，向下不兼容 2，推荐 3.8~3.12 稳定版本

### 2、Python核心思想

核心宗旨：**优雅、明确、简单**

常用核心准则：

1. 优美胜于丑陋
2. 明了胜于晦涩
3. 简洁胜于复杂
4. 可读性很重要
5. 错误绝不应该悄悄忽略

### 3、Python特性

解释型语言：无需提前编译，代码逐行执行，开发调试效率高

跨平台：一份代码可在 Windows、MacOS、Linux 运行

语法简洁：大量简化语法，代码量远少于 C/Java，上手门槛低

面向对象：天然支持面向对象编程，万物皆对象

丰富第三方库：数据分析、爬虫、人工智能、web 开发、自动化工具库齐全

可拓展：可与 C/C++ 混合开发，弥补运行速度短板

开源免费：商用、个人使用无版权费用

## 二、Python安装

### 1、Python解释器的安装步骤

#### （1）下载安装包

官网：[https://www.python.org/downloads/](https://link.wtturl.cn/?target=https%3A%2F%2Fwww.python.org%2Fdownloads%2F&scene=im&aid=497858&lang=zh)，选择对应系统位数稳定版

#### （2）安装关键操作

Windows 系统务必勾选：`Add Python to PATH`（自动配置环境变量）

若未勾选，需手动配置两个路径：

1. python.exe 主程序路径（如`C:\Python311\`）
2. pip 工具路径（如`C:\Python311\Scripts\`）

#### （3）环境变量手动配置步骤

1. 此电脑右键→属性→高级系统设置→环境变量
2. 在系统变量中找到`Path`，双击编辑
3. 新建两条记录，分别粘贴 exe 路径、Scripts 路径，保存全部窗口

#### （4）验证安装（CMD 终端执行两条命令）

```python
# 查看Python版本，出现版本号即成功
python --version
# 查看包管理工具pip版本
pip --version
```

报错 “不是内部命令”= 环境变量配置失败，重新检查路径

### 2、PyCharm安装

#### （1）版本区分

- 社区版 Community：免费，够用基础学习
- 专业版 Professional：付费，支持 web、数据库、远程开发等企业功能，学生可凭学生证免费申请授权

#### （2）基础安装流程

1. 官网下载对应系统安装包，一路下一步
2. 勾选创建桌面快捷方式、关联.py 文件
3. 首次打开：新建项目，选择 Python 解释器（绑定已安装的 python.exe）

#### （3）PyCharm 高频快捷键（Windows）

|       快捷键       |          功能          |
| :----------------: | :--------------------: |
|      Ctrl + S      |        保存文件        |
|      Ctrl + /      |  单行注释 / 取消注释   |
|      Ctrl + D      |    复制当前一行代码    |
|      Ctrl + Y      |       删除当前行       |
|   Ctrl + Alt + L   |     代码自动格式化     |
|   Shift + Enter    |     快速新建下一行     |
| Ctrl + Alt + Enter |     快速新建上一行     |
| Ctrl + Shift + ↑ ↓ | 当前代码上移或下移一行 |
| Ctrl + Shift + F10 |      运行当前脚本      |
|        Tab         |        代码缩进        |
|    Shift + Tab     |      代码反向缩进      |

## 三、Python基础语法

### 1、注释

作用：给代码添加说明文字，程序运行时会忽略注释内容，分为 3 类

1. 单行注释：`# 注释内容`

```python
# 这是单行注释，用来解释下方代码
print("Hello Python")
```

1. 多行注释（文档注释，三引号）：`"""内容"""` / `'''内容'''`

```python
"""
多行注释，可写多行说明
常用于函数、文件开头做功能描述
"""
print("多行注释演示")
```

1. 注释规范：关键逻辑、复杂运算必须加注释，冗余简单代码无需注释

### 2、变量

#### （1）变量概念

内存中开辟一块空间存储数据，变量名指向这块内存，方便重复调用数据

#### （2）变量定义语法

```python
变量名 = 数据值
```

```python
name = "小明"
age = 18
```

#### （3）变量命名规范（强制遵守）

1. 只能由字母、数字、下划线组成，**不能以数字开头**
2. 区分大小写：Name 和 name 是两个不同变量
3. 禁止使用 Python 内置关键字（if、for、while、print、class 等）
4. 推荐命名风格：
   - 普通变量：下划线命名 user_name、student_age
   - 常量：全大写 MAX_NUM = 100

#### （4）变量数据基础类型

- 数字：int 整数、float 浮点数
- 字符串：str，使用单 / 双 / 三引号包裹
- 布尔：bool，只有 True / False

#### （5）变量查看与类型转换

```python
# 查看数据类型 type()
num = 10
print(type(num))

# 类型转换
a = "20"
b = int(a)  # 字符串转整数
```

### 3、运算符

#### （1）算术运算符

| 符号 |       作用       |  示例   |
| :--: | :--------------: | :-----: |
|  +   |        加        |  3+2=5  |
|  -   |        减        |  3-2=1  |
|  *   |        乘        |  3*2=6  |
|  /   | 除（结果浮点数） | 5/2=2.5 |
|  //  | 整除（向下取整） | 5//2=2  |
|  %   |       取余       |  5%2=1  |
|  **  |      幂运算      | 2**3=8  |

扩展1：幂运算、立方根计算（** 运算符 /pow () 函数）

```python
# ** 幂运算
print(2 ** 3)       # 2的三次方=8
print(8 ** (1/3))   # 8的立方根

# pow(底数, 指数) 等价 x**y
print(pow(2, 3))
print(pow(8, 1/3))
# 三参数pow：pow(x,y,z) = x**y % z
print(pow(5, 2, 3))
```

扩展2：浮点数精度丢失问题与 decimal 精确计算

计算机二进制存储小数会存在精度误差，典型示例：

```python
print(0.1 + 0.2)  # 输出 0.30000000000000004，而非0.3
```

金融高精度场景使用 `decimal` 模块处理，**数值必须传字符串**：

```python
from decimal import Decimal
a = Decimal("0.1")
b = Decimal("0.2")
print(a + b)  # 精准输出 0.3
```

#### （2）赋值运算符

```python
=、+=、-=、*=、/=、//=、%=
```

```python
a = 10
a += 5  # 等价 a = a +5
```

#### （3）比较运算符（返回布尔值 True/False）

```python
>、<、>=、<=、==相等、!=不相等
```

#### （4）逻辑运算符

- and：两边都成立才为 True
- or：任意一边成立即为 True
- not：取反

### 4、输出 print ()

#### 基础用法

```python
# 直接输出文字
print("Hello World")
# 输出变量
name = "小红"
print(name)
# 同时输出多个内容，逗号分隔自动加空格
print(name, 18)
```

#### 格式化输出（4 种完整写法，含占位符 %、f-string、format、逗号拼接）

##### 方式 1：逗号简单拼接（仅临时打印，无法控制格式）

```python
age = 18
print("今年", age, "岁")
```

##### 方式 2：% 占位符格式化（老式写法，支持固定宽度、小数保留）

常用占位符说明：

- `%d`：整数；`%5d`：整数占 5 字符宽度，左补空格；`%05d`：占 5 位不足补 0
- `%f`：浮点数；`%.2f`：浮点数保留 2 位小数
- `%s`：通用字符串

```python
age = 18
score = 92.356
# 基础整数、小数控制
print("年龄：%d" % age)
print("分数保留两位小数：%.2f" % score)
# 固定字符宽度
print("年龄占5格：%5d" % age)
# 多个变量同时输出
print("姓名：%s，年龄：%d，成绩：%.1f" % ("小红", age, score))
```

##### 方式 3：f-string（Python3.6+ 推荐，简洁强大，优先使用）

大括号内可直接写变量、运算，支持数字格式控制

```python
age = 18
score = 92.356
# 基础嵌入变量
print(f"今年{age}岁")
# 内嵌表达式运算
print(f"明年年龄：{age + 1}")
# 控制数字宽度、小数位数
print(f"分数保留2位小数：{score:.2f}")
print(f"年龄占5个字符宽度：{age:5d}")
```

**方式 4：format 格式化（兼容低版本 Python）**

```python
age = 18
score = 92.356
# 基础填充
print("今年{}岁".format(age))
# 控制小数、宽度
print("分数保留两位小数：{:.2f}".format(score))
print("年龄占5格：{:5d}".format(age))
```

#### print 核心参数 end 控制换行

print 默认结尾 `end="\n"` 自动换行，修改 `end=""` 可取消换行，也可自定义结尾符号

```python
# 默认自动换行
print("第一行")
print("第二行")

# end="" 不换行输出
print("1", end="")
print("2", end="")
print("3")  # 输出结果：123

# 自定义结尾分隔符
print("苹果", end="、")
print("香蕉")  # 输出结果：苹果、香蕉
```

### 5、输入 input ()

#### 基础语法

```python
变量 = input("提示文字")
```

#### 核心特性：input 接收的所有输入**默认都是字符串 str 类型**

```python
# 获取用户输入姓名
username = input("请输入你的名字：")
# 获取数字输入，必须手动转类型
height = input("请输入身高：")
height = float(height)
```

## 四、选择与循环

### 1、if

#### 1.1 单分支 if

语法：

```python
if 条件表达式:
    条件成立执行的代码块
```

执行逻辑：条件为 `True`，执行缩进内代码；条件为 `False`，直接跳过。

示例：

```python
age = 20
if age >= 18:
    print("已成年")
```

#### 1.2 双分支 if ... else

语法：

```python
if 条件:
    条件成立代码
else:
    条件不成立代码
```

二选一执行，两个代码块只会走其中一个。

示例：

```python
age = 16
if age >= 18:
    print("成年")
else:
    print("未成年")
```

#### 1.3 多分支 if ... elif ... else

语法：

```python
if 条件1:
    代码1
elif 条件2:
    代码2
elif 条件3:
    代码3
else:
    所有条件都不满足执行
```

执行规则：从上往下依次判断，遇到第一个成立条件就执行对应代码，后续不再判断；else 可选，兜底所有不满足的情况。

示例：

```python
score = 80
if score >= 90:
    print("优秀")
elif score >= 60:
    print("及格")
else:
    print("不及格")
```

### 2、while（未知循环次数时使用）

#### 2.1 基础 while 循环

语法：

```python
while 循环条件:
    循环体代码
    计数器更新（避免死循环）
```

逻辑：条件为 True 重复执行循环体；条件 False 结束循环。

示例：打印 1~5

```python
i = 1
while i <= 5:
    print(i)
    i += 1
```

死循环（条件永远为 True）：

```python
while True:
    print("无限循环")
```

#### 2.2 while ... else 结构

语法：

```python
while 条件:
    循环体
else:
    循环正常结束后执行的代码
```

关键特性：

1. 循环**没有被 break 打断、正常走完**，才会执行 else；

2. 如果循环内触发 

   ```
   break
   ```

    跳出循环，else 代码不会执行。

   示例：

```python
i = 1
while i <= 3:
    print(i)
    i += 1
else:
    print("循环正常结束")
```

带 break 跳过 else：

```python
i = 1
while i <= 3:
    if i == 2:
        break
    print(i)
    i += 1
else:
    print("不会执行这句")
```

#### 2.3 Python 实现等效 do-while（标准写法）

利用 `while True` + 末尾 `break` 判断，模拟先执行、后判断：

```python
i = 1
while True:
    # 循环体（一定会先执行1次）
    print(i)
    i += 1
    # 后置判断条件，不满足就退出
    if i > 5:
        break
```

### 3、for（已知循环次数、遍历容器优先使用）

#### 3.1 for + range () 数字循环

`range(起始,结束,步长)`，左闭右开区间（包含起始，不包含结束）

三种用法：

1.range(n)：0 ~ n-1

```python
for i in range(3):
    print(i)  # 0 1 2
```

2.range(a, b)：a ~ b-1

```python
for i in range(1, 6):
    print(i)  # 1 2 3 4 5
```

3.range (a,b,step)：带步长

```python
# 1~10 偶数
for i in range(2, 11, 2):
    print(i)
```

拓展：range倒序输出

range (起始值，终止值，步长负数)

规则：起始 > 终止，步长写 `-2`，区间左闭右开

```python
# 从10开始，到0结束（取不到0），每次减2
for i in range(10, 0, -2):
    print(i)
```

运行结果：

```python
10
8
6
4
2
```

#### 3.2 for ... else 结构

规则和 while else 完全一致：循环完整遍历结束、未触发 break 才执行 else。

语法：

```python
for 变量 in 可迭代对象:
    循环体
else:
    正常遍历完成执行
```

示例：

```python
for i in range(1,4):
    print(i)
else:
    print("遍历完毕，无break中断")
```

break 中断示例：

```python
for i in range(1,4):
    if i == 2:
        break
    print(i)
else:
    print("不会运行")
```

#### 3.3 进阶for循环大全一览

#### ①直接遍历字符串 str

逐个取出每个字符

```python
s = "python"
for char in s:
    print(char)
```

#### ②遍历列表 list

```python
lst = [10, 20, 30, "张三"]
for item in lst:
    print(item)
```

#### ③遍历元组 tuple

```python
t = (1, 3, 5)
for num in t:
    print(num)
```

#### ④遍历集合 set（无序，顺序不固定）

```python
s = {2, 4, 6}
for i in s:
    print(i)
```

#### ⑤遍历字典 dict（三种常用写法）

```python
info = {"name":"小明", "age":18}

# 1. 只遍历键
for k in info:
    print(k)

# 2. 遍历 键+值
for k, v in info.items():
    print(k, v)

# 3. 只遍历值
for v in info.values():
    print(v)
```

#### ⑥reversed () 反向遍历（不修改原数据）

```python
lst = [1,2,3,4]
for i in reversed(lst):
    print(i)
```

#### ⑦enumerate () 遍历同时拿到下标 + 值（高频实用）

```python
lst = ["苹果", "香蕉", "橙子"]
for index, val in enumerate(lst):
    print(index, val)
```

### 4、通用控制关键字（循环通用）

#### break

直接终止整个循环，跳出循环，不会执行对应 else。

#### continue

立刻结束本次循环，直接进入下一次循环，后续代码不执行。

示例 continue：

```python
# 只打印奇数
for i in range(1,6):
    if i % 2 == 0:
        continue
    print(i)
```

## 五、字符串的常用操作

### 5.1 字符串定义、索引与切片

#### 5.1.1 三种定义方式

```python
s1 = '单引号字符串'
s2 = "双引号字符串"
s3 = '''三引号支持
多行文本内容'''
```

#### 5.1.2 索引取值

规则：下标从 0 开始；负数代表从末尾倒数取值

```python
s = "python"
print(s[0])   # p 取第一个字符
print(s[-1])  # n 取最后一个字符
```

#### 5.1.3 切片 `[起始:结束:步长]`

左闭右开区间：包含起始下标，不包含结束下标

```python
s = "abcdef"
print(s[1:4])    # bcd
print(s[:3])     # abc 从头截取到下标3之前
print(s[2:])     # cdef 从下标2截取到末尾
print(s[::-1])   # fedcba 字符串整体反转
print(s[::2])    # ace 步长2，隔一个字符取一个
```

### 5.2 获取信息类内置方法

`len(字符串)`：获取字符串总字符长度

```python
s = "hello"
print(len(s)) # 5
```

`find(子串)`：查找子串下标，找不到返回 -1

```python
s = "hello python"
print(s.find("py"))   # 6
print(s.find("java")) # -1
```

`index(子串)`：查找子串下标，找不到直接报错

```python
s = "hello python"
print(s.index("he")) # 0
```

`count(子串)`：统计子串出现的次数

```python
s = "aaabbb"
print(s.count("a")) # 3
```

`startswith("xx")`：判断字符串是否以指定内容开头，返回布尔值

`endswith("xx")`：判断字符串是否以指定内容结尾，返回布尔值

```python
s = "test.txt"
print(s.endswith(".txt")) # True
```

### 5.3 大小写转换方法

```python
s = "Hello Python"
print(s.upper())        # HELLO PYTHON 全部转为大写
print(s.lower())        # hello python 全部转为小写
print(s.title())        # Hello Python 每个单词首字母大写
print(s.capitalize())   # Hello python 仅第一个字符大写，其余小写
```

### 5.4 去除首尾字符（空格、自定义符号）

```python
s = "  python  "
print(s.strip())   # 去除左右两侧空白
print(s.lstrip())  # 只去除左侧空白
print(s.rstrip())  # 只去除右侧空白

# 可传入参数，删除首尾指定字符
s2 = ",,hello,"
print(s2.strip(",")) # hello
```

### 5.5 字符串分割与拼接

#### 5.5.1 split () 分割：字符串 → 列表

```python
# 按指定符号分割
s = "苹果,香蕉,橙子"
lst = s.split(",")
print(lst) # ['苹果', '香蕉', '橙子']

# 不传参数，自动按任意空白（空格/换行/制表符）分割
s2 = "a b  c"
print(s2.split()) # ['a','b','c']
```

#### 5.5.2 join () 拼接：列表 → 字符串

```python
lst = ["2026","08","01"]
res = "-".join(lst)
print(res) # 2026-08-01
```

### 5.6 字符替换 replace ()

```python
s = "hello java"
new_s = s.replace("java", "python")
print(new_s) # hello python

# 第三个参数控制替换次数
s2 = "aaaaa"
print(s2.replace("a","b",2)) # bbaaa
```

### 5.7 内容判断方法（返回 True / False）

- `isdigit()`：判断字符串是否全部为纯数字
- `isalpha()`：判断字符串是否全部由字母组成
- `isalnum()`：判断仅包含字母 + 数字，无符号、空格
- `isspace()`：判断字符串全部由空白字符构成

```python
print("123".isdigit())    # True
print("12a3".isdigit())   # False
print("abc".isalpha())    # True
print("a123".isalnum())   # True
print("   ".isspace())    # True
```

### 5.8 填充对齐方法

```python
s = "123"
print(s.center(10, "*")) # ***123**** 总宽度10，居中，*填充
print(s.ljust(10, "#"))  # 123####### 总宽度10，左对齐
print(s.rjust(10, "0"))  # 0000000123 总宽度10，右对齐（数字补零常用）
```

### 5.9 字符串格式化输出

#### 5.9.1 f-string（Python3.6+ 推荐，简洁）

```python
name = "小明"
print(f"姓名：{name}")
```

#### 5.9.2 % 占位符格式化（老式写法）

```python
print("年龄：%d" % 18)
```

#### 5.9.3 format 格式化

```python
age = 18
print("今年{}岁".format(age))
```

## 六、Python的容器

### 6.1 容器总体概览

#### 6.1.1 容器概念

容器就是可以存放多个数据的复合数据类型，能批量存储、管理一组数据。

#### 6.1.2 Python 四大容器

1. 列表 list
2. 元组 tuple
3. 字典 dict
4. 集合 set

#### 6.1.3 简单分类

- 序列（有序、支持下标索引、切片）：

  容器序列：list、tuple；

  补充：字符串 str 属于序列，但不属于容器

- 无序列容器（不支持数字下标）：dict、set

### 6.2 列表 list

#### 6.2.1 概念与特性

1. 语法：`[]` 包裹，逗号分隔元素
2. 有序、可变容器，支持增删改查
3. 可存放任意数据类型（数字、字符串、列表等）
4. 允许元素重复

```python
lst = [10, "张三", True, [1,2]]
```

> 列表是可变类型，修改操作不会产生新列表，内存地址不变。

#### 6.2.2 常用操作

##### 1）增

- `append(元素)`：末尾追加单个元素
- `insert(下标, 元素)`：指定下标插入
- `extend(可迭代对象)`：批量追加一组数据

```python
lst = [1,2]
lst.append(3)
lst.insert(0, 0)
lst.extend([4,5])
print(lst) # [0,1,2,3,4,5]
```

##### 2）删

- `pop(下标)`：按下标删除，返回被删除元素；不传下标默认删最后一个
- `remove(元素)`：删除第一个匹配的元素，无匹配则报错
- `del 列表[下标]`：按下标删除
- `clear()`：清空列表所有元素

```python
lst = [1,2,3]
lst.pop()
lst.remove(1)
lst.clear()
```

##### 3）改

通过下标直接赋值修改：`lst[下标] = 新值`

```python
lst = [10,20]
lst[0] = 99
print(lst) # [99, 20]
```

##### 4）查

- 索引：`lst[下标]`、`lst[-1]`
- 切片：`lst[起始:结束:步长]`
- `index(元素)`：查找元素下标
- `count(元素)`：统计元素出现次数

##### 5）其他常用方法

- `sort()`：原地升序排序；`sort(reverse=True)` 降序
- `reverse()`：原地反转列表
- `len(lst)`：获取列表长度

### 6.3 元组 tuple

#### 6.3.1 概念与特性

1. 语法：`()` 包裹，逗号分隔
2. **有序、不可变**，创建后不能增删改元素
3. 可存任意类型，允许重复元素
4. 单元素元组必须加逗号 `(5,)`，否则只是括号表达式

```python
t1 = (1, 2, "abc")
t2 = (66,)  # 正确单元素元组
```

> 元组整体不可变，但如果内部嵌套列表，列表里的数据可以修改。

#### 6.3.2 常用操作

只能查询，无修改、删除方法

1. 索引、切片：同列表
2. `len(tuple)`：长度
3. `count(元素)`：统计个数
4. `index(元素)`：查找下标
5. 拆包赋值

```python
t = (10,20)
a, b = t
print(a, b) # 10 20
```

### 6.4 序列通用操作（list /tuple/str 共用）

序列：有序、支持数字索引、切片的类型

1. 索引取值 `[下标]`、负索引倒数取
2. 切片 `[start:end:step]`
3. `len()` 获取长度
4. `+` 拼接两个同类型序列
5. `*` 重复序列 `[1,2] * 3 → [1,2,1,2,1,2]`
6. `in / not in` 判断元素是否存在

```python
lst = [1,2,3]
print(2 in lst)    # True
print(9 not in lst)# True
```

> 【补充】`in` 作用于字典时，只会判断键 key，不会判断值 value。

1. `max()` / `min()`：取最大、最小元素（元素为数字时）

### 6.5 字典 dict

#### 6.5.1 概念与特性

1. 语法：`{键:值, 键2:值2}` 键值对存储
2. Python3.7+ 有序；无数字下标，靠**键 key**取值
3. key 要求：必须是**不可变类型**（int/str/tuple），唯一不可重复
4. value 无限制，任意类型均可

```python
info = {"name":"小明", "age":18}
```

> 【避坑提示】列表、集合不能当作字典的 key；`pop()` 是根据键删除，和列表 pop 用法不同。

#### 6.5.2 常用操作

##### 1）增 / 改

`字典[键] = 值`：键存在则修改，不存在则新增

```python
info = {"name":"小明"}
info["age"] = 18    # 新增
info["name"] = "小红" # 修改
```

##### 2）删

- `pop(key)`：删除指定键，返回对应值
- `del 字典[key]`：删除键值对
- `clear()`：清空字典

##### 3）查

- `字典[key]`：按键取值，不存在报错
- `get(key, 默认值)`：取值，无键返回默认值（推荐）

```python
print(info.get("gender", "未知"))
```

##### 4）遍历三方法

```python
info = {"name":"小明", "age":18}
for k in info.keys():       # 只遍历键
    print(k)
for v in info.values():     # 只遍历值
    print(v)
for k, v in info.items():   # 同时遍历键+值
    print(k, v)
```

### 6.6 集合 set

#### 6.6.1 概念与特性

1. 语法：`{元素1,元素2}`；空集合只能写 `set()`，`{}` 是空字典
2. **无序、元素自动去重**
3. 元素必须是不可变类型（不能放 list、dict）
4. 可变集合，支持增删，无索引、无切片

```python
s = {1,2,2,3}
print(s) # {1,2,3} 自动去重
```

> 【避坑提示】集合`pop()`随机删除一个元素，不是按下标删除；remove 找不到元素会报错，discard 不会。

#### 6.6.2 常用操作

##### 1）增

- `add(元素)`：添加单个元素
- `update(可迭代对象)`：批量添加

##### 2）删

- `remove(元素)`：删除元素，不存在报错
- `discard(元素)`：删除元素，不存在不报错（推荐）
- `pop()`：随机删除一个元素
- `clear()`：清空集合

##### 3）集合运算（交并差）

```python
a = {1,2,3}
b = {3,4,5}
print(a & b)  # 交集 {3} 两者共有
print(a | b)  # 并集 {1,2,3,4,5} 全部合并去重
print(a - b)  # 差集 {1,2} a独有
```

### 6.7 可变类型与不可变类型

#### 6.7.1 概念

- 可变类型：数据创建后，**内存地址不变**，内容可以直接修改
- 不可变类型：数据不能原地修改，一旦修改会生成新数据，内存地址改变

#### 6.7.2 完整分类

1. **不可变类型（值不能原地修改）**

   数字 (int/float/bool)、字符串 str、元组 tuple

2. **可变类型（支持原地增删改）**

   列表 list、字典 dict、集合 set

#### 6.7.3 简单判断技巧

用 `id(变量)` 查看内存地址，修改后地址不变 = 可变；地址变化 = 不可变。

```python
# 不可变示例
a = 10
print(id(a))
a = 20
print(id(a)) # 地址改变

# 可变示例
lst = [1,2]
print(id(lst))
lst.append(3)
print(id(lst)) # 地址不变
```

### 补充汇总

#### 四大容器核心特点速记表

|    容器    |  是否有序   |       是否可重复       | 是否可变 |       取值方式       |
| :--------: | :---------: | :--------------------: | :------: | :------------------: |
| list 列表  |    有序     |        允许重复        |   可变   |       数字下标       |
| tuple 元组 |    有序     |        允许重复        |  不可变  |       数字下标       |
| dict 字典  | 有序 (3.7+) | key 唯一，value 可重复 |   可变   |      key 键取值      |
|  set 集合  |    无序     |        自动去重        |   可变   | 无下标，无法单独取值 |

---
> 🏠 **[返回主页 README](./README.md)** \| ◀️ **上一篇：[02. Kubernetes 总结](./02Kubernetes%E6%80%BB%E7%BB%93.md)** \| ▶️ **下一篇：[05. Python 文件流总结](./05Python%E6%96%87%E4%BB%B6%E6%B5%81%E6%80%BB%E7%BB%93.md)** \| 🎓 **[进入本模块面试高频题](./interview/01_云原生与Python高频面试题.md)**
