# Name: Chetan
# SRN: PES2UG24CS131
# SECTION C
# SE LAB SUBMISSION 14/10/26

"""Manage helpdesk tickets and their assignments."""

import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

tickets = {}
TICKET_COUNTER = 100


def raise_ticket(user, issue_type, urgency="3", audit_trail=None):
    """Create a ticket and record its creation in the audit trail."""
    global TICKET_COUNTER

    try:
        priority = int(urgency)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Urgency must be an integer from 1 to 5."
        ) from exc

    if not 1 <= priority <= 5:
        raise ValueError("Urgency must be between 1 and 5.")

    if audit_trail is None:
        audit_trail = []

    TICKET_COUNTER += 1
    tickets[TICKET_COUNTER] = {
        "user": user,
        "issue": issue_type,
        "priority": priority,
        "tech": None,
        "notes": [],
    }
    audit_trail.append(
        f"{user} raised #{TICKET_COUNTER} at {datetime.now().isoformat()}"
    )
    return TICKET_COUNTER


def assign_ticket(ticket_id, technician):
    """Assign a technician to an existing ticket."""
    if ticket_id not in tickets:
        raise KeyError(f"Ticket {ticket_id} does not exist.")
    tickets[ticket_id]["tech"] = technician


def add_note(ticket_id, note):
    """Add a note to an existing ticket."""
    if ticket_id not in tickets:
        raise KeyError(f"Ticket {ticket_id} does not exist.")
    tickets[ticket_id]["notes"].append(note)


def close_ticket(ticket_id, password):
    """Close a ticket after checking the administrator password."""
    admin_password = os.environ.get("HELPDESK_ADMIN_PASSWORD")
    if not admin_password:
        raise RuntimeError(
            "Set the HELPDESK_ADMIN_PASSWORD environment variable."
        )
    if password != admin_password:
        return False
    if ticket_id not in tickets:
        raise KeyError(f"Ticket {ticket_id} does not exist.")
    del tickets[ticket_id]
    return True


def unresolved_high_priority():
    """Return IDs of unassigned tickets with priority 4 or 5."""
    return [
        ticket_id
        for ticket_id, ticket in tickets.items()
        if ticket["priority"] >= 4 and ticket["tech"] is None
    ]


def ping_user_machine(hostname):
    """Ping a host without invoking a shell."""
    if not hostname or any(char.isspace() for char in hostname):
        raise ValueError("Provide a valid hostname or IP address.")

    ping_path = shutil.which("ping")
    if ping_path is None:
        raise RuntimeError("The ping executable was not found.")

    return subprocess.run(
        [ping_path, "-n", "1", hostname],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    ).returncode


def save_tickets(file="tickets.json"):
    """Save the current tickets as JSON."""
    output_path = Path(file)
    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(tickets, output_file, indent=2)


def main():
    """Demonstrate basic helpdesk ticket operations."""
    global TICKET_COUNTER
    tickets.clear()
    TICKET_COUNTER = 100

    first_ticket = raise_ticket("anil", "printer", "5")
    second_ticket = raise_ticket("meera", "wifi", "4")
    third_ticket = raise_ticket("joe", "vpn", "2")

    assign_ticket(first_ticket, "Tech-Kiran")
    add_note(first_ticket, "Technician assigned.")

    print("Unassigned high priority:", unresolved_high_priority())
    prompt = "Urgency for a new laptop ticket (1-5, Enter for 3): "
    level = input(prompt) or "3"

    try:
        raise_ticket("sana", "laptop", level)
    except ValueError as exc:
        print(f"Ticket not created: {exc}")

    admin_password = os.environ.get("HELPDESK_ADMIN_PASSWORD", "")
    if admin_password:
        close_ticket(third_ticket, admin_password)

    save_tickets()
    print("Open tickets:", sorted(tickets))
    print("Second ticket:", second_ticket)


if __name__ == "__main__":
    main()
