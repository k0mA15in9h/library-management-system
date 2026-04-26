import uuid
from datetime import datetime, timedelta
from .storage import get_data, save_data
from .books import update_book_availability, get_book_by_isbn, get_member
from .fine import calculate_fine, add_fine_to_member

def issue_book(isbn: str, member_id: str, days_to_due: int = 14):
    """Issue a book to a member."""
    # Validate book
    book = get_book_by_isbn(isbn)
    if not book:
        return f"Book with ISBN '{isbn}' not found."
    if book["copies_available"] <= 0:
        return f"No copies of '{book['title']}' available."
        
    # Validate member
    member = get_member(member_id)
    if not member:
        return f"Member with ID '{member_id}' not found."
        
    # Create transaction
    issue_date = datetime.now()
    due_date = issue_date + timedelta(days=days_to_due)
    
    transaction = {
        "transaction_id": str(uuid.uuid4())[:8],
        "isbn": isbn,
        "member_id": member_id,
        "issue_date": issue_date.strftime("%Y-%m-%d"),
        "due_date": due_date.strftime("%Y-%m-%d"),
        "return_date": None,
        "fine_paid": 0.0
    }
    
    # Update availability
    update_book_availability(isbn, -1)
    
    # Save transaction
    transactions = get_data("transactions")
    transactions.append(transaction)
    save_data("transactions", transactions)
    
    return f"Successfully issued '{book['title']}' to '{member['name']}'. Due on {transaction['due_date']}."

def return_book(transaction_id: str):
    """Return a book and calculate any fines."""
    transactions = get_data("transactions")
    
    for t in transactions:
        if t["transaction_id"] == transaction_id and t["return_date"] is None:
            return_date = datetime.now().strftime("%Y-%m-%d")
            t["return_date"] = return_date
            
            # Calculate fine
            fine = calculate_fine(t["due_date"], return_date)
            if fine > 0:
                add_fine_to_member(t["member_id"], fine)
            
            # Update book availability
            update_book_availability(t["isbn"], 1)
            
            save_data("transactions", transactions)
            
            msg = f"Book returned successfully."
            if fine > 0:
                msg += f" A fine of ${fine:.2f} was added to the member's account."
            return msg
            
    return "Active transaction not found or book already returned."

def get_member_transactions(member_id: str):
    """Get all transactions for a member."""
    transactions = get_data("transactions")
    return [t for t in transactions if t["member_id"] == member_id]

def get_all_transactions():
    """Get all transactions."""
    return get_data("transactions")
