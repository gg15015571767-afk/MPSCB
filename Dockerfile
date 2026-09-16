# 构建上下文 = 父目录 NanobotProject（docker compose 里 context: ..）
# 因为依赖本地 ../nanobot（领先 PyPI 0.3.0），需 COPY 源码安装
FROM docker.m.daocloud.io/library/python:3.11-slim

WORKDIR /app

# 拷贝并安装 nanobot 框架（本地版本，与开发环境一致）
# NANOBOT_SKIP_WEBUI_BUILD=1 跳过 WebUI 打包（机器人无需 WebUI）
COPY nanobot /app/nanobot
RUN NANOBOT_SKIP_WEBUI_BUILD=1 pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple /app/nanobot

# 拷贝并安装本项目（注册 mpscb-ticket + nanobot.tools 入口）
COPY MPSCB /app/mpscb
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple /app/mpscb

# RAG 依赖（sentence-transformers + torch，较大）
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple "sentence-transformers>=3.0"

WORKDIR /app/mpscb

# 数据目录（SQLite 卷挂载点）
VOLUME /app/mpscb/data

# 启动机器人（飞书 + 钉钉长连接）
CMD ["python", "scripts/run_bot.py"]
