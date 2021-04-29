#pylint:disable=W0312
import discord
from discord.ext import commands

class Support(commands.Cog):
    """
Support the Bot\
    """
    def __init__(self, bot):
	    self.bot = bot

    @commands.command(name = "suggest", aliases = ["suggestion"], help = 'Suggest Anything you want the Bot Devs to add.', brief = 'Suggest the Bot Devs')
    @commands.guild_only()
    async def _suggest(self, ctx, *, suggestion):
        guild = self.bot.get_guild(576680266010198016)
        channel = guild.get_channel(778892224363757588)
        embed = discord.Embed(
            title = f"{ctx.author.name}, {ctx.guild.name}",
            description = f"""**Suggestion**:

{suggestion}""")
        await ctx.send(f"Thank you! **{ctx.author}** for your suggestion! We will surely review it and add it if its meaningful and possible for me. Really **Thanks** from the CPU😂.")
        await channel.send(embed = embed)
        
    @commands.command(name = "vote", brief = "Vote this bot.", help = "Vote the bot to support us.")
    @commands.guild_only()
    async def vote(self, ctx):
        embed = discord.Embed(title = "Vote Us using link below:", description = " => [top.gg](https://top.gg/bot/748422859042324540/vote)")
        embed.set_footer(text = f"Requested by {ctx.author.name}", icon_url = ctx.author.avatar_url)
        await ctx.send(embed = embed)
        
    @commands.command(name = 'invite', brief = "Invite the bot to server.", help = "Sends You a link for Inviting Bot.")
    async def invite(self, ctx):
        inv_embed = discord.Embed(title = "Invite Links", description = """**Click a link below:**
  [Admin Perms](https://discord.com/api/oauth2/authorize?client_id=748422859042324540&permissions=8&scope=bot)
  [Limited Perms (Recommended)](https://discord.com/api/oauth2/authorize?client_id=748422859042324540&permissions=2080762998&scope=bot)
**Invite The Worst Bot in the History.**""", color = ctx.author.color)
        inv_embed.set_footer(text = f"Requested by {ctx.author}")
        
        await ctx.send(embed = inv_embed) 

def setup(bot):
    bot.add_cog(Support(bot))