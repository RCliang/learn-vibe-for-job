# Ch5 Linux 与服务器基础：配套代码

章节：[Ch5 Linux 与服务器基础（Day 22-23）](https://your-name.github.io/learn-vibe-coding/guide/ch5)

## 文件说明

| 文件 | 说明 |
| --- | --- |
| `heartbeat.py` | 交付物脚本：每 5 秒打印心跳；`flush=True` 是「日志实时性」教学点 |

无第三方依赖（纯标准库），服务器上有 Python 即可运行。

## 交付物全流程（在课程指导下完成）

```bash
# 1. 本地：上传脚本到服务器（scp = SSH 版「复制文件」）
scp heartbeat.py root@你的服务器IP:/root/

# 2. 服务器：前台跑，体验 Ctrl+C
python3 /root/heartbeat.py

# 3. 服务器：后台跑 + 日志重定向（生产姿势）
nohup python3 /root/heartbeat.py > /root/heartbeat.log 2>&1 &
tail -f /root/heartbeat.log        # 实时观察；Ctrl+C 只退出查看，服务仍在

# 4. 收尾：找到并停止进程
ps aux | grep heartbeat
kill <PID>
```
