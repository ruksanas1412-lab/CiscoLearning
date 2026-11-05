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
    def withdraw(self,with_amt):
        if with_amt>self.balance:
            print("insufficient fund")
        elif with_amt<0:
            print(" withdraw amount must be greater than 0")
        else:
            self.balance-=with_amt
bank_act=BankAccount("mru",40000)
bank_act.show_balance()
dep_amt=int(input("Enter deposit amount:"))
bank_act.deposit(dep_amt)
bank_act.show_balance()



