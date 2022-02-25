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
        
        res = self.capi.get('/account/{}'.format(bank_account_id))
        if res:
            odict = res.get_result()
            print(bcolors.OK + f"Get is successful with details: {type(odict)}" + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, get returns null." + bcolors.RESET)
            quit()

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
        if res:
            odict = res.get_result()
            print(bcolors.OK + f"Get is successful with details: {type(odict)}" + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, get returns null." + bcolors.RESET)
            quit()

        print(odict)
        transaction=json.loads(odict['value'].decode())
        transaction[self.getMonth()].append(bank_account_id+" deposit "+ str(money) +" in "+self.getTime())
        print(transaction)
        
        res = self.capi.put('/transaction/{}'.format(bank_account_id),json.dumps(transaction).encode(),previous_version=ServiceClientAPI.CURRENT_VERSION,previous_version_by_key=ServiceClientAPI.CURRENT_VERSION)
        if res:
            ver = res.get_result()
            print(bcolors.OK + f"Put is successful with version {ver}." + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, put returns null." + bcolors.RESET)

    # Withdraw takes money out
    # parameter:
    # bank_account_id: the account id
    # money: amount of money to withdraw
    def withdraw(self, bank_account_id, money):
        if money < 0:
            return False
        
        res = self.capi.get('/account/{}'.format(bank_account_id))
        if res:
            odict = res.get_result()
            print(bcolors.OK + f"Get is successful with details: {type(odict)}" + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, get returns null." + bcolors.RESET)
            quit()

        print(odict)
        account = json.loads(odict['value'].decode())
        account['balance']-= money
        print(account)

        res = self.capi.put('/account/{}'.format(bank_account_id),json.dumps(account).encode(),previous_version=ServiceClientAPI.CURRENT_VERSION,previous_version_by_key=ServiceClientAPI.CURRENT_VERSION)
        if res:
            ver = res.get_result()
            print(bcolors.OK + f"Put is successful with version {ver}." + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, put returns null." + bcolors.RESET)
        
        res = self.capi.get('/transaction/{}'.format(bank_account_id))
        if res:
            odict = res.get_result()
            print(bcolors.OK + f"Get is successful with details: {type(odict)}" + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, get returns null." + bcolors.RESET)
            quit()

        print(odict)
        transaction=json.loads(odict['value'].decode())
        transaction[self.getMonth()].append(bank_account_id+" withdraw "+ str(money) +" in "+self.getTime())
        print(transaction)
        
        res = self.capi.put('/transaction/{}'.format(bank_account_id),json.dumps(transaction).encode(),previous_version=ServiceClientAPI.CURRENT_VERSION,previous_version_by_key=ServiceClientAPI.CURRENT_VERSION)
        if res:
            ver = res.get_result()
            print(bcolors.OK + f"Put is successful with version {ver}." + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, put returns null." + bcolors.RESET)



    # Transfer: moves money from one account to another
    # parameter:
    # fromaccount_id: the account id to withdraw
    # toaccount_id: the account id to deposit
    # money: amount of money to transfer
    def transfer(self, fromaccount_id, toaccount_id, money):
        if money < 0:
            return False
        
        res = self.capi.get('/account/{}'.format(fromaccount_id))
        if res:
            odict = res.get_result()
            print(bcolors.OK + f"Get is successful with details: {type(odict)}" + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, get returns null." + bcolors.RESET)
            quit()

        print(odict)
        account = json.loads(odict['value'].decode())
        account['balance']-= money
        print(account)

        res = self.capi.put('/account/{}'.format(fromaccount_id),json.dumps(account).encode(),previous_version=ServiceClientAPI.CURRENT_VERSION,previous_version_by_key=ServiceClientAPI.CURRENT_VERSION)
        if res:
            ver = res.get_result()
            print(bcolors.OK + f"Put is successful with version {ver}." + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, put returns null." + bcolors.RESET)



        res = self.capi.get('/account/{}'.format(toaccount_id))
        if res:
            odict = res.get_result()
            print(bcolors.OK + f"Get is successful with details: {type(odict)}" + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, get returns null." + bcolors.RESET)
            quit()

        print(odict)
        account = json.loads(odict['value'].decode())
        account['balance']+= money
        print(account)

        res = self.capi.put('/account/{}'.format(toaccount_id),json.dumps(account).encode(),previous_version=ServiceClientAPI.CURRENT_VERSION,previous_version_by_key=ServiceClientAPI.CURRENT_VERSION)
        if res:
            ver = res.get_result()
            print(bcolors.OK + f"Put is successful with version {ver}." + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, put returns null." + bcolors.RESET)


        
        res = self.capi.get('/transaction/{}'.format(fromaccount_id))
        if res:
            odict = res.get_result()
            print(bcolors.OK + f"Get is successful with details: {type(odict)}" + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, get returns null." + bcolors.RESET)
            quit()

        print(odict)
        transaction=json.loads(odict['value'].decode())
        transaction[self.getMonth()].append(fromaccount_id+" transfer "+ str(money) +" to " + toaccount_id +" in "+self.getTime())
        print(transaction)
        
        res = self.capi.put('/transaction/{}'.format(fromaccount_id),json.dumps(transaction).encode(),previous_version=ServiceClientAPI.CURRENT_VERSION,previous_version_by_key=ServiceClientAPI.CURRENT_VERSION)
        if res:
            ver = res.get_result()
            print(bcolors.OK + f"Put is successful with version {ver}." + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, put returns null." + bcolors.RESET)


        res = self.capi.get('/transaction/{}'.format(toaccount_id))
        if res:
            odict = res.get_result()
            print(bcolors.OK + f"Get is successful with details: {type(odict)}" + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, get returns null." + bcolors.RESET)
            quit()

        print(odict)
        transaction=json.loads(odict['value'].decode())
        transaction[self.getMonth()].append(fromaccount_id+" transfer "+ str(money) +" to " + toaccount_id +" in "+self.getTime())
        print(transaction)
        
        res = self.capi.put('/transaction/{}'.format(toaccount_id),json.dumps(transaction).encode(),previous_version=ServiceClientAPI.CURRENT_VERSION,previous_version_by_key=ServiceClientAPI.CURRENT_VERSION)
        if res:
            ver = res.get_result()
            print(bcolors.OK + f"Put is successful with version {ver}." + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, put returns null." + bcolors.RESET)
            
    
    # Dashboard generates a report showing the customer’s current bank balance and the transactions for the current month.
    # parameter:
    # bank_account_id: the account id to generate dashboard
    def dashboard(self, bank_account_id):
        res = self.capi.get('/transaction/{}'.format(bank_account_id))
        if res:
            odict = res.get_result()
            print(bcolors.OK + f"Get is successful with details: {type(odict)}" + bcolors.RESET)
        else:
            print(bcolors.FAIL + "Something went wrong, get returns null." + bcolors.RESET)
            quit()

        print(odict)
        transaction=json.loads(odict['value'].decode())
        print(transaction[self.getMonth()])

    # Audit generates a report for the entire bank, with a dashboard record for every customer.
    def audit(self):
        res=self.capi.get_members('/transaction/')
        print(res)
        # audit_result=sorted(self.transaction.items(),key=lambda x:self.account[x[0]].owner_name,reverse=False)
        # for item in audit_result:
        #     print(item)
        

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
res=B.new_account('111220','lhw','text_id_blanc','contact_info_blank','overdraft_limit','overdraft_intrRate',100)
B.transfer('111213', '111220',10)
B.withdraw('111213',10)
B.deposit('111220',10)
B.deposit('111220',10)
B.dashboard('111213')
B.audit()
