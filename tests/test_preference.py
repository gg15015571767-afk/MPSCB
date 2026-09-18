"""用户偏好存储测试（SqlPreferenceStore，SQLite）。"""

from __future__ import annotations

from mpscb.domain.preference import SqlPreferenceStore


def test_set_get(session_factory):
    store = SqlPreferenceStore(session_factory)
    store.set("u1", "nickname", "小王")
    assert store.get("u1", "nickname") == "小王"
    assert store.get("u1", "missing") is None


def test_upsert(session_factory):
    store = SqlPreferenceStore(session_factory)
    store.set("u1", "language", "zh")
    store.set("u1", "language", "en")  # 覆盖旧值
    assert store.get("u1", "language") == "en"


def test_get_all(session_factory):
    store = SqlPreferenceStore(session_factory)
    store.set("u1", "language", "zh")
    store.set("u1", "nickname", "小王")
    assert store.get_all("u1") == {"language": "zh", "nickname": "小王"}


def test_user_isolation(session_factory):
    store = SqlPreferenceStore(session_factory)
    store.set("u1", "nickname", "A")
    store.set("u2", "nickname", "B")
    assert store.get("u1", "nickname") == "A"
    assert store.get("u2", "nickname") == "B"
