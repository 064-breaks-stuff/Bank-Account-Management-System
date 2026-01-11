import sqlite3
import os
from datetime import datetime

# ============================================================================
# DATABASE SETUP AND INITIALIZATION
# ============================================================================

class BankDatabase:
    """
    Manages all database operations for the bank management system.
    Uses SQLite for persistent storage with proper table relationships.
    """
    
    def __init__(self, db_name: str = 'bank_system.db'):
        """
        Initialize the database connection and create tables if they don't exist.
        
        Args:
            db_name (str): Name of the SQLite database file
        """
        # sqlite3.connect() opens a connection to the database file
        # If the file doesn't exist, it creates it automatically
        self.connection = sqlite3.connect(db_name)
        
        # Enable foreign key constraints (disabled by default in SQLite)
        # This ensures data integrity when records reference other records
        self.connection.execute("PRAGMA foreign_keys = 1")
        
        # Create a cursor object to execute SQL queries
        # The cursor is like a "command executor" for the database
        self.cursor = self.connection.cursor()
        
        # Initialize all tables when the database is created
        self.create_tables()
    
    def create_tables(self):
        """
        Create two main tables:
        1. accounts - Stores account holder information
        2. transactions - Stores all transaction records linked to accounts
        """
        
        # -------- CREATE ACCOUNTS TABLE --------
        # This is the "parent" table containing account information
        create_accounts_table = """
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            -- PRIMARY KEY ensures each account has a unique ID
            -- AUTOINCREMENT means the ID is automatically generated
            
            account_holder TEXT NOT NULL UNIQUE,
            -- Text field for the account holder's name
            -- NOT NULL means this field must always have a value
            -- UNIQUE ensures no two accounts have the same holder name
            
            bank_name TEXT NOT NULL,
            -- Text field for the bank name
            
            balance REAL NOT NULL DEFAULT 0,
            -- REAL allows decimal numbers (for monetary values)
            -- DEFAULT 0 means new accounts start with $0
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            -- TIMESTAMP stores the date and time account was created
            -- CURRENT_TIMESTAMP automatically records when the account was created
        );
        """
        
        # -------- CREATE TRANSACTIONS TABLE --------
        # This is the "child" table containing all transaction records
        create_transactions_table = """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            -- Unique identifier for each transaction
            
            account_id INTEGER NOT NULL,
            -- Links this transaction to a specific account (Foreign Key)
            -- NOT NULL means every transaction must be linked to an account
            
            action TEXT NOT NULL CHECK(action IN ('Deposit', 'Withdrawal', 'Balance Check')),
            -- The type of action performed (must be one of the three options)
            -- CHECK constraint ensures only valid actions are stored
            
            amount REAL,
            -- The transaction amount (can be NULL for Balance Check actions)
            
            source_or_reason TEXT,
            -- For deposits: the source of money (e.g., "Salary", "Transfer")
            -- For withdrawals: the reason for withdrawal (e.g., "Bills", "Shopping")
            -- Can be NULL for Balance Check actions
            
            balance_after REAL NOT NULL,
            -- The account balance immediately after this transaction
            -- Stored for record-keeping and audit purposes
            
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            -- Records when the transaction occurred
            
            FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
            -- Foreign Key relationship to the accounts table:
            --   - account_id must reference a valid account_id in accounts table
            --   - ON DELETE CASCADE means if an account is deleted, all its 
            --     transactions are automatically deleted too
        );
        """
        
        # Execute both CREATE TABLE statements
        # IF NOT EXISTS prevents errors if tables already exist
        self.cursor.execute(create_accounts_table)
        self.cursor.execute(create_transactions_table)
        
        # commit() saves the changes permanently to the database
        self.connection.commit()
    
    def close(self):
        """Close the database connection"""
        # Always close the connection when done
        self.connection.close()


# ============================================================================
# BANK ACCOUNT MANAGEMENT
# ============================================================================

class BankAccount:
    """
    Represents a single bank account with database integration.
    Handles deposits, withdrawals, and balance inquiries while storing
    all transactions in the database.
    """
    
    def __init__(self, account_holder: str, bank_name: str, db_cursor, db_connection):
        """
        Initialize or retrieve a bank account.
        
        Args:
            account_holder (str): Name of the account holder
            bank_name (str): Name of the bank
            db_cursor: Database cursor for executing queries
            db_connection: Database connection object for committing changes
        """
        self.account_holder = account_holder
        self.bank_name = bank_name
        self.cursor = db_cursor
        self.connection = db_connection
        self.account_id = None
        self.balance = 0.0
        
        # Check if account already exists, if not create it
        self.create_or_retrieve_account()
    
    def create_or_retrieve_account(self):
        """
        Check if the account exists in the database.
        If it exists, retrieve its details.
        If not, create a new account.
        """
        # SELECT query to find an existing account with this holder name
        self.cursor.execute(
            "SELECT account_id, balance FROM accounts WHERE account_holder = ?",
            (self.account_holder,)  # ? is a placeholder to prevent SQL injection
        )
        
        # fetchone() returns the first matching row, or None if no match
        result = self.cursor.fetchone()
        
        if result:
            # Account exists - retrieve its ID and current balance
            self.account_id, self.balance = result
            print(f"\n✓ Account retrieved for {self.account_holder}")
        else:
            # Account doesn't exist - create a new one
            self.cursor.execute(
                """INSERT INTO accounts (account_holder, bank_name, balance)
                   VALUES (?, ?, ?)""",
                (self.account_holder, self.bank_name, 0.0)
            )
            # commit() saves the INSERT to the database
            self.connection.commit()
            
            # Get the ID of the newly created account
            # lastrowid returns the primary key of the last inserted row
            self.account_id = self.cursor.lastrowid
            self.balance = 0.0
            print(f"\n✓ New account created for {self.account_holder}")
    
    def deposit(self, amount: float, source: str):
        """
        Add money to the account and record the transaction.
        
        Args:
            amount (float): Amount to deposit
            source (str): Source of the deposit (e.g., "Salary", "Transfer")
        """
        # Validate input
        if amount <= 0:
            print("\n✗ Deposit amount must be positive!")
            return False
        
        # Update the account balance in the database
        self.balance += amount
        
        # UPDATE query to modify the balance in the accounts table
        self.cursor.execute(
            "UPDATE accounts SET balance = ? WHERE account_id = ?",
            (self.balance, self.account_id)
        )
        
        # Record the transaction in the transactions table
        self.cursor.execute(
            """INSERT INTO transactions 
               (account_id, action, amount, source_or_reason, balance_after)
               VALUES (?, ?, ?, ?, ?)""",
            (self.account_id, 'Deposit', amount, source, self.balance)
        )
        
        # Save all changes to the database
        self.connection.commit()
        
        print(f"\n✓ Deposited: ${amount:.2f}")
        print(f"  Source: {source}")
        print(f"  Current Balance: ${self.balance:.2f}")
        return True
    
    def withdraw(self, amount: float, reason: str):
        """
        Remove money from the account and record the transaction.
        
        Args:
            amount (float): Amount to withdraw
            reason (str): Reason for withdrawal (e.g., "Bills", "Shopping")
        """
        # Validate input
        if amount <= 0:
            print("\n✗ Withdrawal amount must be positive!")
            return False
        
        # Check for sufficient balance (THIS WAS COMMENTED OUT IN YOUR ORIGINAL CODE)
        if self.balance < amount:
            print(f"\n✗ Insufficient balance! Available: ${self.balance:.2f}")
            return False
        
        # Update the account balance
        self.balance -= amount
        
        # UPDATE query to modify the balance in the database
        self.cursor.execute(
            "UPDATE accounts SET balance = ? WHERE account_id = ?",
            (self.balance, self.account_id)
        )
        
        # Record the transaction
        self.cursor.execute(
            """INSERT INTO transactions 
               (account_id, action, amount, source_or_reason, balance_after)
               VALUES (?, ?, ?, ?, ?)""",
            (self.account_id, 'Withdrawal', amount, reason, self.balance)
        )
        
        # Save changes to the database
        self.connection.commit()
        
        print(f"\n✓ Withdrawn: ${amount:.2f}")
        print(f"  Reason: {reason}")
        print(f"  Current Balance: ${self.balance:.2f}")
        return True
    
    def check_balance(self):
        """
        Display account balance and record a balance check transaction.
        This helps maintain a complete audit trail.
        """
        # Refresh balance from database to ensure we have the latest value
        self.cursor.execute(
            "SELECT balance FROM accounts WHERE account_id = ?",
            (self.account_id,)
        )
        
        # fetchone() returns a tuple, so we extract the first element [0]
        result = self.cursor.fetchone()
        if result:
            self.balance = result[0]
        
        # Record the balance check action
        self.cursor.execute(
            """INSERT INTO transactions 
               (account_id, action, balance_after)
               VALUES (?, ?, ?)""",
            (self.account_id, 'Balance Check', self.balance)
        )
        self.connection.commit()
        
        # Display account information
        print(f"\n{'='*40}")
        print(f"Account Holder: {self.account_holder}")
        print(f"Bank Name: {self.bank_name}")
        print(f"Account ID: {self.account_id}")
        print(f"Current Balance: ${self.balance:.2f}")
        print(f"{'='*40}")
    
    def get_transaction_history(self):
        """
        Retrieve and display all transactions for this account from the database.
        """
        # SELECT query to get all transactions for this account
        # ORDER BY transaction_date DESC sorts by most recent first
        self.cursor.execute(
            """SELECT transaction_id, action, amount, source_or_reason, balance_after, transaction_date
               FROM transactions 
               WHERE account_id = ? 
               ORDER BY transaction_date DESC""",
            (self.account_id,)
        )
        
        # fetchall() returns all matching rows as a list of tuples
        transactions = self.cursor.fetchall()
        
        if not transactions:
            print("\n✗ No transactions found!")
            return
        
        # Display transaction history in a formatted table
        print(f"\n{'='*100}")
        print(f"Transaction History for {self.account_holder}")
        print(f"{'='*100}")
        print(f"{'ID':<5} {'Action':<12} {'Amount':<12} {'Details':<20} {'Balance':<12} {'Date':<20}")
        print(f"{'-'*100}")
        
        # Loop through each transaction
        for trans in transactions:
            trans_id, action, amount, details, balance, date = trans
            # Format amount: show "N/A" for Balance Check transactions
            amount_str = f"${amount:.2f}" if amount else "N/A"
            # Truncate details if too long
            details_str = (details[:19] if details else "")
            
            print(f"{trans_id:<5} {action:<12} {amount_str:<12} {details_str:<20} ${balance:<11.2f} {date:<20}")
        
        print(f"{'='*100}\n")


# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    """Main program execution"""
    
    # Initialize the database
    db = BankDatabase('bank_system.db')
    
    try:
        # Get account information from user
        print("\n" + "="*50)
        print("Welcome to Bank Management System")
        print("="*50)
        
        name = input("\nEnter account holder name: ").strip()
        bank = input("Enter bank name: ").strip()
        
        # Create or retrieve account
        account = BankAccount(name, bank, db.cursor, db.connection)
        
        # Main menu loop
        while True:
            print("\n" + "="*50)
            print("What would you like to do?")
            print("="*50)
            print("(1) Deposit money")
            print("(2) Withdraw money")
            print("(3) Check Balance")
            print("(4) View Transaction History")
            print("(5) Exit")
            
            action = input("\nChoose an option (1-5): ").strip()
            
            if action == "1" or action.lower() == "deposit":
                try:
                    amount = float(input("Enter deposit amount: $"))
                    source = input("Enter source (e.g., Salary, Transfer): ").strip()
                    account.deposit(amount, source)
                except ValueError:
                    print("\n✗ Please enter a valid amount!")
            
            elif action == "2" or action.lower() == "withdraw":
                try:
                    amount = float(input("Enter withdrawal amount: $"))
                    reason = input("Enter reason for withdrawal: ").strip()
                    account.withdraw(amount, reason)
                except ValueError:
                    print("\n✗ Please enter a valid amount!")
            
            elif action == "3" or action.lower() == "balance":
                account.check_balance()
            
            elif action == "4" or action.lower() == "history":
                account.get_transaction_history()
            
            elif action == "5" or action.lower() == "exit":
                print("\n✓ Thank you for using Bank Management System!")
                break
            
            else:
                print("\n✗ Invalid option. Please choose 1-5.")
    
    finally:
        # Always close the database connection when done
        # This ensures data is saved and resources are released
        db.close()
        print("\n✓ Database connection closed.")


if __name__ == "__main__":
    main()