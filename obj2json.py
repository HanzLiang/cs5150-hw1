import json


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


class user:
    def __init__(self, name, pwd):
        self.name = name
        self.pwd = pwd

    def __str__(self):
        return 'user(' + self.name + ',' + self.pwd + ')'

# 重写JSONEncoder的default方法，object转换成dict


class userEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bankAccount):
            return {
                'bank_account_id': o.bank_account_id,
                'pwd': o.pwd,
                'bank_account_id': o.bank_account_id,
                'owner_name': o.owner_name,
                'tex_id': o.text_id,
                'contact_info': o.contact_info,
                'overdraft_limit': o.overdraft_limit,
                'overdraft_inter_rate': o.overdraft_intrRate,
                'balance': o.balance,
            }
        return json.JSONEncoder.default(o)

# 重写JSONDecoder的decode方法，dict转换成object


class userDecode(json.JSONDecoder):
    def decode(self, s):
        dic = super().decode(s)
        return user(dic['name'], dic['pwd'])

# 重写JSONDecoder的__init__方法，dict转换成object


class userDecode2(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=dic2objhook)


# 对象转换成dict
def obj2dict(obj):

    if (isinstance(obj, user)):
        return {
            'name': obj.name,
            'pwd': obj.pwd
        }
    else:
        return obj

# dict转换为对象


def dic2objhook(dic):

    if isinstance(dic, dict):
        return user(dic['name'], dic['pwd'])
    return dic


# 第一种方式，直接把对象先转换成dict
u = user('smith', '123456')
uobj = json.dumps(obj2dict(u))
print('uobj: ', uobj)


# 第二种方式，利用json.dumps的关键字参数default
u = user('smith', '123456')
uobj2 = json.dumps(u, default=obj2dict)
print('uobj2: ', uobj)

# 第三种方式，定义json的encode和decode子类，使用json.dumps的cls默认参数
user_encode_str = json.dumps(u, cls=userEncoder)
print('user2json: ', user_encode_str)

# json转换为object
u2 = json.loads(user_encode_str, cls=userDecode)
print('json2user: ', u2)

# 另一种json转换成object的方式
u3 = json.loads(user_encode_str, cls=userDecode2)
print('json2user2: ', u3)
