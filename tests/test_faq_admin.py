"""FAQ 知识库管理（增删查 + 批量导入）测试。"""

from __future__ import annotations

from mpscb.domain import faq as faq_service


def test_add_and_list(session):
    f = faq_service.add_faq(
        session, question="如何退款", answer="7 天内可退", keywords="退款", category="售后"
    )
    assert f.id is not None
    faqs = faq_service.list_faqs(session)
    assert len(faqs) == 1
    assert faqs[0].question == "如何退款"


def test_delete_existing_and_missing(session):
    f = faq_service.add_faq(session, question="a", answer="b")
    assert faq_service.delete_faq(session, f.id) is True
    assert faq_service.list_faqs(session) == []
    assert faq_service.delete_faq(session, f.id) is False  # 已删除


def test_import_faqs(session):
    n = faq_service.import_faqs(
        session,
        [
            {"question": "如何退款", "answer": "7 天内可退", "keywords": "退款", "category": "售后"},
            {"question": "多久发货", "answer": "24 小时内", "keywords": "发货"},
        ],
    )
    assert n == 2
    faqs = faq_service.list_faqs(session)
    assert len(faqs) == 2
    assert faqs[1].keywords == "发货"
    assert faqs[1].category is None  # 未提供 category 时应为 None
