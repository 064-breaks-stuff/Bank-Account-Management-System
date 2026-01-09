# Bank Management System
class BankAccount:
    def __init__(self, account_holder, balance=0):
        self.account_holder = account_holder
        self.balance = balance
 
    def deposit(self, amount):
        self.balance += amount
        print(f"Deposited: ${amount}. Current Balance: ${self.balance}")
 
    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            print(f"Withdrawn: ${amount}. Current Balance: ${self.balance}")
        else:
            print("Insufficient balance")
 
    def show_balance(self):
        print(f"Account Holder: {self.account_holder}")
        print(f"Balance: ${self.balance}")
 
# Create a bank account
account = BankAccount("John Doe", 500)
 
# Simulate user actions
account.deposit(200)
account.withdraw(150)
account.show_balance()