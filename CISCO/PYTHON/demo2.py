class BankAccount:
    def __init__(self,name,balance):
        self.name=name
        self.balance=balance
    def show_balance(self):
        print("balance is",self.balance)
    def deposit(self,dep_amt):
        if dep_amt<=0:
            print("dep amt must be greater than 0")
        else:
            self.balance+=dep_amt
            print("Successfully deposited")

    def withdraw(self,with_amt):
        if with_amt>self.balance:
            print("insufficient fund")
        elif with_amt<0:
            print(" withdraw amount must be greater than 0")
        else:
            self.balance-=with_amt
            print("Successfully withdrawn")

bank_act=BankAccount("mru",40000)
while True:
    print("-----MENU------")
    print("1. Show Balance")
    print("2. Deposit")
    print("3. Withdraw")
    print("4. Exit")
    choice=input("Enter your choice:")
    if choice=="1":
        bank_act.show_balance()
    if choice=="2":
        dep_amt=int(input("Enter deposit amount:"))
        bank_act.deposit(dep_amt)

    if choice=="3":
        with_amt=int(input("Enter withdraw amount:"))
        bank_act.withdraw(with_amt)
    if choice=="4":
        print("Thanks!")



