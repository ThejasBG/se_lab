"""Functional tests focused on executing every application line."""
import pytest
from event_ticket_tier import process_ticket_manifest, monitor_gate_flow


def manifest(**overrides):
    data = {"is_confirmed": True, "tier": "general", "exclusive_lounge": False,
            "orders": [{"qty": 2, "promo": ""}]}
    data.update(overrides)
    return data


def test_general_order_and_tax():
    assert process_ticket_manifest([manifest()], 0.1) == {"total_revenue": 99.0, "status": "COMPLETED"}


def test_each_valid_tier():
    assert process_ticket_manifest([manifest(tier="vip")], 0)["total_revenue"] == 300.0
    assert process_ticket_manifest([manifest(tier="premium")], 0)["total_revenue"] == 180.0
    assert process_ticket_manifest([manifest(tier="general")], 0)["total_revenue"] == 90.0


def test_unconfirmed_unknown_tier_and_missing_defaults():
    assert process_ticket_manifest([manifest(is_confirmed=False)], 0)["status"] == "ZERO_SALES"
    assert process_ticket_manifest([manifest(tier="student")], 0)["status"] == "ZERO_SALES"
    assert process_ticket_manifest([{"is_confirmed": True}], 0)["total_revenue"] == 0.0


def test_invalid_arguments():
    with pytest.raises(ValueError):
        process_ticket_manifest("not a list", 0)
    with pytest.raises(ValueError):
        process_ticket_manifest([], -0.01)


def test_invalid_quantity_and_zero_sales():
    result = process_ticket_manifest([manifest(orders=[{"qty": 0}, {"qty": -2}])], 0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_promotions_and_bulk_discount():
    orders = [{"qty": 1, "promo": "EARLYBIRD"}, {"qty": 5, "promo": ""}, {"qty": 1, "promo": ""}]
    assert process_ticket_manifest([manifest(orders=orders)], 0)["total_revenue"] == 36 + 205 + 45


def test_fraud_risk_non_vip_and_vip():
    non_vip = process_ticket_manifest([manifest(orders=[{"qty": 2, "promo": "FRAUD_RISK"}])], 0)
    assert non_vip["total_revenue"] == 90.0
    vip = process_ticket_manifest([manifest(tier="vip", orders=[{"qty": 2, "promo": "FRAUD_RISK"}])], 0)
    assert vip == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_lounge_and_audit_rejection():
    assert process_ticket_manifest([manifest(exclusive_lounge=True)], 0)["total_revenue"] == 165.0
    many_bad = manifest(orders=[{"qty": 0}] * 5)
    assert process_ticket_manifest([many_bad], 0)["status"] == "AUDIT_REJECTED"


def test_gate_flow_all_outcomes():
    assert monitor_gate_flow([]) == "NO_DATA"
    assert monitor_gate_flow([[51]]) == "FLOW_NORMAL"
    assert monitor_gate_flow([[51, 50, 51]]) == "FLOW_NORMAL"
    assert monitor_gate_flow([[51, 52]]) == "OVERFLOW"
    assert monitor_gate_flow([[], [50, 40]]) == "FLOW_NORMAL"
