import time
from collections import defaultdict
import json
from derecho.cascade.client import ServiceClientAPI


class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR

class Bank:
    capi = ServiceClientAPI()
    transaction = capi.create_object_pool("/transaction","VolatileCascadeStoreWithStringKey",0)
    account = capi.create_object_pool("/account","VolatileCascadeStoreWithStringKey",0)

    def getTime(self):
        localtime = time.asctime(time.localtime(time.time()))
        return localtime

    def getMonth(self):
        time_now = time.asctime(time.localtime(time.time()))
        time_now = time_now.split(' ')
        month_year = time_now[1]+'/'+time_now[-1]
        return month_year
    
    # New_account creates a new account
    # parameter:
    # the meta-data to create an account
    
    def new_account(self, bank_account_id, owner_name, text_id, contact_info, overdraft_limit, overdraft_intrRate, balance):
        new_account={
                'bank_account_id': bank_account_id,
                'owner_name': owner_name,
                'text_id': text_id,
                'contact_info': contact_info,
                'overdraft_limit': overdraft_limit,
                'overdraft_intrRate': overdraft_intrRate,
                'balance': balance}     

        res = self.capi.put('/account/{}'.format(bank_account_id),json.dumps(new_account).encode(),previous_version=ServiceClientAPI.CURRENT_VERSION,previous_version_by_key=ServiceClientAPI.CURRENT_VERSION)
        if res:
            ver = res.get_result()
            print(bcolors.OK + f"Put is successful with version {ver}." + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, put returns null." + bcolors.RESET)

        transaction={self.getMonth():[]}
        res = self.capi.put('/transaction/{}'.format(bank_account_id),json.dumps(transaction).encode(),previous_version=ServiceClientAPI.CURRENT_VERSION,previous_version_by_key=ServiceClientAPI.CURRENT_VERSION)
        if res:
            ver = res.get_result()
            print(bcolors.OK + f"Put is successful with version {ver}." + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, put returns null." + bcolors.RESET)


    # Deposit puts money into an account.
    # parameter:
    # bank_account_id: the account id
    # money: amount of money to deposit
    def deposit(self, bank_account_id, money):
        if money < 0:
            return False
        # if bank_account_id not in self.account:
        #     return False
        res = self.capi.get('/account/{}'.format(bank_account_id))
        odict = res.get_result()
        print(odict)
        account = json.loads(odict['value'].decode())
        account['balance']+= money
        print(account)

        res = self.capi.put('/account/{}'.format(bank_account_id),json.dumps(account).encode(),previous_version=ServiceClientAPI.CURRENT_VERSION,previous_version_by_key=ServiceClientAPI.CURRENT_VERSION)
        if res:
            ver = res.get_result()
            print(bcolors.OK + f"Put is successful with version {ver}." + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, put returns null." + bcolors.RESET)
        
        res = self.capi.get('/transaction/{}'.format(bank_account_id))
        odict = res.get_result()
        print(odict)
        transaction=json.loads(odict['value'].decode())
        transaction[self.getMonth()].append(bank_account_id+" deposit "+ str(money) +" in "+self.getTime())
        print(transaction)
        res = self.capi.put('/transaction/{}'.format(self.bank_account_id),json.dumps(transaction).encode(),previous_version=ServiceClientAPI.CURRENT_VERSION,previous_version_by_key=ServiceClientAPI.CURRENT_VERSION)

        # month=self.getMonth()
        # if month not in self.transaction[bank_account_id]:
        #     self.transaction[bank_account_id][month] = []        
        # self.transaction[bank_account_id][month].append(bank_account_id+" deposit "+str(money)+" in "+self.getTime())

        return True

    # Withdraw takes money out
    # parameter:
    # bank_account_id: the account id
    # money: amount of money to withdraw
    def withdraw(self, bank_account_id, money):
        if money < 0:
            return False
        if bank_account_id not in self.account:
            return False
        account = self.account[bank_account_id]
        if account.balance >= money:
            account.balance -= money
            
            month=self.getMonth()
            if month not in self.transaction[bank_account_id]:
                self.transaction[bank_account_id][month] = []       
            self.transaction[bank_account_id][month].append(bank_account_id+" withdraw "+str(money)+" in "+self.getTime())
            
            return True

        else:
            return False

    # Transfer: moves money from one account to another
    # parameter:
    # fromaccount_id: the account id to withdraw
    # toaccount_id: the account id to deposit
    # money: amount of money to transfer
    def transfer(self, fromaccount_id, toaccount_id, money):
        if money < 0:
            return False
        if fromaccount_id not in self.account or toaccount_id not in self.account:
            return False
        
        fromaccount = self.account[fromaccount_id]
        if fromaccount.balance >= money:
            fromaccount.balance -= money
            toaccount = self.account[toaccount_id]
            toaccount.balance += money

            month=self.getMonth()
            if month not in self.transaction[fromaccount_id]:
                self.transaction[fromaccount_id][month] = []       
            self.transaction[fromaccount_id][month].append(fromaccount_id+" transfer "+str(money)+" to "+toaccount_id+" in "+self.getTime())

            if month not in self.transaction[toaccount_id]:
                self.transaction[toaccount_id][month] = []       
            self.transaction[toaccount_id][month].append(fromaccount_id+" transfer "+str(money)+" to "+toaccount_id+" in "+self.getTime())


            return True
        else:
            return False
    
    # Dashboard generates a report showing the customer’s current bank balance and the transactions for the current month.
    # parameter:
    # bank_account_id: the account id to generate dashboard
    def dashboard(self, bank_account_id):
        if bank_account_id not in self.account:
            return False
        month=self.getMonth()
        print("current balance:",self.account[bank_account_id].balance)
        print(self.transaction[bank_account_id][month])

    # Audit generates a report for the entire bank, with a dashboard record for every customer.
    def audit(self):
        audit_result=sorted(self.transaction.items(),key=lambda x:self.account[x[0]].owner_name,reverse=False)
        for item in audit_result:
            print(item)
        

class bankAccount:
    bank_account_id = 0
    owner_name = ""
    tex_id = ""
    contact_info = ""
    open_date = ""
    overdraft_limit = ""
    overdraft_inter_rate = ""
    balance = 0

    def __init__(self, bank_account_id, owner_name, text_id, contact_info, overdraft_limit, overdraft_intrRate, balance):
        self.bank_account_id = bank_account_id
        self.owner_name = owner_name
        self.tex_id = text_id
        self.contact_info = contact_info
        self.overdraft_limit = overdraft_limit
        self.overdraft_inter_rate = overdraft_intrRate
        self.balance = balance


B=Bank()
res=B.new_account('111213','lhz','text_id_blanc','contact_info_blank','overdraft_limit','overdraft_intrRate',100)
B.deposit('111213',100)

