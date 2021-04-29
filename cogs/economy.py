#pylint:disable=W0312
import discord
from discord.ext import commands
from module.economy_c import Economy as Eco, BankCrisis, CashCrisis, BAmountConverter, CAmountConverter
import random
class Economy(commands.Cog):
    def __init__(self, bot):
	    self.bot = bot

    @commands.command(name="balance", aliases=["bal","wallet"])
    async def balance(self, ctx, user: discord.Member = None):
        if user is None:
            user=ctx.author
            
        user_economy=Eco(user.id)
        embed=discord.Embed(title=f"Wallet of {user.name}")
        embed.add_field(name="Cash", value=user_economy.get("cash"), inline=False)
        embed.add_field(name="Bank", value=user_economy.get("bank"), inline=False)
        embed.add_field(name="Total", value=user_economy.get("cash")+user_economy.get("bank"), inline=False)
        await ctx.send(embed=embed)
        
    @commands.command(name="beg")
    async def beg(self, ctx):
        win_lose= random.choice((True, False))
        if win_lose:
            coin=random.randrange(20, 50)
            user_economy=Eco(ctx.author.id)
            user_economy.edit(cash=coin)
            message=f"Someone donated you {coin} coins"
        else:
            message="Sad! Noone wants to donate you!"
        await ctx.reply(message, mention_author=False)
        
    @commands.command(name="withdraw", aliases=["with"])
    async def withdraw(self, ctx, amount: BAmountConverter):
        if amount is False:
            return
        user_eco=Eco(ctx.author.id)
        try:
            user_eco.edit(bank=-amount, cash=amount)
        except BankCrisis:
            return await ctx.send(f"You have only {user_eco.get('bank')} coins to withdraw.")
        await ctx.send(f"{amount} coins have been withdrawn")

    @commands.command(name="deposit", aliases=["dep"])
    async def deposit(self, ctx, amount: CAmountConverter):
        if amount is False:
            return
        user_eco=Eco(ctx.author.id)
        try:
            user_eco.edit(bank=amount, cash=-amount)
        except CashCrisis:
            return await ctx.send(f"You have only {user_eco.get('cash')} coins to deposit.")
        await ctx.send(f"{amount} coins have been deposited")
        
    @commands.command(name='bet')
    async def bet(self, ctx, amount: CAmountConverter):
        if amount is False:
            return
        user_eco=Eco(ctx.author.id)
        try:
            user_eco.edit(cash=-amount)
        except CashCrisis:
            return await ctx.send(f"You have only {user_eco.get('cash')} coins to bet.")
        win=random.choice((True, True, True, True, False, False, False, False, False))
        if win:
            percent=random.randrange(40, 100)
            amt=round(percent/100*amount)
            user_eco.edit(cash=amount+amt)
            title="You Won"
            description=f'You won {amt} coins. ({percent}%)'
            
        else:
            title='You Lost'
            description=f'You lost {amount} coins.'
        description+=f'\nYou now have {user_eco.get("cash")} coins in your wallet'
        await ctx.send(embed=discord.Embed(title=title, description=description))
            
def setup(bot):
    bot.add_cog(Economy(bot))