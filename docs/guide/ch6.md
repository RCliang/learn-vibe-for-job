---
title: Ch6 Docker 容器化（Day 24-25）
outline: [2, 3]
---

# Ch6 Docker 容器化（Day 24-25）

> **本章 JD 关键词**：Docker、容器化部署
>
> **学完你能做什么**：讲清镜像与容器的分层原理（面试必问）；解释 Dockerfile 指令顺序背后的层缓存机制；用 `docker exec` 进入容器内部排错；用 docker compose 把长命令变成可版本管理的编排文件；把项目 2 完整容器化（本章交付物）。

::: info 📋 本章路线
**Day 24**：镜像与容器原理、命令体系、层缓存 · **Day 25**：docker compose + 项目 2 容器化交付
:::

**你已经会用但还不懂的三件事**：Day 14 你 build 过、run 过、看过 logs——本章回答三个当时略过的问题：镜像和容器到底是什么？为什么改一行代码重新 build 秒级完成？服务多了命令记不住怎么办？

练习环境：本地有 Docker Desktop 就本地练；没有也无妨——**你的云服务器上 Day 14 装过 Docker**，SSH 进去练一模一样。

---

## 1. 镜像与容器：分层蛋糕（Day 24 上午）

### 1.1 从「菜谱」比喻升级到准确版

Day 14 说镜像像菜谱、容器像菜——入门够用，但面试官会追问细节。准确的心智模型是**分层**：

```
镜像（image）＝ 一叠只读层
┌─────────────────────────────┐
│ 层4: COPY app.py ...         │ ← 你的 Dockerfile 每条指令一层
│ 层3: RUN pip install ...     │
│ 层2: WORKDIR /app            │
│ 层1: python:3.12-slim 基础镜像│ ← 别人做好的地基
└─────────────────────────────┘
容器（container）＝ 镜像 + 顶上再盖一层可读写的「薄层」
```

三个推论（面试常考）：

1. **同一镜像可以同时跑多个容器**——它们共享只读层，各盖各的读写层
2. **容器删除，读写层里的数据就没了**——要持久化的数据必须放 **volume**（挂载到宿主机目录），概念先记住，Ch7 之后你会用到
3. `docker run` 发生了什么：本地找镜像 → 没有就去仓库拉（pull）→ 叠读写层建容器 → 隔离环境中启动进程

### 1.2 命令体系（照着项目 2 的容器练一遍）

```bash
docker images                     # 本地有哪些镜像
docker ps                         # 运行中的容器（-a 含已停止的）
docker logs -f agent-app          # 跟踪日志（Ch5 tail -f 的容器版）
docker exec -it agent-app bash    # 「走进容器」——里面是一个迷你 Linux
docker stop agent-app && docker rm agent-app    # 停止并删除容器（镜像还在）
docker rmi agent-app:latest       # 删除镜像
docker system df                  # 磁盘占用（镜像/容器/缓存各占多少）
```

**必做实验**：把项目 2 跑起来（5.1 有完整命令），然后 `docker exec -it agent-app bash` 进去，`ls /app` 看到你的代码、`cat requirements.txt`、`exit` 出来——「容器里就是一个隔离的小电脑」这件事，进去一次就永远懂了。

## 2. 层缓存：Dockerfile 的顺序是艺术（Day 24 下午）

### 2.1 缓存规则（一条就够）

> 构建镜像时逐层比对：**指令（和它影响的文件）没变 → 直接复用缓存层；任何一层变了 → 该层及其后所有层全部重建**。

这就是 Day 14 那句「先 COPY requirements.txt 再装依赖」的完整原理：

```dockerfile
COPY requirements.txt .                          # 层3：依赖清单很少变
RUN pip install -r requirements.txt              # 层4：跟着层3复用缓存 → 秒过
COPY app.py agent_core.py ./                     # 层5：改代码只重建这层及以后
```

改一行 `server.py` 重新 build：层 1-4 全部命中缓存，只重建层 5——**秒级完成**。反之把 `COPY . .` 放最前面：改任何代码，pip install 那层也作废，每次 build 都重装依赖。

**实验（在项目 2 上做，各 build 两次）**：

1. 改 `server.py` 里一行注释 → `docker compose build` → 观察输出里 `CACHED` 字样和总耗时
2. 在 `requirements.txt` 加一个包 → 再 build → 观察 pip 层重新执行、耗时变长
3. `docker history agent-app:latest` → 亲眼看镜像的层列表（每层多大、哪条指令建的）

### 2.2 镜像瘦身三招（面试谈资）

你已经用了前两招（Dockerfile 注释里埋过）：① `python:3.12-slim` 小基础镜像（不用完整版 debian）；② `pip install --no-cache-dir` 不留 pip 缓存。第三招**多阶段构建**（构建工具用完即弃、只拷产物进最终镜像）是进阶概念，见完整路径。

## 3. docker compose：把 docker run 写成代码（Day 25 上午）

回想 Day 14 那条命令：`docker run -d --name kb-bot -p 8501:8501 --env-file .env kb-bot`——参数越来越多、没人记得住、更没法版本管理。compose 的答案：**把所有参数写进 YAML**（项目 2 的 [`docker-compose.yml`](https://github.com/RCliang/learn-vibe-for-job/tree/main/code/project2-agent)）：

```yaml
services:
  agent-app:
    build: .                  # 用当前目录 Dockerfile 构建
    image: agent-app:latest
    ports:
      - "8000:8000"
    env_file:
      - .env                  # 密钥运行时注入
    restart: always           # ← Day 14 完整路径卖的那个关子：崩溃/重启自动拉起
```

五个命令走天下：

```bash
docker compose up -d --build   # 构建 + 后台启动全部服务
docker compose ps              # 状态
docker compose logs -f         # 日志
docker compose up -d --build   # 改代码后重建更新（compose 会智能替换容器）
docker compose down            # 停止并清理
```

**为什么面试爱问 compose**：真实项目是「应用 + 数据库 + 缓存」多容器组合，compose 一个文件管全家；你现在是单服务，但心智模型已经就位，见到多服务时只需往 `services:` 下再加一段。

## 4. 交付物：项目 2 容器化（Day 25 下午）

**目标**：项目 2 以「一条 compose 命令」的方式在本地（或服务器）起停。

```bash
cd code/project2-agent
mkdir data && cp ../../data/project2-orders.json data/   # 语料进项目目录
cp .env.example .env && nano .env                        # 填 GLM_API_KEY

docker compose up -d --build
docker compose ps                       # STATUS: Up
docker compose logs -f | grep -i uvicorn   # 看到 "Uvicorn running on 0.0.0.0:8000"
curl http://127.0.0.1:8000/api/health   # {"status":"ok"}
```

浏览器打开 `http://127.0.0.1:8000`，聊一句「我（张小明）有哪些订单」确认功能正常——**前后端+Agent 全部跑在一个容器里**。

**验收四连**（截图进错题本）：

- [ ] `docker compose ps` 显示 Up；`curl /api/health` 返回 ok
- [ ] `docker exec` 进容器，`ls /app` 能看到 server.py 与 frontend/
- [ ] `docker compose down` 后端口不可访问；`up -d` 恢复
- [ ] 重启实验：`docker restart agent-app` 后 `restart: always` 语义不变、服务自动回来

这套 compose 文件就是 Ch7 上云的全部家当——服务器上 `git pull` + `docker compose up -d --build`，项目 2 就上线了。

## 5. 自测门槛

进入 Ch7 前确认你能：

- [ ] 用「分层蛋糕」向 AI 出题考核的方式讲清：镜像 vs 容器、容器删了读写层数据去哪了
- [ ] 说出层缓存的失效规则，解释 Dockerfile 为什么依赖清单先拷
- [ ] 不看笔记完成 compose 五连：up / ps / logs / 重建 / down
- [ ] `docker exec` 进容器查看文件；`docker history` 看层
- [ ] 交付物四连验收全过

## 6. 最小路径 vs 完整路径

- **最小路径（必做）**：第 1-4 节 + 自测门槛
- **完整路径（选做）**：
  - 给项目 1（Streamlit 版）也写一个 `docker-compose.yml`
  - 多阶段构建：给一个「builder 阶段编译、最终阶段只带产物」的最小示例跑通
  - volume 实践：把项目 2 的会话记忆写到挂载目录，`down` 后数据还在
  - `docker system prune` 清理实验（先 `system df` 看能省多少）
  - 概念阅读：镜像仓库与推送（阿里云容器镜像服务），Ch7 部署的另一条路

## 7. 排错指引

| 现象 | 原因 | 解法 |
| --- | --- | --- |
| 每次改代码 build 都很慢 | 层缓存失效 | 核对指令顺序：`COPY 代码` 是否排在了 `pip install` 之前 |
| `docker compose` 报命令不存在 | 老版独立 docker-compose / 未装 | 服务器用 Day 14 脚本装的 Docker 自带 compose 子命令；确认写法是 `docker compose`（空格）不是 `docker-compose`（横杠） |
| up 后端口访问不通 | 端口没映射 / 监听 127.0.0.1 / 安全组 | 核对 compose `ports`；uvicorn 必须 `--host 0.0.0.0`（项目 2 的 Dockerfile 已配） |
| `port is already allocated` | 端口被占 | `docker compose down`；或换宿主机端口如 `"8001:8000"` |
| 容器名冲突 `already in use` | 旧容器没清 | `docker rm -f agent-app` 或 `docker compose down` |
| 磁盘越用越满 | 旧镜像/停掉的容器/构建缓存堆积 | `docker system df` 看占用，`docker system prune` 清理 |
| exec 进去没有 bash | slim 镜像精简了 shell | 用 `docker exec -it agent-app sh` |
| 构建时网络拉依赖超时 | 默认源在国外 | 项目 2 的 Dockerfile 已配清华源；确认用的不是自己乱改的版本 |
