"""启动飞书客服机器人（gateway + 工具状态注入）。

用法：从项目根目录运行 `python scripts/run_bot.py`（或 `conda activate mpscb` 后运行）。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# 让 mpscb-ticket 等 console script 可被 MCP 子进程找到
os.environ["PATH"] = str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", "")

from mpscb.app import init_runtime


def main() -> None:
    # 1) 加载 .env + 注入工具状态（DB 会话工厂 + 偏好存储）——必须与 agent 同进程
    init_runtime()

    # 1.5) 确保电信问答向量索引存在（RAG，首次约 1-2 分钟）
    from mpscb.domain.review_rag import ensure_qa_index

    if ensure_qa_index("resources/anhuidianxinzhidao_filter.csv", "data/qa_index"):
        print("已构建电信问答索引")

    # 2) 加载并解析 nanobot 配置（含 ${VAR} 环境变量引用）
    from nanobot.config.loader import load_config, resolve_config_env_vars, set_config_path

    resolved = Path("config.json").resolve()
    set_config_path(resolved)  # 关键：让 gateway 内部的 load_provider_snapshot 也用我们的 config
    config = resolve_config_env_vars(load_config(resolved), config_path=resolved)

    # 3) 启动 gateway（飞书 channel + agent loop，同进程，工具状态已就绪）
    from nanobot.cli.gateway_runtime import _run_gateway

    _run_gateway(config)


if __name__ == "__main__":
    main()
