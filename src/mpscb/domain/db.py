"""数据库引擎与会话工厂。"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from mpscb.domain.models import Base


def create_engine_for_db(path: str | Path) -> Engine:
    """创建 SQLite 引擎并建表（幂等）。"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{p}", echo=False)
    Base.metadata.create_all(engine)
    return engine


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
