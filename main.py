# Bank Management System

import pandas as pd
class BankAccount:
    def __init__(self, account_holder: str, bank_name: str, balance: float=0):
        self.account_holder = account_holder
        self.balance = balance
        self.bank_name = bank_name
 
    def deposit(self, amount: float, source: str):
        self.balance += amount
        print(f"Deposited: ${amount}, Source: {source}. Current Balance: ${self.balance}")
 
    def withdraw(self, amount: float, reason: str):
        if self.balance >= amount:
            self.balance -= amount
            print(f"Withdrawn: ${amount}, Reason: {reason}. Current Balance: ${self.balance}")
        else:
            print("Insufficient balance")
 
    def show_balance(self):
        print(f"Account Holder: {self.account_holder}")
        print(f"Name of bank: {self.bank_name}")
        print(f"Balance: ${self.balance}")
 
# Check if the user has an already existing bank account and proceed accordingly

'''
affirm:str = input("Do you have an existing bank account? ")

yes = ["yes", "Yes", "YES", "y", "Y", "yeah", "Yeah", "yep", "Yep", "yup", "Yup", "ya", "aye", "Aye", "affirmative", "ok", "OK", "okay", "Sure", "alright", "right", "correct", "true", "indeed", "absolutely", "definitely", "certainly", "got it", "understood", "roger", "👍", "👌", "✅"]

no = ["no", "No", "NO", "n", "N", "nah", "Nah", "nope", "Nope", "nop", "nay", "Nay", "negative", "Negative", "not", "Not", "never", "Never", "nuh-uh", "no way", "No way", "not at all", "Not at all", "decline", "Decline", "pass", "Pass", "nah fam", "wrong", "Wrong", "false", "False", "disagree", "Disagree", "👎", "❌", "🚫", "否", "non", "nein", "нет"]

if affirm in no:
    name:str = input("Under what name would you like to open your new account? ")
    bank:str = input("With which bank would you like to open your new account? ")
    account = BankAccount(name, bank)

elif affirm in yes:
    name:str = input("Under what name did you open your bank account? ")
    bank:str = input("With which bank did you open your bank account? ") '''

# Create a bank account

name:str = input("Under what name would you like to open your new account? ")
bank:str = input("With which bank would you like to open your new account? ")
account = BankAccount(name, bank)

# Create a pandas dataframe to display withdraw and deposit statements along with balance remaining

bank_database = pd.DataFrame(columns = ["Status", "Amount", "Source/Reason", "Balance"])
 
# Simulate user actions

action:str = input("What would you like to do?: \n(1) Deposit money\n(2) Withdraw money\n(3) Check Balance\n\n")

list1 = []

match action.lower():

    case "deposit" | "deposit money" | "1" | "(1)": 
        amount, source = input("Please enter the amount you would like to deposit, followed by the source of the money to be deposited, separated by commas.\n").split(", ")
        list1.append("Deposit")
        amount = int(amount)
        list1.append(amount)
        list1.append(source)
        account.deposit(amount, source)
        list1.append(amount)

    case "withdraw" | "withdraw money" | "2" | "(2)": 
        amount, reason = input("Please enter the amount you would like to withdraw, followed by the reason for withdrawal, separated by commas.\n").split(", ")
        list1.append("Withdrawal")
        amount = int(amount)
        list1.append(amount)
        list1.append(reason)
        account.withdraw(amount, reason)
        list1.append(amount)

    case "show balance" | "balance" | "3" | "(3)": account.show_balance()

    case _: print("Please choose one of the listed actions.")

list1 = pd.DataFrame(list1, columns=bank_database.columns)

bank_database = pd.concat([bank_database, list1], ignore_index = True)
print(bank_database)