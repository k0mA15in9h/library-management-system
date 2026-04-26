from library.menu import run_menu

if __name__ == "__main__":
    try:
        run_menu()
    except KeyboardInterrupt:
        print("\nExiting Library Management System. Goodbye!")
