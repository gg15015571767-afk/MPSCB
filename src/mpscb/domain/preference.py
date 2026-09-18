"""用户偏好存储抽象。

agent 只调工具、工具只调本接口；换后端对 agent 零改动。
当前实现：SQLite（`SqlPreferenceStore`，与业务同库、带时间戳、可查询）。
"""

from __future__ import annotations

from typing import Protocol

from sqlalchemy import select

from mpscb.domain.models import Preference


class PreferenceStore(Protocol):
    """用户偏好存储接口。"""

    def get(self, user_id: str, key: str) -> str | None: ...

    def set(self, user_id: str, key: str, value: str) -> None: ...

    def get_all(self, user_id: str) -> dict[str, str]: ...


class SqlPreferenceStore:
    """SQLite 实现（SQLAlchemy）。偏好存 `preferences` 表，(user_id, key) 唯一。"""

    def __init__(self, session_factory):
        self._session_factory = session_factory

    def get(self, user_id: str, key: str) -> str | None:
        with self._session_factory() as s:
            p = s.scalar(
                select(Preference).where(Preference.user_id == user_id, Preference.key == key)
            )
            return p.value if p else None

    def set(self, user_id: str, key: str, value: str) -> None:
        with self._session_factory() as s:
            p = s.scalar(
                select(Preference).where(Preference.user_id == user_id, Preference.key == key)
            )
            if p is not None:
                p.value = value  # onupdate 自动刷新 updated_at
            else:
                s.add(Preference(user_id=user_id, key=key, value=value))
            s.commit()

    def get_all(self, user_id: str) -> dict[str, str]:
        with self._session_factory() as s:
            rows = s.scalars(select(Preference).where(Preference.user_id == user_id))
            return {p.key: p.value for p in rows}
