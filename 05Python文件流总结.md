> 📌 **[AI 大模型与云原生全栈知识库](./README.md)** / **模块二：Python 编程基础与进阶**
> 🏠 [返回主页 README](./README.md) \| ⚡ [面试 30 分钟速记](./interview/00_面试冲刺30分钟速记卡片.md) \| 🎓 [本模块面试题](./interview/01_云原生与Python高频面试题.md)

---

# Python文件流总结

文件IO（文件流）是Python工程必备核心技能，用于实现程序与本地磁盘的数据交互，完成文件读取、写入、拷贝、目录管理等操作。本文按照 **概念→打开关闭→文本读写→指针操作→二进制读写→路径管理→异常处理→实战避坑** 的标准学习顺序整理，知识点层层递进、无逻辑断层，全部配套可运行代码。

# 一、文件流基础概念

## 1\.1 什么是文件IO

文件IO全称文件输入输出，指程序读取本地文件数据、向本地文件写入数据的过程。程序无法直接操作磁盘文件，需要通过**文件流（文件对象）**作为中间桥梁完成数据交互。

## 1\.2 文件分类

### 1）文本文件

存储字符串文本数据，如 `.txt、.py、.json、.md`，读写需要指定编码格式。

### 2）二进制文件

存储字节数据，无编码概念，如图片、视频、音频、压缩包、exe程序。

## 1\.3 文件操作标准流程

固定三步：**打开文件 → 读写文件 → 关闭文件**

核心注意：文件打开后必须关闭，否则会造成**文件句柄泄露、内存占用、数据缓存未写入、文件被占用无法修改**等问题。

# 二、文件打开与关闭

## 2\.1 基础语法

```python
open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True)
```

常用核心参数：

- **file**：文件路径（相对路径 / 绝对路径）

- **mode**：文件打开模式，默认只读 `r`

- **encoding**：文本编码，文本文件必须指定，常用 `utf-8`

## 2\.2 六大核心打开模式（必考）

|模式|含义|文件不存在|原有内容|
|---|---|---|---|
|r|只读模式（默认）|报错|保留|
|w|只写模式|新建文件|**清空覆盖**|
|a|追加写入模式|新建文件|保留，末尾追加|
|r\+|读写模式|报错|保留|
|w\+|读写模式|新建文件|**清空覆盖**|
|a\+|读写追加模式|新建文件|保留，末尾追加|

后缀加 **b**（rb/wb/ab）：代表二进制模式，无需编码，读写字节数据

## 2\.3 手动打开关闭

```python
# 手动打开文件
f = open("test.txt", "w", encoding="utf-8")

# 写入内容
f.write("Hello Python文件流")

# 手动关闭文件（必须执行）
f.close()
```

## 2\.4 with 上下文管理器（工程推荐写法）

自动关闭文件，无需手动调用 close\(\)，即使代码报错也能安全释放文件资源，是企业开发标准写法。

```python
# with 自动打开、自动关闭
with open("test.txt", "w", encoding="utf-8") as f:
    f.write("上下文管理器安全读写")

```

# 三、文本文件读写操作

## 3\.1 读取文件四大方法

### 1）read\(\)：读取全部内容

```python
with open("test.txt", "r", encoding="utf-8") as f:
    content = f.read()  # 读取全部文本
    print(content)
```

注意：超大文件禁止使用，会一次性加载全部内容到内存，造成内存溢出。

### 2）readline\(\)：读取一行内容

```python
with open("test.txt", "r", encoding="utf-8") as f:
    line = f.readline()
    print(line)
```

### 3）readlines\(\)：读取所有行，返回列表

```python
with open("test.txt", "r", encoding="utf-8") as f:
    line_list = f.readlines()
    print(line_list)
```

### 4）逐行循环读取（超大文件最优解）

```python
# 迭代器逐行读取，内存占用极低
with open("test.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())  # strip去除换行空格
```

## 3\.2 写入文件两大方法

### 1）write\(\)：写入字符串，返回写入字符数

```python
with open("test.txt", "w", encoding="utf-8") as f:
    num = f.write("第一行内容\n第二行内容")
    print("写入字符数量：", num)
```

注意：write 不会自动换行，需要手动加 `\n`。

### 2）writelines\(\)：写入可迭代字符串序列

```python
lines = ["Python\n", "文件IO\n", "学习总结"]
with open("test.txt", "w", encoding="utf-8") as f:
    f.writelines(lines)
```

注意：writelines 同样不会自动换行，序列内需要手动添加换行符。

# 四、文件指针（光标）进阶操作

文件所有读写操作都基于**当前指针位置**，指针在哪里，读写就从哪里开始。

## 4\.1 tell\(\)：获取当前指针位置

```python
with open("test.txt", "r", encoding="utf-8") as f:
    print(f.tell())  # 初始指针位置0
    f.read(2)
    print(f.tell())  # 读取2个字符后指针位置
```

中文utf\-8编码：1个中文占3个字节；英文数字占1个字节。

## 4\.2 seek\(\)：移动文件指针

语法：`seek(偏移量, 参考位置)`

- 参考位置 0：文件开头（默认）

- 参考位置 1：当前指针位置（仅二进制模式可用）

- 参考位置 2：文件末尾（仅二进制模式可用）

```python
with open("test.txt", "r", encoding="utf-8") as f:
    f.seek(3, 0)  # 从开头偏移3字节
    print(f.read())
```

## 4\.3 不同模式指针初始位置

- r / r\+：指针在文件开头

- w / w\+：清空文件，指针归位开头

- a / a\+：指针直接在文件末尾

# 五、二进制文件读写（图片/视频/音频）

## 5\.1 核心特点

- 打开模式带 **b**：rb / wb / ab

- **不允许指定encoding**，否则报错

- 读写数据为 bytes 字节类型

- 所有文件本质都是二进制，文本文件也可以用二进制读取

## 5\.2 二进制读写案例（图片拷贝）

```python
# 读取二进制图片
with open("test.jpg", "rb") as f1:
    data = f1.read()

# 写入新图片
with open("new_test.jpg", "wb") as f2:
    f2.write(data)
```

# 六、路径与目录操作（os / pathlib）

## 6\.1 os 模块常用操作

```python
import os

# 判断文件/文件夹是否存在
print(os.path.exists("test.txt"))

# 创建文件夹
os.mkdir("test_dir")

# 重命名文件
os.rename("old.txt", "new.txt")

# 删除文件
os.remove("new.txt")

# 获取当前工作目录
print(os.getcwd())
```

## 6\.2 pathlib 面向对象路径（推荐）

Python3\.4\+ 新特性，语法更简洁，跨平台兼容。

```python
from pathlib import Path

# 创建路径对象
p = Path("test.txt")

# 判断是否存在
print(p.exists())

# 创建文件
p.touch()

# 删除文件
p.unlink()
```

# 七、文件操作异常捕获（工程健壮写法）

## 7\.1 常见文件异常

- **FileNotFoundError**：文件不存在

- **PermissionError**：权限不足

- **UnicodeDecodeError**：编码不匹配乱码

## 7\.2 标准安全模板（with \+ try\-except）

```python
try:
    with open("test.txt", "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    print("文件不存在！")
except UnicodeDecodeError:
    print("文件编码错误！")
except Exception as e:
    print(f"文件读取异常：{e}")
else:
    print("读取成功：", content)
finally:
    print("文件操作结束")
```

# 八、文件流核心注意事项（高频坑点）

- 优先使用 **with** 语句，自动释放资源，杜绝句柄泄露

- 文本文件必须指定 **encoding="utf\-8"**，避免Windows默认GBK乱码

- **w模式会清空原文件**，谨慎使用；追加内容必须用a模式

- 二进制模式禁止写encoding参数，否则直接报错

- 超大文件禁止read\(\)一次性读取，必须逐行遍历，防止内存溢出

- write、writelines 均不会自动换行，需要手动添加 \\n

- a\+模式指针默认在末尾，读取内容需要手动移动seek指针

# 九、整体知识总结

文件IO核心逻辑：区分**文本/二进制**文件、熟练掌握五大打开模式、优先使用with上下文、大文件逐行读取、操作必须捕获异常。所有本地数据持久化、日志处理、文件批量操作、数据导入导出，全部基于文件流实现，是Python自动化、数据分析、后端开发的基础必备能力。

> （注：部分内容可能由 AI 生成）

---
> 🏠 **[返回主页 README](./README.md)** \| ◀️ **上一篇：[03. Python 基础总结](./03Python%E5%9F%BA%E7%A1%80%E6%80%BB%E7%BB%93.md)** \| ▶️ **下一篇：[06. Python 函数篇](./06Python%E5%87%BD%E6%95%B0%E7%AF%87.md)** \| 🎓 **[进入本模块面试高频题](./interview/01_云原生与Python高频面试题.md)**
