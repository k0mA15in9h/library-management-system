import sys
import tkinter as tk
from tkinter import ttk, messagebox

from .storage import initialize_storage
from .books import (
    add_book, get_all_books, search_book, 
    add_member, get_all_members, get_member
)
from .transactions import issue_book, return_book, get_member_transactions
from .fine import pay_fine

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("900x700")

        self.style = ttk.Style()
        self.style.configure("TFrame", padding=10)
        self.style.configure("TButton", font=("Helvetica", 10))
        self.style.configure("TLabel", font=("Helvetica", 11))
        self.style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        initialize_storage()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Tabs
        self.books_tab = ttk.Frame(self.notebook)
        self.members_tab = ttk.Frame(self.notebook)
        self.transactions_tab = ttk.Frame(self.notebook)
        self.dashboard_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.books_tab, text='Books')
        self.notebook.add(self.members_tab, text='Members')
        self.notebook.add(self.transactions_tab, text='Transactions')
        self.notebook.add(self.dashboard_tab, text='Dashboard')

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.setup_books_tab()
        self.setup_members_tab()
        self.setup_transactions_tab()
        self.setup_dashboard_tab()

    def on_tab_change(self, event):
        tab_id = self.notebook.index(self.notebook.select())
        if tab_id == 0:
            self.refresh_books_list()
        elif tab_id == 1:
            self.refresh_members_list()

    # --- BOOKS TAB ---
    def setup_books_tab(self):
        # Top Frame: Add Book
        top_frame = ttk.LabelFrame(self.books_tab, text="Add a New Book")
        top_frame.pack(fill='x', pady=5)

        ttk.Label(top_frame, text="ISBN:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.book_isbn_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=self.book_isbn_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(top_frame, text="Title:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.book_title_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=self.book_title_var).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(top_frame, text="Author:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.book_author_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=self.book_author_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(top_frame, text="Copies:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.book_copies_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=self.book_copies_var).grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(top_frame, text="Add Book", command=self.add_new_book).grid(row=0, column=4, rowspan=2, padx=15, pady=5)

        # Middle Frame: Search
        search_frame = ttk.Frame(self.books_tab)
        search_frame.pack(fill='x', pady=5)
        ttk.Label(search_frame, text="Search Book:").pack(side='left', padx=5)
        self.book_search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.book_search_var, width=30).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_books_action).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Clear", command=self.refresh_books_list).pack(side='left', padx=5)

        # Bottom Frame: List
        list_frame = ttk.Frame(self.books_tab)
        list_frame.pack(expand=True, fill='both', pady=5)

        columns = ("isbn", "title", "author", "available", "total")
        self.books_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.books_tree.heading("isbn", text="ISBN")
        self.books_tree.heading("title", text="Title")
        self.books_tree.heading("author", text="Author")
        self.books_tree.heading("available", text="Available")
        self.books_tree.heading("total", text="Total")

        self.books_tree.column("isbn", width=100)
        self.books_tree.column("available", width=80, anchor='center')
        self.books_tree.column("total", width=80, anchor='center')

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.books_tree.yview)
        self.books_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.books_tree.pack(side='left', expand=True, fill='both')

        self.refresh_books_list()

    def add_new_book(self):
        isbn = self.book_isbn_var.get().strip()
        title = self.book_title_var.get().strip()
        author = self.book_author_var.get().strip()
        copies_str = self.book_copies_var.get().strip()

        if not (isbn and title and author and copies_str):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        try:
            copies = int(copies_str)
            if copies <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Copies must be a positive integer.")
            return

        result = add_book(isbn, title, author, copies)
        messagebox.showinfo("Success", result)
        self.book_isbn_var.set("")
        self.book_title_var.set("")
        self.book_author_var.set("")
        self.book_copies_var.set("")
        self.refresh_books_list()

    def refresh_books_list(self):
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        books = get_all_books()
        for b in books:
            self.books_tree.insert("", tk.END, values=(b["isbn"], b["title"], b["author"], b["copies_available"], b["copies_total"]))
        
        self.book_search_var.set("")

    def search_books_action(self):
        query = self.book_search_var.get().strip()
        if not query:
            self.refresh_books_list()
            return
            
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        results = search_book(query)
        for b in results:
            self.books_tree.insert("", tk.END, values=(b["isbn"], b["title"], b["author"], b["copies_available"], b["copies_total"]))

    # --- MEMBERS TAB ---
    def setup_members_tab(self):
        top_frame = ttk.LabelFrame(self.members_tab, text="Register New Member")
        top_frame.pack(fill='x', pady=5)

        ttk.Label(top_frame, text="Member ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.member_id_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=self.member_id_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(top_frame, text="Name:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.member_name_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=self.member_name_var).grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(top_frame, text="Register", command=self.add_new_member).grid(row=0, column=4, padx=15, pady=5)

        list_frame = ttk.Frame(self.members_tab)
        list_frame.pack(expand=True, fill='both', pady=5)

        columns = ("id", "name", "fines")
        self.members_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.members_tree.heading("id", text="Member ID")
        self.members_tree.heading("name", text="Name")
        self.members_tree.heading("fines", text="Fines Due ($)")

        self.members_tree.column("id", width=150)
        self.members_tree.column("fines", width=100, anchor='center')

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.members_tree.yview)
        self.members_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.members_tree.pack(side='left', expand=True, fill='both')

        self.refresh_members_list()

    def add_new_member(self):
        member_id = self.member_id_var.get().strip()
        name = self.member_name_var.get().strip()

        if not (member_id and name):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        result = add_member(member_id, name)
        messagebox.showinfo("Result", result)
        self.member_id_var.set("")
        self.member_name_var.set("")
        self.refresh_members_list()

    def refresh_members_list(self):
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        members = get_all_members()
        for m in members:
            self.members_tree.insert("", tk.END, values=(m["member_id"], m["name"], f"{m['fines_due']:.2f}"))

    # --- TRANSACTIONS TAB ---
    def setup_transactions_tab(self):
        issue_frame = ttk.LabelFrame(self.transactions_tab, text="Issue a Book")
        issue_frame.pack(fill='x', pady=10)

        ttk.Label(issue_frame, text="Book ISBN:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.tx_issue_isbn_var = tk.StringVar()
        ttk.Entry(issue_frame, textvariable=self.tx_issue_isbn_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(issue_frame, text="Member ID:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.tx_issue_member_var = tk.StringVar()
        ttk.Entry(issue_frame, textvariable=self.tx_issue_member_var).grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(issue_frame, text="Issue Book", command=self.issue_book_action).grid(row=0, column=4, padx=15, pady=5)

        return_frame = ttk.LabelFrame(self.transactions_tab, text="Return a Book")
        return_frame.pack(fill='x', pady=10)

        ttk.Label(return_frame, text="Transaction ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.tx_return_id_var = tk.StringVar()
        ttk.Entry(return_frame, textvariable=self.tx_return_id_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(return_frame, text="Return Book", command=self.return_book_action).grid(row=0, column=2, padx=15, pady=5)

    def issue_book_action(self):
        isbn = self.tx_issue_isbn_var.get().strip()
        member_id = self.tx_issue_member_var.get().strip()

        if not (isbn and member_id):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        result = issue_book(isbn, member_id)
        messagebox.showinfo("Result", result)
        self.tx_issue_isbn_var.set("")
        self.tx_issue_member_var.set("")

    def return_book_action(self):
        tx_id = self.tx_return_id_var.get().strip()
        if not tx_id:
            messagebox.showwarning("Input Error", "Please provide a Transaction ID.")
            return

        result = return_book(tx_id)
        messagebox.showinfo("Result", result)
        self.tx_return_id_var.set("")

    # --- DASHBOARD TAB ---
    def setup_dashboard_tab(self):
        search_frame = ttk.Frame(self.dashboard_tab)
        search_frame.pack(fill='x', pady=10)

        ttk.Label(search_frame, text="Member ID:").pack(side='left', padx=5)
        self.dash_member_id_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.dash_member_id_var).pack(side='left', padx=5)
        ttk.Button(search_frame, text="View Dashboard", command=self.view_dashboard).pack(side='left', padx=15)

        self.dash_info_var = tk.StringVar()
        self.dash_info_var.set("Enter a Member ID to view details.")
        info_label = ttk.Label(self.dashboard_tab, textvariable=self.dash_info_var, style="Header.TLabel")
        info_label.pack(pady=5, anchor='w')

        # Fines Payment Area
        self.fine_frame = ttk.LabelFrame(self.dashboard_tab, text="Pay Fines")
        ttk.Label(self.fine_frame, text="Amount ($):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.dash_fine_amount_var = tk.StringVar()
        ttk.Entry(self.fine_frame, textvariable=self.dash_fine_amount_var).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.fine_frame, text="Pay Fine", command=self.pay_fine_action).grid(row=0, column=2, padx=15, pady=5)

        # Transactions List
        ttk.Label(self.dashboard_tab, text="Transaction History:", font=("Helvetica", 11, "bold")).pack(anchor='w', pady=(15, 5))
        
        list_frame = ttk.Frame(self.dashboard_tab)
        list_frame.pack(expand=True, fill='both', pady=5)

        columns = ("tx_id", "isbn", "issue_date", "due_date", "status")
        self.dash_tx_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.dash_tx_tree.heading("tx_id", text="Txn ID")
        self.dash_tx_tree.heading("isbn", text="ISBN")
        self.dash_tx_tree.heading("issue_date", text="Issue Date")
        self.dash_tx_tree.heading("due_date", text="Due Date")
        self.dash_tx_tree.heading("status", text="Status")

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.dash_tx_tree.yview)
        self.dash_tx_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.dash_tx_tree.pack(side='left', expand=True, fill='both')

    def view_dashboard(self):
        member_id = self.dash_member_id_var.get().strip()
        if not member_id:
            return

        member = get_member(member_id)
        if not member:
            messagebox.showwarning("Not Found", "Member not found.")
            self.dash_info_var.set("Member not found.")
            self.fine_frame.pack_forget()
            self._clear_dash_tree()
            return

        self.dash_info_var.set(f"Profile: {member['name']} (ID: {member['member_id']}) | Fines Due: ${member['fines_due']:.2f}")
        
        if member['fines_due'] > 0:
            self.fine_frame.pack(fill='x', pady=5, after=self.dash_info_var.get() and self.dashboard_tab.winfo_children()[1])
        else:
            self.fine_frame.pack_forget()

        self._clear_dash_tree()
        transactions = get_member_transactions(member_id)
        for t in transactions:
            status = "Returned" if t['return_date'] else "Pending"
            self.dash_tx_tree.insert("", tk.END, values=(t['transaction_id'], t['isbn'], t['issue_date'], t['due_date'], status))

    def _clear_dash_tree(self):
        for item in self.dash_tx_tree.get_children():
            self.dash_tx_tree.delete(item)

    def pay_fine_action(self):
        member_id = self.dash_member_id_var.get().strip()
        amount_str = self.dash_fine_amount_var.get().strip()

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid fine amount.")
            return

        result = pay_fine(member_id, amount)
        messagebox.showinfo("Result", result)
        self.dash_fine_amount_var.set("")
        self.view_dashboard()  # Refresh Dashboard


def run_menu():
    """Main application loop initialized from main.py."""
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()
