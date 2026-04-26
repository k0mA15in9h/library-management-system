from datetime import datetime
from .storage import get_data, save_data

FINE_PER_DAY = 1.0  # $1 per day

def calculate_fine(due_date_str: str, return_date_str: str) -> float:
    """Calculate fine for an overdue book based on strings formatted as YYYY-MM-DD."""
    fmt = "%Y-%m-%d"
    due_date = datetime.strptime(due_date_str, fmt)
    return_date = datetime.strptime(return_date_str, fmt)
    
    delta = return_date - due_date
    if delta.days > 0:
        return delta.days * FINE_PER_DAY
    return 0.0

def add_fine_to_member(member_id: str, amount: float):
    """Add a fine amount to a member's total due fine."""
    if amount <= 0:
        return

    members = get_data("members")
    for m in members:
        if m["member_id"] == member_id:
            m["fines_due"] += amount
            save_data("members", members)
            break

def pay_fine(member_id: str, amount: float):
    """Allow a member to pay off part or all of their fine."""
    members = get_data("members")
    for m in members:
        if m["member_id"] == member_id:
            if m["fines_due"] == 0:
                return f"Member {member_id} has no pending fines."
            
            if amount > m["fines_due"]:
                amount = m["fines_due"]  # Can't pay more than what's due
                
            m["fines_due"] -= amount
            save_data("members", members)
            return f"Successfully paid ${amount:.2f}. Remaining fine: ${m['fines_due']:.2f}"
            
    return f"Member {member_id} not found."
