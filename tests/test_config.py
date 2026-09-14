"""nanobot 配置加载校验（对应 agent/config.json）。"""

from __future__ import annotations

from pathlib import Path

from nanobot.config.loader import load_config

CONFIG = Path(__file__).parent.parent / "config.json"


def test_config_loads():
    cfg = load_config(CONFIG)
    assert cfg.agents.defaults.provider == "deepseek"
    assert cfg.agents.defaults.model == "deepseek-v4-pro"
    assert cfg.agents.defaults.workspace == "agent"
    assert cfg.agents.defaults.timezone == "Asia/Shanghai"


def test_ticket_mcp_registered():
    cfg = load_config(CONFIG)
    assert "ticket" in cfg.tools.mcp_servers
    server = cfg.tools.mcp_servers["ticket"]
    assert server.type == "stdio"
    assert server.command == "mpscb-ticket"
    assert server.env.get("MPSCB_DB") == "data/mpscb.db"
