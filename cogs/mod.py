#pylint:disable=W0312
import discord
from discord.ext import commands
import json, asyncio
from module.jsonl import JsonLoader
from typing import Union, Optional
class Mod(commands.Cog):
    """
Mod Commands for moderators\
    """
    def __init__(self, bot):
	    self.bot = bot

    @commands.group(name = "prefix", help = 'Prefix Commands to add and remove', brief = 'Prefix Commands [add, remove]', invoke_without_command = True)
    @commands.guild_only()
    async def prefix(self, ctx):
        file = JsonLoader("prefixes.json")
        prefixes = file.cont.get(str(ctx.guild.id), ["**Default: **", self.bot.user.mention, "!"])
        pure_prefixes = []
        embed = discord.Embed(title = f"Prefixes ({ctx.guild.name})")
        embed.description = "```\n"
        for pure in prefixes:
            purest = pure.rstrip(" ")
            if purest == "<@!748422859042324540>":
                pass
            elif purest == f"<@{self.bot.user.id}>":
                pure_prefixes.append(f"@{self.bot.user.name}")
            elif not purest in pure_prefixes:
                pure_prefixes.append(purest)
        index = 1
        for p in pure_prefixes:
            embed.description += f"{index}. {p}\n"
            index += 1
        embed.description += "```"
        return await ctx.send(embed = embed)
    
    @prefix.command(name = 'remove', aliases = ["del", "delete"], brief = "Removes prefix for Guild", help = "Remove unwanted prefixes from on Server")
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True, )
    async def pref_remove(self, ctx, prefixes):
        prefixes = prefixes.lstrip(" ").rstrip(" ")
        pref = JsonLoader("prefixes.json")
        pref_dict = pref.cont
        prefix = pref.cont.get(str(ctx.guild.id), None)
        if prefix is None:
            return await ctx.send("No prefixes Added to This Server")
        elif prefixes == "<@748422859042324540>" or prefixes == "<@!748422859042324540>":
            return await ctx.send("You cannot remove mentions as prefix. Sorry")
        elif not prefixes in prefix:
            return await ctx.send("No prefixes in server called " + prefixes)
        elif prefixes in prefix:
            prefix.remove(f"{prefixes} ")
            prefix.remove(prefixes)
            pref_dict[str(ctx.guild.id)] = prefix
            pref.edit(pref_dict)
            await ctx.send(f"**{prefixes}** has been removed from prefixes")
    @pref_remove.error
    async def premove_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"You are missing Admin permission...")
            
    
    @prefix.command(name = "add", aliases = ["set"], help = "Adds the prefix to the bot for Server", brief = 'Add the prefix for server')
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def setprefix(self, ctx, prefixes):
        prefixes = prefixes.lstrip(" ").rstrip(" ")
        f = JsonLoader("prefixes.json")
        custom_prefixes = f.cont
        pref_list = custom_prefixes.get(str(ctx.guild.id), [f"<@{self.bot.user.id}> ", f"<@!{self.bot.user.id}> ", "! ", "!"])
        if prefixes in pref_list:
            await ctx.send(f"Prefix {prefixes} is already added")
        elif len(prefixes) > 3:
            await ctx.send(f"Prefix cannot be longer than 3 letters")
        elif len(pref_list) > 10:
            await ctx.send(f"Only 5 prefixes allowed at once!")
        else:
            pref_list = custom_prefixes.get(str(ctx.guild.id), [f"<@{self.bot.user.id}> ", f"<@!{self.bot.user.id}> "])
            pref_list.append(f"{prefixes} ")
            pref_list.append(prefixes)
            custom_prefixes[ctx.guild.id] = pref_list
            f.edit(custom_prefixes)
            await ctx.send("Prefixes **" + prefixes+ "** is added")

    @setprefix.error
    async def pref_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You are missing Admin permission...")
    
    @commands.command(name = "unban", help = "Unbans a user that is already banned.", brief = "Unbans a user.")
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def unban(self, ctx, user:commands.UserConverter, *, reason: Optional[str]= None):
        try:
            await ctx.guild.unban(user, reason = reason)
            await ctx.send(f"Unbanned **{user.name}** for {reason}")
        except discord.errors.NotFound:
            await ctx.send("No such bans found.")
            
    @commands.command(name = "ban", brief = "Bans a user.", help = "Bans a user with name[If in guild] or id")
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, user: Union[discord.Member, discord.User], *, reason: Optional[str] = None):
        if isinstance(user, discord.Member):
            if user.guild_permissions.administrator:
                return await ctx.send("You cannot ban administrator.")
            if user.guild_permissions.ban_members or user.guild_permissions.manage_guild:
                return await ctx.send("You cannot ban mod.")
        await ctx.guild.ban(user, reason = reason)
        await ctx.send(f"Banned **{user.name}** for {reason}")
        if isinstance(user, discord.Member):
            await user.send(f"You were banned from {ctx.guild.name} for {reason}")
    
    @commands.command(name="nuke", brief = "Nuke the channel", help = "Deletes a channel and creates a clone")
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def nuke(self, ctx):
        current_channel = ctx.channel
        cloned = await current_channel.clone()
        await cloned.edit(position = ctx.channel.position)
        await current_channel.delete()
        await cloned.send(f"""Nuked by **{ctx.author}**!
https://imgur.com/LIyGeCR""")
    @nuke.error
    async def nuke_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("No perms, Sorry!")

    
    @commands.command(name = 'muterole', aliases = ['smr'], brief = "Change a Role to MuteRole", help = 'Change a Role for Muting')
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def _muterole(self, ctx, muterole: discord.Role = None):
        if muterole is None:
            await ctx.send('What role should be added for muting🤔?')
        elif muterole.id in [allrole.id for allrole in ctx.guild.roles]:
            with open('./cogs/mutedict.json', 'r') as mutefile:
                muteroles = json.load(mutefile)
            mutefile.close()
            muteroles[str(ctx.guild.id)] = muterole.id
            with open('./cogs/mutedict.json', 'w') as mutefile:
                json.dump(muteroles, mutefile, indent = 4)
            mutefile.close()
            await ctx.send(f'Muterole set to {muterole.name}')
        else:
            await ctx.send('Role Not Found')


    @commands.command(name="kick", brief = "Kicks a member", help = "Kicks a member from a guild")
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason=None):
        if ctx.author.top_role > member.top_role:
            await ctx.guild.kick(member, reason=reason)
            if reason == None:
                await ctx.send(f"User **{member.name}** has been kicked.")
                await member.send(f"You have been kicked from **{ctx.guild.name}**. No reasons given")
            else:
                await ctx.send(f"User **{member.name}** has been kicked for {reason}.")
                await member.send(f"You have been **kicked** from **{ctx.guild}** server due to the following reason:\n**{reason}**")
        elif ctx.author.id == ctx.guild.owner.id and ctx.author.top_role <= member.top_role:
            await ctx.guild.kick(member, reason=reason)
            if reason == None:
                await ctx.send(f"User **{member.name}** has been kicked.")
                await member.send(f"You have been kicked from **{ctx.guild.name}**. No reasons given")
            else:
                await ctx.send(f"User **{member.name}** has been kicked for {reason}.")
                await member.send(f"You have been **kicked** from **{ctx.guild}** server due to the following reason:\n**{reason}**")
        else: 
            await ctx.send("You are not higher in role to do so!")

    
    
    @commands.command(name = 'createmuterole', aliases = ['cmr', 'createmute'] ,help = "Creates a mute role", brief = 'Creates a role and sets it to muterole')
    @commands.guild_only()
    @commands.has_permissions(manage_roles = True)
    async def create_mute_role(self, ctx):
        perms = discord.Permissions(send_messages=False)
        mute_role = await ctx.guild.create_role(name="Muted", color=discord.Color.dark_grey(), permissions=perms)

        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, send_messages=False)
            
        with open('./cogs/mutedict.json', 'r') as mute_file:
            muteroledict = json.load(mute_file)
        mute_file.close()
        muteroledict[str(ctx.guild.id)] = mute_role.id
        
        with open('./cogs/mutedict.json', 'w') as mute_file:
            json.dump(muteroledict, mute_file, indent = 4)
        mute_file.close()
        await ctx.send("Role Created and Set as Mute Role")
    
    
    @commands.command(name = 'mute', help = 'Mute A Member [Moderation]', brief = 'Mute a Member')
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def _mute(self, ctx, mutemember: discord.Member = None):
        if mutemember is None:
            await ctx.send("Who do you want me to mute?")
            return
        else:
            try:
                with open('./cogs/mutedict.json', 'r') as mutefile:
                    muteroles = json.load(mutefile)
                    if muteroles[str(ctx.guild.id)] in [allrole.id for allrole in ctx.guild.roles]:
                        muterole = discord.utils.get(ctx.guild.roles, id = muteroles[str(ctx.guild.id)])
                        await mutemember.add_roles(muterole)
                        await ctx.send(f'User **{mutemember.name}** has been Muted.')
                    else:
                        await ctx.send('''No roles having the id you saved. Maybe someone deleted. 
Save by using **!muterole ``[@Mute Role]``**''')
            except KeyError:
                await ctx.send("""Sorry, this server doesn't have any Mute role.
Get started by adding a mute role by using 
**!muterole ``[@Mute Role]``**""")
            finally:
                mutefile.close()
    
    @commands.command(name = "unmute", brief = "Unmutes Member", help = "Unmute the Members that are muted")
    @commands.guild_only()
    @commands.has_permissions(kick_members = True)
    async def unmute(self, ctx, member: discord.Member):
        file = JsonLoader("./cogs/mutedict.json")
        mute_role_ids = file.cont
        mute_role_id = mute_role_ids.get(str(ctx.guild.id), None)
        if mute_role_id is None:
            return await ctx.send("No mute roles added. Try adding roles by using **[p]muterole <muterole>**")
        muterole = discord.utils.get(ctx.guild.roles, id = mute_role_id)
        if not muterole in member.roles:
            return await ctx.send("User is not muted right now.")
        await member.remove_roles(muterole)
        await ctx.send(f"User **{member.name}** is unmuted now! They can talk now.")
                
    @commands.command(name = 'purge', aliases = ["clear"], pass_context=True, brief = "Deletes [no.] of messages", help = "Purges the number of messages you want")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, limit):
        if limit == "all" or limit == "max":
            limit = 100
        try:
            limit = int(limit)
            if limit > 100:
                limit = 100
            await ctx.channel.purge(limit=limit + 1)
            purge_msg = await ctx.send(f"""Cleared **{limit}** messages by **@{ctx.author}**""")
            await asyncio.sleep(5)
            await purge_msg.delete()
            await ctx.message.delete()
        except ValueError:
            purge_str = await ctx.send("Sorry! Didn't get it! Try writing numbers!")
            await asyncio.sleep(5)
            await purge_str.delete()
    
    
    @commands.command(name = 'slowmode', aliases = ["sm", "smode"], help = """Sets Slowmode for [Time]""", brief = "SlowMode in Current Channel")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels = True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def _slowmode(self, ctx, slowmode_time: int):
        await ctx.channel.edit(slowmode_delay=slowmode_time)
        await ctx.send(f"Slowmode set to {slowmode_time} seconds")
    
    @_slowmode.error
    async def slowmode_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You can't change showmode")
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("No spamming slowdown.")
    
    
def setup(bot):
    bot.add_cog(Mod(bot))