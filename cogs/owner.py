import discord, traceback, collections, pip, os, sys, asyncio, contextlib, subprocess, ast, dbl, aiohttp
from discord.ext import commands
from jishaku.codeblocks import codeblock_converter
from jishaku.exception_handling import ReplResponseReactor
from jishaku.functools import AsyncSender
from jishaku.flags import JISHAKU_RETAIN, SCOPE_PREFIX
from jishaku.paginators import PaginatorInterface, WrappedPaginator
from jishaku.repl import AsyncCodeExecutor, Scope, get_var_dict_from_ctx
ownerid = [576678817523826698, 546347626870603776]
CommandTask = collections.namedtuple("CommandTask", "index ctx task")


class OwnerCmd(commands.Cog, command_attrs=dict(hidden=True)):
    """FOR OWNER ONLY"""
    def __init__(self, bot):
        self.token = os.getenv("DBL_TOKEN")
        self.bot = bot
        self.dbl = dbl.DBLClient(self.bot, self.token ,autopost = True, webhook_path = "/dblwebhook", webhook_port = os.getenv("DBL_PORT"), webhook_auth = os.getenv("DBL_PASSWORD"))
        self.last_result = None
        self._scope = Scope()
        self.retain = JISHAKU_RETAIN
        self.tasks = collections.deque()
        self.task_count: int = 0
        
    @property
    def scope(self):

        if self.retain:
            return self._scope
        return Scope()
    
    @contextlib.contextmanager
    def submit(self, ctx: commands.Context):

        self.task_count += 1
        if sys.version_info < (3, 7, 0):
            cmdtask = CommandTask(self.task_count, ctx, asyncio.Task.current_task())  # pylint: disable=no-member
        else:
            try:
                current_task = asyncio.current_task()
            except RuntimeError:
                current_task = None

            cmdtask = CommandTask(self.task_count, ctx, current_task)

        self.tasks.append(cmdtask)

        try:
            yield cmdtask
        finally:
            if cmdtask in self.tasks:
                self.tasks.remove(cmdtask)


    @commands.command(name = 'serverlist', aliases = ['sl'], brief = "Servers the bot are in",help = """Shows the list of Servers the Bot is In.
Only for Bot Owner i.e. ServerBoys""", hidden = True)
    async def _serverlist(self, ctx):
        if ctx.author.id in ownerid:
            fullMsgLen = 0
            serverList = discord.Embed(title = f"{len(self.bot.guilds)} servers with {len(self.bot.users)}")
            for guild in self.bot.guilds:
                serverListmsg = f'**{guild}** (id = {guild.id}) with __{guild.member_count}__ members'
                msgLen = len(serverListmsg)
                fullMsgLen += msgLen
                serverList.add_field(name = f"{guild} with {guild.member_count} members",value= f'''**Role Count: **{len(guild.roles)} \n**Channel Count: **{len(guild.channels)}''' , inline = False)
                serverList.set_thumbnail(url=self.bot.user.avatar_url)
                if fullMsgLen >= 2000:
                    await ctx.send(embed = serverList)
                    serverList = discord.Embed(title = f"{len(client.guilds)} servers with {len(client.users)}")
                    fullMsgLen = 0
            await ctx.send(embed=serverList)
        else:
             await ctx.send("Owner Only Command")                
                
    @commands.command(hidden = True)
    async def install(self, ctx, package: str):
        if ctx.author.id in ownerid:
                proc = subprocess.run(f'pip install {package}', shell=True, capture_output = True)
                stee= proc.stdout.decode('utf-8')
                strr = proc.stderr.decode('utf-8')
                await ctx.send(f"""```
{stee}```
```
{strr}```""")
    
    @commands.command(hidden = True)
    async def shell(self, ctx, *, cmd: str):
        if ctx.author.id in ownerid:
                proc = subprocess.run(cmd, shell=True, capture_output = True)
                stee= proc.stdout.decode('utf-8')
                strr = proc.stderr.decode('utf-8').replace("ERROR", "- ERROR").replace("WARNING", "+ WARNING")
                if stee.strip() != "":
                    await ctx.send(f"""
```
{stee}```""")
                if strr.strip() != "":
                    await ctx.send(f"""
```diff
{strr}```""")
    
    @commands.command(name = 'unload', aliases = ['ulc', 'ulcog'], hidden = True)
    async def unload(self, ctx, extension):
        if ctx.author.id in ownerid:
            try:
                self.bot.unload_extension(f'cogs.{extension}')
                await ctx.send("Unloaded")
            except commands.errors.ExtensionNotLoaded:
                await ctx.send("Extenstion Not Loaded")

    @commands.command(name = 'node', aliases = ['ns'], hidden = True)
    async def node_state(self, ctx):
        if ctx.author.id in ownerid:
            async with aiohttp.ClientSession() as cs:
                async with cs.get("https://danbot.host/nodeStatus") as r:
                    diction = await r.json()
            embed = discord.Embed(title = "DanBot")
            for val in diction.keys():
                msg = ""
                for node in diction[val].keys():
                    msg += f"""{node} :  {diction[val][node]}
"""
                embed.add_field(name = f"__**{val.capitalize()}**__", value = f"**{msg}**", inline = False)
            await ctx.send(embed = embed)

            
    
    @commands.command(name = 'deletecog', aliases = ["dcog", "delc", "delcog"], hidden = True)
    async def deletecog(self, ctx, cogfile):
        if ctx.author.id in ownerid:
            try:
                os.remove(f"./cogs/{cogfile}.py")
                try:
                    self.bot.unload_extension(f"cogs.{cogfile}")
                except commands.error.ExtensionNotLoaded:
                    pass
                await ctx.send("Removed")
            except FileNotFoundError:
                await ctx.send("File Not Found")
    
    @commands.command(name = 'command', aliases = ["cmd"], help = 'name, command', hidden = True)
    async def _command(self, ctx, n: str, *, cmnd = ""):
        if ctx.author.id in ownerid:
            filen = n
            cogname = n.capitalize()
            filename = f"{filen}.py"
            for files in os.listdir("./cogs"):
                if files == filename:
                    with open(f"./cogs/{filename}", "r") as readcog:
                        cogSetRaw = readcog.read()
                        cogSetList = cogSetRaw.split("""
    """)
                        cogname = cogSetList[4].split(" ")[1]
                        cogname = cogname[:-15]
                        cogSet = """
    """.join(cogS for cogS in cogSetList[7:-3])
                    readcog.close()
                    break
                else:
                    cogSet = ""


            with open(f"./cogs/{filename}", "w+") as writecog:
                cmdList = cmnd.split("""
    """)
                comd = ''
                for commd in cmdList:
                    comd += f"""
        {commd}"""

                writecog.write(f"""#pylint:disable=W0312
import discord
from discord.ext import commands

class {cogname}(commands.Cog):
    def __init__(self, bot):
	    self.bot = bot
{cogSet}
{comd}

def setup(bot):
    bot.add_cog({cogname}(bot))""")
                await ctx.send("Operation Completed")

    @commands.command(name="eval", hidden = True)
    async def _eval(self, ctx: commands.Context, *, argument: codeblock_converter):
        """
        Direct evaluation of Python code.
        """
        if ctx.author.id in ownerid:

            arg_dict = get_var_dict_from_ctx(ctx, SCOPE_PREFIX)
            arg_dict["_"] = self.last_result

            scope = self.scope

            try:
                async with ReplResponseReactor(ctx.message):
                    with self.submit(ctx):
                        executor = AsyncCodeExecutor(argument.content, scope, arg_dict=arg_dict)
                        async for send, result in AsyncSender(executor):
                            if result is None:
                                continue

                            self.last_result = result

                            if isinstance(result, discord.File):
                                send(await ctx.send(file=result))
                            elif isinstance(result, discord.Embed):
                                send(await ctx.send(embed=result))
                            elif isinstance(result, PaginatorInterface):
                                send(await result.send_to(ctx))
                            else:
                                if not isinstance(result, str):
                                    # repr all non-strings
                                    result = repr(result)

                                if len(result) > 2000:
                                    # inconsistency here, results get wrapped in codeblocks when they are too large
                                    #  but don't if they're not. probably not that bad, but noting for later review
                                    paginator = WrappedPaginator(prefix='```py', suffix='```', max_size=1985)

                                    paginator.add_line(result)

                                    interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
                                    send(await interface.send_to(ctx))
                                else:
                                    if result.strip() == '':
                                        result = "\u200b"

                                    send(await ctx.send(result.replace(self.bot.http.token, "[token omitted]")))
            finally:
                scope.clear_intersection(arg_dict)
                
    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        guild = self.bot.get_guild(576680266010198016)
        channel = guild.get_channel(781036889980272710)
        userid = int(data["user"])
        user = await self.bot.fetch_user(userid)
        await channel.send(f"{user.name} has voted.")
        
    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        guild = self.bot.get_guild(576680266010198016)
        channel = guild.get_channel(781036889980272710)
        userid = int(data["user"])
        user = await self.bot.fetch_user(userid)
        await channel.send(f"Test: \n{user.name} has voted.")
                
def setup(bot):
    bot.add_cog(OwnerCmd(bot))