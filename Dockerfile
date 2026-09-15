FROM docker.m.daocloud.io/library/python:3.11-slim

WORKDIR /app

# 拷贝项目代码（.env/data/sessions 等已由 .dockerignore 排除）
COPY . .

# 安装本项目（依赖含 nanobot-ai==0.3.0、sqlalchemy；注册 mpscb-ticket + nanobot.tools 入口）
# 用清华 PyPI 镜像（国内网络）
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple .

# 数据目录（SQLite 卷挂载点）
VOLUME /app/data

# 启动机器人（飞书 + 钉钉长连接，配置经 env 注入）
CMD ["python", "scripts/run_bot.py"]
