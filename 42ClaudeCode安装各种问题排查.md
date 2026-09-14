> 📌 **[AI 大模型与云原生全栈知识库](./README.md)** / **42. Claude Code 安装全流程与终端代理网络排查避坑指南**
> 🏠 [返回主页 README](./README.md) | ⚡ [面试 30 分钟速记](./interview/00_面试冲刺30分钟速记卡片.md) | 💻 [白板手写代码](./interview/08_大厂手写代码与白板编程题.md)

---

## 1、ClaudeCode安装过程一定得翻墙

## 2、ClaudeCode使用PowerShell配置临时代理

（powershell 管理员模式）安装ClaudeCode的通用命令

```python
irm https://claude.ai/install.ps1 | iex
```

就算你翻了墙也不一定能安装成功，这个是因为**不是VPN（Clash）本身的问题，而是你的PowerShell终端没有走代理！**
Clash虽然开启了“系统代理”，但这对PowerShell无效。你需要手动为PowerShell会话配置代理环境变量。

```python
$env:HTTP_PROXY="http://127.0.0.1:<你的代理端口>"
$env:HTTPS_PROXY="http://127.0.0.1:<你的代理端口>"
```

## 3、解决安装后的常见问题

### 1）PowerShell执行策略限制

如果安装后执行 `claude`命令，收到类似 `...因为在此系统上禁止运行脚本...`的错误，这是因为PowerShell的安全策略限制了脚本运行

以普通用户身份打开PowerShell，输入以下命令即可解决：

```python
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2）找不到 `claude`命令

这通常是环境变量 `PATH`未及时更新导致。最简单的解决方法是 **关闭当前PowerShell窗口，重新打开一个新窗口**

如果还是不行，可以手动添加：

1. 按 `Win + R`，输入 `sysdm.cpl` 并回车。
2. 进入“高级”选项卡，点击“环境变量”。
3. 在“用户变量”中找到 `Path`，编辑并新建一个条目，填入 `C:\Users\你的用户名\.local\bin`（注意替换 `你的用户名`），然后保存并重启终端。

## 4、Trae中使用ClaudeCode的问题

---

> 📌 **[AI 大模型与云原生全栈知识库](./README.md)** / **42. Claude Code 安装全流程与终端代理网络排查避坑指南**
> 🏠 [返回主页 README](./README.md) | ⚡ [面试 30 分钟速记](./interview/00_面试冲刺30分钟速记卡片.md) | 💻 [白板手写代码](./interview/08_大厂手写代码与白板编程题.md)
