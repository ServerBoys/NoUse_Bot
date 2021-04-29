import discord
import json
import os
import datetime
from discord.ext import commands 
from discord.ext import tasks
from module.jsonl import JsonLoader
from module.calc_class import Lexer
from PyDictionary import PyDictionary
lexer=Lexer()
class Utility(commands.Cog):
    """
    Utility Tools for you.\
    """
    def __init__(self, bot):
        self.bot = bot
   #     self.snipe_file_loop.start()

  #  def cog_unload(self):
   #     self.snipe_file_loop.cancel()
 #   @tasks.loop(seconds = 60)
#    async def snipe_file_loop(self):
#        print(os.listdir("./jsonf/snipes"))
   #     for files in os.listdir("./jsonf/snipes"):
   #         print(files== "1.json")
         #   if not str(files) == "1.json":
        #        file = JsonLoader(f"./json/snipes/{str(files)}")
         #       deleted = file.cont
         #       del2 = deleted.copy()
          #      for channels, items in deleted.items():
          #          print(channels,": ", items) 
          #          time = int(datetime.datetime.now().timestamp())
           #         if time > items["time"]+ 420:
           #             del2.pop(channels)
           #             if len(del2) == 0:
             #               os.remove(f"/json/snipes/{str(files)}")
            #            else:
             #               file.edit(del2)

    @commands.command(name = "snipe", help = "Gets last deleted message", brief = "Snipes last deleted message")
    async def snipe(self, ctx):
        channel = ctx.channel.id
        guild = ctx.guild.id
        if not os.path.isfile(f"./jsonf/snipes/{guild}.json"):
            return await ctx.send(embed = discord.Embed(title = "No Snipes", description= "Couldn't snipe anything"))
        file = JsonLoader(f"./jsonf/snipes/{guild}.json")
        snipes = file.cont
        deleted = snipes.get(str(channel), None)
        if deleted is None:
            return await ctx.send(embed = discord.Embed(title = "No Snipes", description= "Couldn't snipe anything"))
        message = deleted["message"]
        user = deleted["user"]
        av = deleted["av"]
        embed = discord.Embed(
            description = message,
            image_url = av,
            color = ctx.author.color
        )
        embed.set_author(name = user, icon_url = av)
        embed.set_footer(text = f"Requested by {ctx.author}")
        await ctx.send(embed = embed)
        
    @commands.command(name = "poll", brief = 'Create Poll', help = '''Create Poll.
Minimum 2 poll choices are needed.''')
    @commands.guild_only()
    async def poll(self, ctx, *, polls):
        polls = polls.lstrip(" ").rstrip(" ")
        pollList = polls.split(",")
        if len(pollList) < 2:
            return await ctx.send("Polls cant be less than 2")
        if len(pollList) == 2:
            pollList.insert(0, f"Poll By {ctx.author.name}")
        pollT = pollList[0].lstrip(" ").rstrip(" ").lstrip("""
""").rstrip("""
""")
        if pollT == "" or pollT == ",":
            pollT = f'Pole By {ctx.author.name}'
        purePoll = []
        for pol in pollList[1:]:
            pol = pol.lstrip(" ").rstrip(" ").lstrip("""
""").rstrip("""
""")
            if pol == "":
                pass
            else:
                purePoll.append(pol)
        if len(purePoll) < 2:
            return await ctx.send("Polls can't be less than 2")
        if len(purePoll) > 9:
            return await ctx.send("Polls can't be more that 9")
        i = 1
        poll_msg = ""
        for pol in purePoll:
            poll_msg += f"{i}.  {pol}\n"
            i += 1
        embed = discord.Embed(title = pollT,
                              description = poll_msg,
                              color = discord.Color.orange())
        embed.set_footer(text = f"By: {ctx.author.name}")
        msg = await ctx.send(embed = embed)
        ntt = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", '8️⃣', "9️⃣"]
        for emoji in ntt[:len(purePoll)]:
            await msg.add_reaction(emoji)

    @commands.command(name = 'meaning', aliases = ["dictionary"], brief = "Meaning of a word", help = 'Searches you the meaning of the word')
    @commands.guild_only()
    async def meaning(self, ctx, word: str):
        dic = PyDictionary()
        try:
            dicword = dic.meaning(word, False)
            dicem = discord.Embed(title = word, color = ctx.author.color)
            for dickey in dicword.keys():
                dicem.add_field(name = dickey, value = "".join([dicmeaning+ "\n" for dicmeaning in dicword[dickey]]), inline = False)
        except Exception:
            dicem = discord.Embed(title = "Word Not Found", description = f"{word} cannot be found")
        dicem.set_footer(text = f"Requested by {ctx.author}")
        await ctx.send(embed = dicem)
    
    @commands.command(name="calculate", aliases=["calc"], help='Calcuate Math Problems', brief = 'Calculator for Maths')
    async def calc(self, ctx, *, exp):
        print(exp)
        try:
            ans=lexer.parse(exp)
        except:
            return await ctx.reply("Sorry, I can't understand that.")
        embed=discord.Embed(title=f"Question: {exp}", description=f"Ans: {ans}")
        await ctx.reply(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            try:
                ans=lexer.parse(message.content)
                if ans is not None:
                    await message.channel.send(embed=discord.Embed(title=f"Question: {message.content}", description=f"Answer: {ans}"))
            except:
                pass
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        user = message.author
        channel = message.channel.id
        guild = message.guild.id
        time = int(datetime.datetime.now().timestamp())
        if not os.path.isfile(f"./jsonf/snipes/{guild}.json"):
            with open(f"./jsonf/snipes/{guild}.json", "w+") as f:
                json.dump({}, f)
            f.close()
        file = JsonLoader(f"./jsonf/snipes/{guild}.json")
        snipes = file.cont
        snipes[str(channel)] = {
            "time": time,
            "message": message.content,
            "user": str(user),
            "av": str(user.avatar_url)
        }                      
        file.edit(snipes)

def setup(bot):
    bot.add_cog(Utility(bot))