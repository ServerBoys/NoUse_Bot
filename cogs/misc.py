#pylint:disable=W0312
import discord
from PyDictionary import PyDictionary
from discord.ext import commands, tasks
from module.pingc import ping
from module.convert import seconvert, convert, ColorConvertor, NotInHex
from module.jsonl import JsonLoader
import asyncio, io, random, datetime, calendar, os, json
from PIL import Image, ImageFont, ImageDraw
from typing import Optional

class Misc(commands.Cog):
    """
Miscellaneous commands to help you!\
    """
    def __init__(self, bot):
        self.bot = bot
        self.rm_loop.start()
    
    def cog_unload(self):
        self.rm_loop.cancel()
    
    @tasks.loop(seconds = 10)
    async def rm_loop(self):
        jld = JsonLoader("./jsonf/reminder.json")
        rm_dict = jld.cont
        d = {}
        if len(rm_dict.keys()) == 0:
            pass
        else:
            for keys in rm_dict.keys():
                d[keys] = rm_dict[keys]
            for keys in rm_dict.keys():
                guild = await self.bot.fetch_guild(rm_dict[keys][3])
                user = await guild.fetch_member(int(keys))
                time = int(datetime.datetime.now().timestamp())
                if rm_dict[keys][0] <= time:
                    await user.send(f"""You asked to remind me. I reminded you in {convert(time- rm_dict[keys][0]+ rm_dict[keys][2])}
Reason: {rm_dict[keys][1]}""")
                    d.pop(keys)
                    jld.edit(d)
    
    @commands.group(name = 'afk', brief = "Makes you AFK", help = "Makes you AFK \nWorks! 👍" ,pass_content = True, invoke_without_command = True)
    @commands.guild_only()
    async def _afk(self, ctx, *, reason: str = "None"):
        if not os.path.exists(f"./cogs/afklist/{ctx.guild.id}.json"):
            async with open(f"./cogs/afklist/{ctx.guild.id}.json", "w") as cfile:
                json.dump({}, cfile)
            cfile.close()
        with open(f'./cogs/afklist/{ctx.guild.id}.json', 'r') as afkfile:
            afkpeoplelist = json.load(afkfile)
        afkfile.close()
        if str(ctx.author.id) in afkpeoplelist.keys():
            await ctx.send("You are already AFK.")
            return
        else:
            try:
                await ctx.author.edit(nick = f"[AFK]{ctx.author.name}")
            except discord.errors.Forbidden:
                pass
            await ctx.send(ctx.author.mention + " , You are AFK now. Reason: "+ reason)
            with open(f'./cogs/afklist/{ctx.guild.id}.json', "w") as afkfile:
                afkpeoplelist[str(ctx.author.id)] = [reason , ctx.guild.id, int(datetime.datetime.now().timestamp())]
                await asyncio.sleep(10)
                json.dump(afkpeoplelist, afkfile, indent = 4)
            afkfile.close()
            
    @_afk.command(name = 'dm', brief = "Turn DM on/off for AFK command.", help = """Turn Your DM for AFK command:
ON or OFF""")
    @commands.guild_only()
    async def _dmafk(self, ctx, toggle: Optional[str] = None):
        file = JsonLoader("./cogs/afklist/nodms.json")
        afk = file.cont
        on_off = {"on": True,
                 "off": False}
        if toggle in on_off.keys():
            if afk.get(str(ctx.author.id), True) == on_off[toggle]:
                return await ctx.send(f"**{ctx.author.name}**, Your DM is already set to {toggle}.")
            afk[str(ctx.author.id)] = on_off[toggle]
            file.edit(afk)
            return await ctx.send(f"**{ctx.author.name}**, DM for AFK command set to {toggle}.")
        for name, value in on_off.items():
            if afk.get(str(ctx.author.id), True) == value:
                return await ctx.send(f"**{ctx.author.name}**, Your DM for AFK command is currently {name}.")
    
    @commands.command(name = 'ping', brief = 'Ping of Bot', help = 'Ping/Latency of bot')
    @commands.guild_only()
    async def ping(self, ctx):
        await ctx.send(f"""**Pong!**
```
Latency: {round(self.bot.latency*1000)}ms
```""")
    
    @commands.command(name = 'calendar', brief = 'Shows Calendar', help ='Shows Calendar for specific month in specific year')
    @commands.guild_only()
    async def calendar(self, ctx, month: Optional[int]=datetime.datetime.now().month, year: Optional[int]=datetime.datetime.now().year):
        import time
        t=time.time()
        if month > 12:
            return await ctx.send("Months cannot be greater than 12")
        if len(str(year)) == 2:
            year = (datetime.datetime.now().year//100)*100 + year
        a = calendar.TextCalendar(calendar.SATURDAY)
        text = a.formatmonth(year, month)
        
        text = text.split("Fr")
        text1 = text[0].replace("Th", "Thu")+ "Fri"
        text11 = text1.splitlines()
        text1 = text1.replace(text11[0], text11[0].replace(" ", "  "))
        text2 =text[1].replace(" ", "  ")
        text3 = text1 + text2
        img = Image.open("./c.jpg")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 85)
        draw.text((20, 0), text3, (255, 255, 255), font = font)
        
        with io.BytesIO() as image_binary:
            img.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.send(file=discord.File(fp=image_binary, filename='image.png'))
            print(time.time()-t)
        
    @commands.command(name = "remind", aliases = ["rm"], brief = 'Reminds you in time', help = 'Remind yourself about Something')
    @commands.guild_only()
    async def _remind(self, ctx, *, time):
        timeL = time.split(" ")
        hours = 0
        minutes = 0
        seconds = 0
        for times in timeL:
            if times[-1] == "h" and hours == 0:
                hours = int(times[:-1])
            elif times[-1] == "m" and minutes == 0:
                minutes = int(times[:-1])
            elif times[-1] == "s" and seconds == 0:
                seconds = int(times[:-1])
            elif times.isalnum and hours == minutes == seconds == 0:
                seconds = int(times)
                index = timeL.index(times) +1
                break
            else:
                index = timeL.index(times)
                break
                
        reason = ""
        try:
            for words in timeL[index:]:
                reason += words + " "
        except NameError:
            reason += "None"
        if reason == "" or reason == " ":
            reason = "None"
        total_sec = seconvert(hours, minutes, seconds)
        if total_sec == 0:
            return await ctx.send("You cant get reminded in 0s.")
        elif total_sec <0:
            return
        elif total_sec < 30:
            return await ctx.send("You can't add reminder in time less than 30s.")
        time_now = int(datetime.datetime.now().timestamp())
        jload = JsonLoader("./jsonf/reminder.json")
        remDict = jload.cont
        remDict[str(ctx.author.id)] = [time_now + int(total_sec), reason, total_sec, ctx.guild.id]
        await ctx.send(f"""I have set your reminder for {convert(total_sec)}.
Reason: {reason}""")
        jload.edit(remDict)
                
    
    
    @commands.command(name = 'message', aliases = ['say'], brief = 'Says Your Message' , help = 'Sends Your Message as Webhook')
    @commands.guild_only()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def _message(self ,ctx , *, args):
        message = ""
        argslist = args.split(" ")
        for arg in argslist:
            if arg[0] == ":" and arg[-1] == ":":
                emojiname = arg.strip(":")
                emoji = discord.utils.get(self.bot.emojis, name= emojiname)
                if emoji == None:
                    message += arg + " "
                else:
                    message += str(emoji) + " "
            elif arg == "@everyone" or arg == "@here":
                message += f"``{arg}`` "
            elif "<@" in arg.strip() and ">" in arg.strip():
                message += str(ping(arg, ctx.guild.roles, ctx.guild.members)) + " "
            else:
                message += arg + " "
        web=await ctx.channel.create_webhook(name=ctx.author.name)
        await ctx.message.delete()
        await web.send(content = message, avatar_url = ctx.author.avatar_url)
        await web.delete()
        
    @_message.error
    async def msgerror(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("You cannot just spam that command")

    @commands.command(name = "choose", brief = 'Make Bot choose a choice', help = 'Make Bot choose between anything')
    @commands.guild_only()
    async def choose(self, ctx, *, choices: str):
        choicelist = choices.split(",")
        choiceindex = 0
        list2 = []
        for choice in choicelist:
            list2.append(choice.strip())
        await ctx.send(content = f"I choose **{random.choice(list2)}**.")       
        
    @commands.command(name="userinfo", brief = "Info. about a user", help = 'Information about user', aliases = ["ui"])
    @commands.guild_only()
    async def userinfo(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(
            color=member.colour,
            timestamp=ctx.message.created_at,
            description=member.mention
        )

        embed.set_author(name=f"{member} Info", icon_url = member.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        embed.add_field(name="ID:", value=member.id, inline=False)
        embed.add_field(
            name="Registered At:",
            value=member.created_at.strftime("%a, %d %b %Y %I:%M %p"),
            inline=False
        )
        embed.add_field(
            name="Joined Server At:",
            value=member.joined_at.strftime("%a, %d %b %Y %I:%M %p"),
            inline=False
        )
        val = ' '.join(role.mention for role in member.roles if not role == ctx.guild.default_role)
        if val == "":
            val = "None"

        embed.add_field(
            name=f"{len(member.roles)-1} Roles",
            value= val,
            inline=False
        )
        pins = {
            "staff": [764397851987017728, "Discord Staff"],
            "partner": [764392787600343070, "Discord Partner"],
            "early_supporter": [764392787344621599, "Early Supporter"],
            "bug_hunter": [764392787058884619, "Bug Hunter"],
            "bug_hunter_level_2": [764392787424051200, "Bug Hunter 2"],
            "early_verified_bot_developer": [764392787378307113, "Early Verified Bot Developer"],
            "verified_bot": [764398186697457686, "Verified Bot"],
            "hypesquad": [764397851819507712, "Hypesquad"],
            "hypesquad_bravery": [764392787222200320, "Hypesquad Bravery"],
            "hypesquad_brilliance": [764392787424313344, "Hypesquad Brilliance"],
            "hypesquad_balance": [764392787017465897, "Hypesquad Balance"]
        }
        badges = " ".join(f"{self.bot.get_emoji(pins[flags[0]][0])} {pins[flags[0]][1]}" for flags in list(member.public_flags) if flags[1])
        if badges == "":
            badges = "None"
        embed.add_field(name="Badges", value= f"**{badges}**")
        embed.add_field(name="Bot?", value=member.bot)

        await ctx.send(embed=embed)
        
        
    @commands.command(name = 'embed', brief = 'Embeds Your Message', help = 'Embed the message to send')
    @commands.guild_only()
    async def embed(self, ctx, emcolor :ColorConvertor = 0):
        def checking(m):
            return m.channel == ctx.channel and m.author == ctx.author
        errorEmbed = discord.Embed(title = "TimeOut", description = "You have crossed the 30 seconds time limit. Try again.", color = 0xff0000)

        try:
            titlesend = await ctx.send("**`Send the title of embeds please`**")
            tit= await self.bot.wait_for('message', check = checking, timeout = 30)
            await tit.delete()
            await titlesend.delete()
        except asyncio.TimeoutError:
            return await ctx.send(embed = errorEmbed)

        descsend = await ctx.send("**`Please send the description`**")
        try:
            desc = await self.bot.wait_for('message', check = checking, timeout = 30)
            await desc.delete()
            await descsend.delete()
        except asyncio.TimeoutError:
            return await ctx.send(embed = errorEmbed)

        footsend = await ctx.send("**`Please send the footer`**")
        try:
            foot = await self.bot.wait_for('message', check = checking, timeout = 30)
            await foot.delete()
            await footsend.delete()
        except asyncio.TimeoutError:
            return await ctx.send(embed = errorEmbed)
        embedVar = discord.Embed(title = tit.content, 
                                    description=desc.content,
                                    color = emcolor)
        embedVar.set_footer(text = foot.content)
        await ctx.send(embed = embedVar)
    @embed.error
    async def embed_error(self, ctx, error):
        if isinstance(error, commands.errors.ConversionError):
            await ctx.send("Color Not Found")
        
        
    @commands.command(name="serverinfo", aliases = ["si"], brief = "Info of Server", help = "Info about server you are in")
    @commands.guild_only()
    async def _serverinfo(self, ctx):
        gname = ctx.guild.name
        description = ctx.guild.description
        owner = ctx.guild.owner.mention
        guild_id = ctx.guild.id
        region = ctx.guild.region
        member_count = ctx.guild.member_count
        icon = ctx.guild.icon_url

        embed = discord.Embed(
            title=f"{gname}'s Information",
            description=description,
            color= 0x00ffff,
            timestamp = ctx.message.created_at
            )
        embed.set_thumbnail(url=icon)
        embed.set_footer(text = f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Owner:", value=owner, inline=False)
        embed.add_field(name="Server ID:", value=guild_id, inline=False)
        embed.add_field(name="Region:", value=region, inline=False)
        embed.add_field(name="Member Count:", value=member_count, inline=False)
        embed.add_field(name = "Created At: ",value = ctx.guild.created_at.strftime("%a, %d %b %Y %I:%M %p"),inline = False)

        await ctx.send(embed=embed)
    

def setup(bot):
    bot.add_cog(Misc(bot))