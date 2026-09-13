"""工具运行时依赖的单例（由应用入口注入，见模块 5/6）。"""

from __future__ import annotations

_session_factory = None
_preference_store = None


def init(*, session_factory, preference_store) -> None:
    """注入 DB 会话工厂与偏好存储（工具执行前必须调用）。"""
    global _session_factory, _preference_store
    _session_factory = session_factory
    _preference_store = preference_store


def get_session_factory():
    return _session_factory


def get_preference_store():
    return _preference_store
