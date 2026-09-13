"""工单服务测试。"""

from __future__ import annotations

import pytest

from mpscb.domain.ticket import create_ticket, get_ticket, list_tickets, update_status


def test_create_ticket_generates_unique_no(session):
    t1 = create_ticket(session, title="a", description="d", user_id="u1")
    t2 = create_ticket(session, title="b", description="d", user_id="u1")
    assert t1.ticket_no != t2.ticket_no
    assert t1.ticket_no.startswith("TK-")
    assert t1.status == "pending"


def test_get_ticket_found_and_missing(session):
    t = create_ticket(session, title="a", description="d", user_id="u1")
    assert get_ticket(session, t.ticket_no).id == t.id
    assert get_ticket(session, "TK-NOPE") is None


def test_update_status(session):
    t = create_ticket(session, title="a", description="d", user_id="u1")
    updated = update_status(session, t.ticket_no, "waiting_human")
    assert updated.status == "waiting_human"
    assert get_ticket(session, t.ticket_no).status == "waiting_human"


def test_update_status_invalid(session):
    t = create_ticket(session, title="a", description="d", user_id="u1")
    with pytest.raises(ValueError):
        update_status(session, t.ticket_no, "bogus")


def test_list_tickets(session):
    create_ticket(session, title="a", description="d", user_id="u1")
    create_ticket(session, title="b", description="d", user_id="u2")
    assert len(list_tickets(session, "u1")) == 1
