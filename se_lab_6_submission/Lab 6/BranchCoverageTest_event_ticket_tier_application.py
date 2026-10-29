"""Decision-focused tests covering true and false outcomes of branches."""
import pytest
from event_ticket_tier import process_ticket_manifest, monitor_gate_flow


def m(tier="general", confirmed=True, orders=None, lounge=False):
    return {"is_confirmed": confirmed, "tier": tier, "orders": orders or [], "exclusive_lounge": lounge}


@pytest.mark.parametrize("bad_manifests,tax", [("bad", 0), ([], -1)])
def test_invalid_input_branches(bad_manifests, tax):
    with pytest.raises(ValueError):
        process_ticket_manifest(bad_manifests, tax)


def test_confirmation_and_tier_branches():
    assert process_ticket_manifest([m(confirmed=False)], 0)["status"] == "ZERO_SALES"
    assert process_ticket_manifest([m("vip", orders=[{"qty": 1}])], 0)["total_revenue"] == 150
    assert process_ticket_manifest([m("premium", orders=[{"qty": 1}])], 0)["total_revenue"] == 90
    assert process_ticket_manifest([m("general", orders=[{"qty": 1}])], 0)["total_revenue"] == 45.0
    assert process_ticket_manifest([m("invalid")], 0)["status"] == "ZERO_SALES"


def test_quantity_promo_and_tier_dependent_fraud_branches():
    assert process_ticket_manifest([m(orders=[{"qty": 0}, {"qty": -1}])], 0)["status"] == "ZERO_SALES"
    assert process_ticket_manifest([m(orders=[{"qty": 1, "promo": "EARLYBIRD"}])], 0)["total_revenue"] == 36
    assert process_ticket_manifest([m(orders=[{"qty": 5, "promo": ""}])], 0)["total_revenue"] == 205
    assert process_ticket_manifest([m(orders=[{"qty": 1, "promo": "FRAUD_RISK"}, {"qty": 1}])], 0)["total_revenue"] == 90.0
    assert process_ticket_manifest([m("vip", orders=[{"qty": 1, "promo": "FRAUD_RISK"}, {"qty": 1}])], 0)["status"] == "ZERO_SALES"


def test_lounge_audit_zero_sales_and_completed_branches():
    assert process_ticket_manifest([m(orders=[{"qty": 1}], lounge=True)], 0)["total_revenue"] == 120
    assert process_ticket_manifest([m(orders=[{"qty": 0}] * 5)], 0)["status"] == "AUDIT_REJECTED"
    assert process_ticket_manifest([], 0)["status"] == "ZERO_SALES"
    assert process_ticket_manifest([m(orders=[{"qty": 1}])], 0)["status"] == "COMPLETED"


def test_gate_flow_branches_and_streak_reset():
    assert monitor_gate_flow([]) == "NO_DATA"
    assert monitor_gate_flow([[50]]) == "FLOW_NORMAL"
    assert monitor_gate_flow([[51]]) == "FLOW_NORMAL"
    assert monitor_gate_flow([[51, 50, 52, 53]]) == "OVERFLOW"
    assert monitor_gate_flow([[], [51, 51]]) == "OVERFLOW"
    assert monitor_gate_flow([[20, 30], [49]]) == "FLOW_NORMAL"
