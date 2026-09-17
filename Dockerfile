FROM docker.m.daocloud.io/library/python:3.11-slim

WORKDIR /app

# 拷贝并安装本项目（依赖含 nanobot-ai==0.3.0、sqlalchemy；注册 mpscb-ticket + nanobot.tools 入口）
COPY . .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple .

# RAG 依赖（sentence-transformers + torch，较大）
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple "sentence-transformers>=3.0"

# 数据目录（SQLite 卷挂载点）
VOLUME /app/data

# 启动机器人（飞书 + 钉钉长连接）
CMD ["python", "scripts/run_bot.py"]
