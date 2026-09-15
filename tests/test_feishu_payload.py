"""飞书消息事件 payload 解析测试（Mock 外部接口，无需真实飞书）。

验证我们理解的飞书 im.message.receive_v1 事件格式正确，并能把
「消息 content → 内部文本 → FAQ 匹配」串起来。
"""

from __future__ import annotations

import json
from pathlib import Path

from mpscb.domain.faq import match_faq
from mpscb.domain.models import Faq

FIXTURE = Path(__file__).parent / "fixtures" / "feishu_message_event.json"


def _load_event() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_is_p2p_text():
    ev = _load_event()
    assert ev["header"]["event_type"] == "im.message.receive_v1"
    assert ev["event"]["message"]["chat_type"] == "p2p"  # 单聊
    assert ev["event"]["message"]["message_type"] == "text"


def test_extract_ids():
    ev = _load_event()
    sender = ev["event"]["sender"]["sender_id"]["open_id"]
    chat_id = ev["event"]["message"]["chat_id"]
    assert sender.startswith("ou_")  # 用户 open_id
    assert chat_id.startswith("oc_")  # 单聊会话 chat_id


def test_content_to_faq_match(session):
    ev = _load_event()
    # 飞书里 message.content 是 JSON 字符串，需再解析出 text
    text = json.loads(ev["event"]["message"]["content"])["text"]
    assert text == "如何退款"

    session.add(Faq(keywords="退款", question="如何退款", answer="7 天内可退"))
    session.commit()

    got = match_faq(session, text)
    assert got is not None and got.answer == "7 天内可退"
