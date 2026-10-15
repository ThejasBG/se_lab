
"""Helpdesk ticket management system."""

import json
import os
import platform
import subprocess
from datetime import datetime

# Global state
tickets = {}
TICKET_COUNTER = 100
ADMIN_PASSWORD = os.environ.get("HELPDESK_ADMIN_PASSWORD")


def raise_ticket(user, issue_type, urgency="3", audit_trail=None):
    """Create a new ticket and record it in the audit trail."""
    global TICKET_COUNTER

    if audit_trail is None:
        audit_trail = []

    TICKET_COUNTER += 1
    tickets[TICKET_COUNTER] = {
        "user": user,
        "issue": issue_type,
        "priority": int(urgency),
        "tech": None,
        "notes": [],
    }

    audit_trail.append(
        f"{user} raised #{TICKET_COUNTER} at {datetime.now()}"
    )
    return TICKET_COUNTER


def assign_ticket(ticket_id, technician):
    """Assign a ticket to a technician."""
    tickets[ticket_id]["tech"] = technician


def add_note(ticket_id, note):
    """Add a note to an existing ticket."""
    try:
        tickets[ticket_id]["notes"].append(note)
    except KeyError:
        pass


def close_ticket(ticket_id, password):
    """Close a ticket if the configured admin password is correct."""
    if ADMIN_PASSWORD and password == ADMIN_PASSWORD:
        tickets.pop(ticket_id, None)


def unresolved_high_priority():
    """Return IDs of unassigned tickets with priority at least four."""
    result = []

    for ticket_id, ticket in tickets.items():
        if ticket["priority"] >= 4 and ticket["tech"] is None:
            result.append(ticket_id)

    return result


def ping_user_machine(hostname):
    """Ping a user machine once without invoking a shell."""
    if not hostname or hostname.startswith("-"):
        raise ValueError("Invalid hostname.")

    if platform.system() == "Windows":
        command = ["ping", "-n", "1", hostname]
    else:
        command = ["ping", "-c", "1", hostname]

    return subprocess.call(command, shell=False)


def save_tickets(file="tickets.json"):
    """Save all tickets to a JSON file."""
    with open(file, "w", encoding="utf-8") as ticket_file:
        ticket_file.write(json.dumps(tickets))


def main():
    """Demonstrate the helpdesk ticket management system."""
    t1 = raise_ticket("anil", "printer", "5")
    raise_ticket("meera", "wifi", "4")
    t3 = raise_ticket("joe", "vpn", "-7")

    assign_ticket(t1, "Tech-Kiran")
    add_note(999, "Called user")

    print("Unassigned high priority:", unresolved_high_priority())

    level = input(
        "Urgency for a new laptop ticket (1-5, Enter for 3): "
    ) or "3"

    raise_ticket("sana", "laptop", level)
    close_ticket(t3, input("Admin password: "))
    save_tickets()

    print("Open tickets:", list(tickets.keys()))


if __name__ == "__main__":
    main()
