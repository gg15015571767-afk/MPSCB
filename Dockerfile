FROM python:3.11-slim

WORKDIR /app

# 先装 nanobot 框架（PyPI 稳定版，与本地 0.3.0 一致）
RUN pip install --no-cache-dir nanobot-ai==0.3.0

# 拷贝项目代码（.env/data/sessions 等已由 .dockerignore 排除）
COPY . .

# 安装本项目（注册 mpscb-ticket 脚本 + nanobot.tools 工具入口）
RUN pip install --no-cache-dir .

# 数据目录（SQLite 卷挂载点）
VOLUME /app/data

# 启动机器人（飞书 + 钉钉长连接，配置经 env 注入）
CMD ["python", "scripts/run_bot.py"]
