import discord
from discord.ext import commands, ipc
from discord_slash import SlashCommand
import asyncio, inspect, json, datetime, sqlite3, os, time
intents = discord.Intents.all()
from module.convert import convert
from module.pingc import ping
import threading
from dotenv import load_dotenv
load_dotenv()
db = sqlite3.connect("data.sqlite")
cursor = db.cursor()
from pretty_help import PrettyHelp
serverid = 576678817523826698
default_prefixes = ['! ', '!' , "<@748422859042324540> ", "<@!748422859042324540> "]

def shell_cmd():
    while True:
        cmd=input("")
        print(os.system(cmd))

        
T1=threading.Thread(target=shell_cmd)
T1.start()

async def determine_prefix(bot, message):
    with open("prefixes.json", "r") as prefile:
        custom_prefixes = json.load(prefile)
    prefile.close()
    guild = message.guild
    if guild:
        return custom_prefixes.get(str(guild.id) , default_prefixes)
    else:
        return default_prefixes

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ipc = ipc.Server(self, host=os.getenv("IPC_HOST"), port=os.getenv("IPC_PORT"), secret_key=os.getenv("IPC_PASSWORD"))
        self.ipc.start()

    def ipc_start(self):
        try:
            self.ipc.start()
        except OSError:
            time.sleep(10)
            print("Retrying")
            self.ipc_start()

    async def on_ipc_ready(self):
        print("Ipc is ready.")

    async def on_ipc_error(self, endpoint, error):
        print(endpoint, "raised", error)
    
bot = Bot(command_prefix = determine_prefix, intents = intents, case_insensitive = True, help_command=PrettyHelp(color = 0x00ff00))
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    cursor.execute("""SELECT * FROM start""")
    values = cursor.fetchall()
    channelid, guildid = values[-1]
    if len(values) > 1:
        cursor.execute("""
        DELETE FROM start
        WHERE NOT channel_id = 778224961026260992
        OR NOT guild_id = 576680266010198016
        """)
        db.commit()
    channel = bot.get_guild(guildid).get_channel(channelid)
    await channel.send(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(
        name = f"Watching {len(bot.guilds)} Servers but Doing Nothing",
        type = discord.ActivityType.watching,
        state = "Watching",
        details = "Worst Bot in History",
        status = discord.Status.dnd
    )
    
@bot.command(pass_context=True, hidden = True)
async def reopen(ctx):
    if ctx.author.id == serverid:
        await ctx.send('Closing')
        if ctx.channel.id != 778224961026260992 or ctx.guild.id != 576680266010198016:
            cursor.execute("""
            INSERT INTO start(channel_id, guild_id)
            VALUES (?,?)
            """, (ctx.channel.id, ctx.guild.id))
            db.commit()
        await bot.close()
        os.system("python bot1.py")
    

for file in os.listdir('./cogs'):
	if file.endswith('.py'):
		bot.load_extension(f'cogs.{file[:-3]}')


@bot.command(name = 'reload', aliases = ["rl", "load"], hidden = True)
async def reload(ctx, extension):
    if ctx.author.id == serverid:
        try:
            try:
                bot.unload_extension(f'cogs.{extension}')
            except commands.errors.ExtensionNotLoaded:
                pass
            bot.load_extension(f'cogs.{extension}')
            await ctx.send("Reloaded")
        except commands.errors.ExtensionNotFound:
            await ctx.send("No Such Extension Found")

@bot.event
async def on_message(message):
    msg_channel: discord.TextChannel = message.channel
    await bot.process_commands(message)
    if not message.author.bot:
        if message.guild is not None:
            if not os.path.exists(f"./cogs/afklist/{message.guild.id}.json"):
                with open(f"./cogs/afklist/{message.guild.id}.json", "w") as cfile:
                    json.dump({}, cfile)
                cfile.close()
            with open(f"./cogs/afklist/{message.guild.id}.json" , "r") as afkpeepf:
                afkpeepdict = json.load(afkpeepf)
            afkpeepf.close()
            for afkpeepid in afkpeepdict.keys():
                deltat = int(datetime.datetime.now().timestamp())- int(afkpeepdict[str(afkpeepid)][2])
                if deltat <= 20:
                    pass
                elif int(afkpeepid) == message.author.id:
                    try:
                        await message.author.edit(nick = "")
                    except discord.errors.Forbidden:
                        pass
                    with open(f'./cogs/afklist/{message.guild.id}.json', 'r') as afkfil:
                        afkpeoplelist = json.load(afkfil)
                        messg = ""

                        for pings in afkpeoplelist[str(message.author.id)][3:]:
                            messg += pings + " \n"
                        if messg == "":
                            messg += "No Pings!"
                        else:
                            pass
                        embed_dm = discord.Embed(title = 'Pings!', description = messg, color = message.author.colour)
                        with open("./cogs/afklist/nodms.json", "r") as dmf:
                            dmbool = json.load(dmf)
                        dmf.close()
                        if not dmbool.get(str(message.author.id), True):
                            pass
                        else:
                            try:
                                await message.author.send(embed = embed_dm)
                            except discord.errors.Forbidden:
                                pass
                    afkfil.close()
                    with open(f'./cogs/afklist/{message.guild.id}.json', "w") as afkfil:
                        await message.channel.send(f"{message.author.mention} , You are now removed from AFK. You were AFK for {convert(deltat)}.")
                        afkpeoplelist.pop(str(message.author.id))
                        json.dump(afkpeoplelist, afkfil, indent = 4)
                    afkfil.close()


                elif f"<@{int(afkpeepid)}>" in message.content.strip() or f"<@!{int(afkpeepid)}>" in message.content.strip():
                    if int(message.guild.id) == int(afkpeepdict[str(afkpeepid)][1]):
                        await msg_channel.send(f"{discord.utils.get(message.guild.members, id = int(afkpeepid)).name} is AFK : {afkpeepdict[str(afkpeepid)][0]} for {convert(deltat)}")
                        argslist = message.content.split(" ")
                        mesage = ""
                        for arg in argslist:
                            if arg[0] == ":" and arg[-1] == ":":
                                emojiname = arg.strip(":")
                                emoji = discord.utils.get(bot.emojis, name= emojiname)
                                if emoji == None:
                                    mesage += arg + " "
                                else:
                                    mesage += str(emoji) + " "
                            elif arg == "@everyone" or arg == "@here":
                                mesage += f"``{arg}`` "
                            elif "<@" in arg.strip() and ">" in arg.strip():
                                mesage += str(ping(arg, message.guild.roles, message.guild.members)) + " "
                            else:
                                mesage += arg + " "
                        with open(f"./cogs/afklist/{message.guild.id}.json", "r") as afkfile:
                            afklistdict = json.load(afkfile)
                        afkfile.close()
                        with open(f"./cogs/afklist/{message.guild.id}.json", "w") as afkfile:
                            listafk = afklistdict[str(afkpeepid)]
                            listafk.append(f"[{message.author.name} : {mesage}](http://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id})")
                            afklistdict[str(afkpeepid)] = listafk
                            json.dump(afklistdict, afkfile, indent = 4)
                        afkfile.close()
        
bot.run(os.getenv('TOKEN'))