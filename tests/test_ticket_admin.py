"""工单管理（list all / count by status / 状态流转）测试。"""

from __future__ import annotations

from mpscb.domain import ticket as ticket_service


def _seed(session):
    ticket_service.create_ticket(session, title="a", description="d", user_id="u1")
    ticket_service.create_ticket(session, title="b", description="d", user_id="u2")
    t = ticket_service.create_ticket(session, title="c", description="d", user_id="u3")
    ticket_service.update_status(session, t.ticket_no, "waiting_human")


def test_list_all_and_filter(session):
    _seed(session)
    assert len(ticket_service.list_all_tickets(session)) == 3
    waiting = ticket_service.list_all_tickets(session, "waiting_human")
    assert len(waiting) == 1
    assert waiting[0].title == "c"


def test_count_by_status(session):
    _seed(session)
    counts = ticket_service.count_tickets_by_status(session)
    assert counts["pending"] == 2
    assert counts["waiting_human"] == 1


def test_full_flow(session):
    t = ticket_service.create_ticket(session, title="x", description="d", user_id="u1")
    ticket_service.update_status(session, t.ticket_no, "waiting_human")
    ticket_service.update_status(session, t.ticket_no, "processing")
    ticket_service.update_status(session, t.ticket_no, "closed")
    assert ticket_service.get_ticket(session, t.ticket_no).status == "closed"
