"""Ch5 交付物：心跳脚本——上传云服务器运行，练熟进程与日志管理。

每 5 秒打印一次心跳（时间戳 + 计数），配套三段玩法：
  ① 前台运行 + 另一窗口 tail -f 看日志滚动
  ② nohup 后台运行 + 输出重定向到日志文件
  ③ ps 找到进程 + kill 收尾
"""

import time
from datetime import datetime

print("心跳服务启动（Ctrl+C 停止）", flush=True)

count = 0
try:
    while True:
        count += 1
        # flush=True 是本章的关键坑：不加的话 Python 会攒一块缓冲再写，
        # tail -f 要等很久才能看到新行——「日志不实时」的常见元凶
        print(f"[{datetime.now():%H:%M:%S}] heartbeat #{count} - 服务正常", flush=True)
        time.sleep(5)
except KeyboardInterrupt:
    print("收到 Ctrl+C，心跳服务退出", flush=True)
