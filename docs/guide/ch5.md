---
title: Ch5 Linux 与服务器基础（Day 22-23）
outline: [2, 3]
---

# Ch5 Linux 与服务器基础（Day 22-23）

> **本章 JD 关键词**：熟悉 Linux 环境
>
> **学完你能做什么**：SSH 密钥免密登录；用命令行完成文件操作、搜索、查看日志；管理后台进程（启动/查找/停止）；理解环境变量与 PATH；把「查日志排错」变成肌肉记忆——这是运维自己应用时的第一生存技能。

::: info 📋 本章路线
**Day 22**：SSH 免密、目录与文件命令、权限、文本编辑 · **Day 23**：进程、日志与重定向、环境变量 + 交付物
:::

**学习方法（重要）**：命令是肌肉记忆不是背诵，**全程在你 Day 14 买的云服务器上练**。另外你有个免费陪练——**Ch0 装的 Git Bash 本身就是一个 Linux 命令环境**，`ls`、`cd`、`grep` 在本地随时能敲。

---

## 1. 为什么 AI 应用工程师必须会 Linux

你的应用最终跑在 Linux 服务器上（云服务器几乎清一色 Linux）。线上出问题时没有「点开文件夹看看」这回事——**SSH 进黑窗口，看日志、找进程、查环境变量**，就是你的全部操作界面。JD 里「熟悉 Linux 环境」筛掉的正是只会图形界面的人。

你在 Day 14 已经照做用过 `ssh`、`docker` 三条命令——本章把这件事从「照做」变成「自己的」。

## 2. Day 22：文件与目录——先熟悉地形

### 2.1 SSH 再深入：从密码到免密

密码登录每次都要输，而且不够安全。标准做法是**密钥对**（你的 Day 14 服务器还在的话直接用它练）：

```bash
# 本地（Git Bash / PowerShell 都自带 OpenSSH）生成密钥对：私钥留本地，公钥给服务器
ssh-keygen -t ed25519            # 一路回车；生成在 ~/.ssh/id_ed25519（私钥）+ .pub（公钥）

# 把公钥内容追加到服务器的授权文件（首次仍需密码）
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh root@服务器IP "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
# （Git Bash 写法：cat ~/.ssh/id_ed25519.pub | ssh root@服务器IP "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"）

ssh root@服务器IP               # 再连：不用密码了
```

原理一句话：**服务器用你提供的公钥验证你手里的私钥**——密码可被猜，私钥文件猜不了。

### 2.2 目录树与路径

Linux 只有一棵树，从根 `/` 开始（Windows 的 C:\、D:\ 在这里不存在）：

```
/            根目录（万物之源）
├── home/    普通用户的家
├── root/    root 用户的家（你 ssh root@ 登陆后默认就在这，~ 就是它）
├── etc/     配置文件（环境变量、nginx 配置常在这）
├── var/log/ 系统与服务日志（排错金矿）
└── tmp/     临时文件
```

`pwd` 看当前位置；绝对路径从 `/` 写起，相对路径从当前位置写起；`.` 是当前目录、`..` 是上级、`~` 是家。

### 2.3 文件操作命令组（今天练熟这一张表）

| 命令 | 作用 | 高频参数 |
| --- | --- | --- |
| `ls` | 列目录 | `-l` 详细（权限/大小/时间）、`-a` 含隐藏、`-lh` 人类可读大小 |
| `cd` / `pwd` | 切换 / 显示当前目录 | `cd ..`、`cd ~` |
| `cp a b` / `mv a b` | 复制 / 移动（mv 兼改名） | `-r` 递归（目录必须加） |
| `mkdir -p a/b/c` | 建目录（一路建到底） | |
| `rm` | 删除 | `-r` 递归 `-f` 不询问 |
| `cat` / `head` / `tail` | 看文件全部 / 前 N 行 / 后 N 行 | `tail -f` **实时跟踪**（明天主角） |
| `nano 文件` | 编辑文件 | `Ctrl+O` 保存 `Ctrl+X` 退出 |

::: danger rm -rf 血泪警告
`rm -rf 目录` 递归强删、不进回收站、无确认。**执行前把命令读三遍**；拿不准就先 `ls` 一遍要删的路径。江湖名言：rm -rf 手起刀落，删库跑路从此始。
:::

::: tip vi 逃生术
服务器上有些环境只有 vi。你不需要会它，但必须会逃出来：按 `Esc`，输 `:q!` 回车（不保存强退）。会这一条就不会被关在里面。
:::

### 2.4 查找与搜索：find / grep

```bash
find / -name "heartbeat.py" 2>/dev/null   # 全盘找文件（2>/dev/null：把「没权限」的报错丢掉，明天讲）
grep -rn "LLM_API_KEY" /root               # 在目录里递归搜文本：哪个文件、第几行、内容
```

`grep` 是排错时「在几十个配置文件里找那一行」的利器——配合 Ch1 的报错搜索思维用。

### 2.5 权限与 sudo：能读懂即可

`ls -l` 每行开头的 `-rw-r--r--` 分三组：**属主 / 属组 / 其他人**，各三位 `r`读 `w`写 `x`执行。

你只需要两件事：看懂「谁能不能执行」；知道 `sudo` 是「以管理员身份运行」——apt 装软件、改 /etc 配置都要它。`Permission denied` 十有八九是权限或路径问题。

## 3. Day 23：进程、日志与环境变量

### 3.1 进程管理：谁在跑、怎么停

```bash
ps aux | grep python        # 找进程：ps 列出全部，grep 过滤——这就是「管道」
kill 12345                  # 礼貌停止 PID 12345
kill -9 12345               # 强制停止（礼貌没用时）
```

**管道 `|` 是 Linux 的灵魂哲学**：前一个命令的输出，作为后一个命令的输入。`ps aux | grep python`、`cat app.log | grep ERROR | tail -20`——小组件拼出大能力，和 Unix 设计哲学一脉相承（面试聊到 Linux 可以提这句）。

### 3.2 后台运行与日志重定向（交付物核心技能）

| 写法 | 含义 |
| --- | --- |
| `python app.py &` | 放后台跑（但 SSH 断开它就死） |
| `nohup python app.py &` | 后台跑且**不受 SSH 断开影响**（no hang up） |
| `> app.log` | 输出写入文件（覆盖） |
| `>> app.log` | 追加写入 |
| `2>&1` | 把报错也并进同一个文件 |
| `/dev/null` | 「黑洞」，丢弃输出 |

生产组合拳（记这一条顶六条）：

```bash
nohup python3 app.py > app.log 2>&1 &
```

排错三板斧：`tail -f app.log`（实时看）→ `grep ERROR app.log`（找报错）→ `ps aux | grep app`（确认还活着）。Docker 用户：`docker logs -f 容器名` 是同一件事的容器版（Day 14 用过）。

### 3.3 环境变量：命令为什么「找不到」

- `echo $PATH` 打印 PATH——它是**命令的搜索路径清单**：你敲 `python3`，系统挨个在清单里的目录找可执行文件
- `command not found` 的真相：要么没装，要么装了但**不在 PATH 里**（Ch0「pip 不是内部命令」的 Linux 版）
- `export LLM_API_KEY=xxx` 本次会话生效；写进 `~/.bashrc` 再 `source ~/.bashrc` 才持久——**Ch0 里 Claude Code 配置要重开终端生效，底层就是这个机制**

### 3.4 交付物：心跳脚本上云（三段玩法）

脚本在 [code/ch5-linux/heartbeat.py](https://github.com/RCliang/learn-vibe-for-job/tree/main/code/ch5-linux)：每 5 秒打印一行心跳。先读懂它，注意 `flush=True` 的注释——**不加 flush，Python 会攒着缓冲再写盘，`tail -f` 迟迟看不到新行**，这是「日志不实时」的头号元凶，也是本周你会在自己项目里遇到的坑。

```bash
# 本地：上传（scp = SSH 版复制文件）
scp heartbeat.py root@你的服务器IP:/root/

# ── 玩法①：前台跑 ──
ssh root@你的服务器IP
python3 /root/heartbeat.py          # 看 3 行心跳，Ctrl+C 停止

# ── 玩法②：后台跑 + 日志（生产姿势）──
nohup python3 /root/heartbeat.py > /root/heartbeat.log 2>&1 &
tail -f /root/heartbeat.log         # 实时滚动；Ctrl+C 只是退出查看，服务还在跑
logout                              # 断开 SSH
ssh root@你的服务器IP && tail /root/heartbeat.log   # 重连后日志仍在增长——nohup 的意义

# ── 玩法③：找到并停止 ──
ps aux | grep heartbeat             # 拿到 PID（第二列）
kill <PID>
ps aux | grep heartbeat             # 确认没了
```

三段玩法治好「服务怎么跑、日志怎么看、进程怎么停」——**截图保存**（tail -f 滚动那张最值得晒）。

## 4. 自测门槛

进入 Ch6 前确认你能（在服务器上盲操作，不查笔记）：

- [ ] `ssh` 免密登录已配好，能解释公钥私钥各在哪一侧
- [ ] 不看表格完成：新建目录 → 复制文件进去 → 改名 → cat 查看 → 删除
- [ ] 一条命令在 /root 下搜出所有包含 `LLM_API_KEY` 的文件及行号
- [ ] 默写生产组合拳 `nohup ... > log 2>&1 &` 并解释每个符号
- [ ] 完成交付物三段玩法；解释 `flush=True` 不加会怎样
- [ ] 遇到 `command not found` 说出两种原因

## 5. 最小路径 vs 完整路径

- **最小路径（必做）**：第 1-4 节 + 交付物
- **完整路径（选做）**：
  - `tmux`：SSH 断开后回话还在（nohup 的更优雅替代，服务器必备神器）
  - `crontab`：让心跳脚本每天定时跑（`crontab -e` 一行搞定）
  - `du -sh *` / `df -h`：查磁盘占用（日志把盘写满是经典线上事故）
  - 把项目 2 的 `uvicorn` 用 nohup 跑在服务器 8000 端口（Ch7 的热身）

## 6. 排错指引

| 现象 | 原因 | 解法 |
| --- | --- | --- |
| SSH 超时（timeout） | 安全组没放行 22 / 服务器没开机 | 控制台查安全组规则和实例状态 |
| SSH 拒绝密码 | 密码错 / 实例重置密码后没重启 | 控制台重置密码后**重启实例** |
| 免密失败还问密码 | 公钥没进 authorized_keys / 权限不对 | `chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys` |
| `command not found` | 没装 / 不在 PATH | 重装；`which 命令` 看它到底在不在；查 `$PATH` |
| `Permission denied` | 权限不足 / 文件不可执行 | 加 `sudo`；`ls -l` 看权限位 |
| `tail -f` 迟迟不刷新 | Python 输出缓冲 | 脚本 `print(..., flush=True)`（交付物已埋此坑讲解） |
| nohup 跑了但 kill 不掉 | PID 拿错了（grep 把自己也列出来了） | 看第二列 PID；或 `kill -9` |
| 误删了文件 | rm -rf 手滑 | 无解，预防为主：删前 `ls`，重要数据定期备份 |
