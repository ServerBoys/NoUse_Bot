from module.jsonl import JsonLoader
from discord.ext import commands
class Economy:
    def __init__(self, user_id):
        self.user_id=str(user_id)
        self.open_account()
        
    @property
    def economy(self):
        return JsonLoader("/home/container/jsonf/economy.json")
        
    def open_account(self):
        cont=self.economy.cont
        if cont.get(self.user_id, None) is None:
            cont[self.user_id]={"cash":0, "bank":0}
            self.economy.edit(cont)
        
    def get(self, info=None):
        if info is None:
            return self.economy.cont[self.user_id]
        else:
            return self.economy.cont[self.user_id][info]
        
    def edit(self, cash=0, bank=0):
        cont=self.economy.cont
        rcash, rbank=tuple(self.get().values())
        if cash<0 and rcash<-cash:
            raise CashCrisis
        if bank<0 and rbank<-bank:
            raise BankCrisis
        cont[self.user_id]={
                'cash':rcash+cash,
                'bank':rbank+bank
        }
        self.economy.edit(cont)

def Excption(message):
    class E(Exception):
        def __init__(self):
            super().__init__(message)
    return E
       
BankCrisis=Excption("Bank Crisis")
CashCrisis=Excption("Cash Crisis")
class AmountNotNumeric(Exception):
    def __init__(self):
        super().__init__("Amount Not Numeric")

def AmtCnv(_type):
    class AmountConverter(commands.Converter):
        
        async def convert(self, ctx, amount):
            if amount in ("all", "max"):
                eco=Economy(ctx.author.id)
                amount=eco.get(_type)
            elif not amount.isnumeric():
                await ctx.send("You need to enter valid amount")
                return False
            return int(amount)
    return AmountConverter
        
BAmountConverter=AmtCnv('bank')
CAmountConverter=AmtCnv('cash')
