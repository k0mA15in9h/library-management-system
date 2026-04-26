from .storage import get_data, save_data

def add_book(isbn: str, title: str, author: str, copies: int):
    """Add a new book or increase copies if it already exists."""
    books = get_data("books")
    
    for book in books:
        if book["isbn"] == isbn:
            book["copies_total"] += copies
            book["copies_available"] += copies
            save_data("books", books)
            return f"Updated copies for '{title}'."
            
    # If not found, add a new one
    new_book = {
        "isbn": isbn,
        "title": title,
        "author": author,
        "copies_total": copies,
        "copies_available": copies
    }
    books.append(new_book)
    save_data("books", books)
    return f"Successfully added '{title}'."

def get_all_books() -> list:
    """Return a list of all books."""
    return get_data("books")

def search_book(query: str) -> list:
    """Search for a book by title, author, or ISBN."""
    books = get_data("books")
    query = query.lower()
    results = [
        b for b in books 
        if query in b["title"].lower() or query in b["author"].lower() or query in b["isbn"].lower()
    ]
    return results

def get_book_by_isbn(isbn: str):
    """Fetch a specific book by its ISBN."""
    books = get_data("books")
    for book in books:
        if book["isbn"] == isbn:
            return book
    return None

def update_book_availability(isbn: str, increment: int):
    """Update the available copies of a book. Can be negative (borrow) or positive (return)."""
    books = get_data("books")
    for book in books:
        if book["isbn"] == isbn:
            book["copies_available"] += increment
            save_data("books", books)
            return True
    return False

def add_member(member_id: str, name: str):
    """Add a new member."""
    members = get_data("members")
    for m in members:
        if m["member_id"] == member_id:
            return f"Member ID {member_id} already exists."
    
    new_member = {
        "member_id": member_id,
        "name": name,
        "fines_due": 0.0
    }
    members.append(new_member)
    save_data("members", members)
    return f"Successfully added member '{name}'."

def get_all_members() -> list:
    return get_data("members")

def get_member(member_id: str):
    """Fetch member details by ID."""
    members = get_data("members")
    for m in members:
        if m["member_id"] == member_id:
            return m
    return None
