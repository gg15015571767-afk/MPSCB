"""用户偏好存储测试（FilePreferenceStore）。"""

from __future__ import annotations

from mpscb.domain.preference import FilePreferenceStore


def test_set_get(tmp_path):
    store = FilePreferenceStore(tmp_path / "pref.json")
    store.set("u1", "nickname", "小王")
    assert store.get("u1", "nickname") == "小王"
    assert store.get("u1", "missing") is None


def test_get_all(tmp_path):
    store = FilePreferenceStore(tmp_path / "pref.json")
    store.set("u1", "language", "zh")
    store.set("u1", "nickname", "小王")
    assert store.get_all("u1") == {"language": "zh", "nickname": "小王"}


def test_user_isolation(tmp_path):
    store = FilePreferenceStore(tmp_path / "pref.json")
    store.set("u1", "nickname", "A")
    store.set("u2", "nickname", "B")
    assert store.get("u1", "nickname") == "A"
    assert store.get("u2", "nickname") == "B"


def test_persist_across_instances(tmp_path):
    p = tmp_path / "pref.json"
    FilePreferenceStore(p).set("u1", "k", "v")
    # 重新实例化应能读到（落盘验证）
    assert FilePreferenceStore(p).get("u1", "k") == "v"
