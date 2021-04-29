#pylint:disable=W0312
import discord
from discord.ext import commands
from module.economy_c import AmountNotNumeric
class ErrorHandler(commands.Cog):
    def __init__(self, bot):
	    self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            params = []
            for key, value in ctx.command.params.items():
                if key not in ("self", "ctx"):
                    params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")
            params = " ".join(params)
            error_name = str(error.param)
            prefix = str(ctx.prefix).rstrip(" ")
            if prefix == str(self.bot.user.mention):
                prefix = f"@{self.bot.user.name} "
            err = error_name
            if ":" in error_name:
                errNameList = error_name.split(":")
                err = errNameList[0].rstrip(" ")
                conv = errNameList[1].lstrip(' ')
                if '.' in conv:
                    c_list = conv.split(".")
                    conv = c_list[-1]
                error_name = f'{err}[{conv}]'
            invoker = f"{prefix}{ctx.invoked_with} {params}"
            err_index = invoker.index(f"<{err}>")
            invokerror = " " * len(invoker[:err_index +1]) + "^" * len(err)
            embed = discord.Embed(title = "Argument Missing!!", description = f"""**```
   {invoker}
   {invokerror}```**
**{err} is an argument that is missing**""")
            await ctx.send(embed = embed)
        elif isinstance(error, commands.errors.MemberNotFound):
            await ctx.send(f"Member **{error.argument}** is not found.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"Bot is missing **{error.missing_perms[0]}** Permission to use {ctx.invoked_with}.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"You need **{error.missing_perms[0]}** to run this command.")
        elif isinstance(error, commands.errors.CommandInvokeError):
            try:
                await ctx.send(error.original.text)
            except AttributeError:
                raise error
        elif isinstance(error, commands.errors.CommandNotFound):
            pass
        elif isinstance(error, AmountNotNumeric):
            await ctx.send("You need to enter a valid amount")
        else:
            raise error
                
    

def setup(bot):
    bot.add_cog(ErrorHandler(bot))