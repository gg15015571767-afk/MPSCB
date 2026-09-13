"""用户偏好存储抽象（对应 技术文档 §11.9：File → Redis 可切换）。

agent 只调工具、工具只调本接口；换后端对 agent 零改动。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol


class PreferenceStore(Protocol):
    """用户偏好存储接口。V1.0 用文件，V1.2 可换 Redis。"""

    def get(self, user_id: str, key: str) -> str | None: ...

    def set(self, user_id: str, key: str, value: str) -> None: ...

    def get_all(self, user_id: str) -> dict[str, str]: ...


class FilePreferenceStore:
    """JSON 文件实现，零外部依赖。"""

    def __init__(self, path: str | Path):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, dict[str, str]] = {}
        if self._path.exists():
            self._data = json.loads(self._path.read_text(encoding="utf-8"))

    def _flush(self) -> None:
        self._path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def get(self, user_id: str, key: str) -> str | None:
        return self._data.get(user_id, {}).get(key)

    def set(self, user_id: str, key: str, value: str) -> None:
        self._data.setdefault(user_id, {})[key] = value
        self._flush()

    def get_all(self, user_id: str) -> dict[str, str]:
        return dict(self._data.get(user_id, {}))
