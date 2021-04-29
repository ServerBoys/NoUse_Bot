#pylint:disable=W0312
import discord
from discord.ext import commands, ipc

class Ipc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.ipc.update_endpoints()
    
    def cog_unload(self):
        self.bot.ipc.update_endpoints()
    
    @ipc.server.route()
    async def get_guild_count(self, data):
        return len(self.bot.guilds)
    
    @ipc.server.route()
    async def get_mutual_guilds_with_admin(self, data):
        final = []
        for guild in self.bot.guilds:
            if guild.id in data.guild_ids:
                user= guild.get_member(data.user_id)
                if user.guild_permissions.administrator:
                    final.append(guild.id)
        return final
    
    @ipc.server.route()
    async def get_channels(self, data):
        guild = self.bot.get_guild(data.guild_id)
        categories = {}
        for category in guild.categories:
            channels = {}
            for channel in category.text_channels: channels[str(channel.id)] = channel.name
            categories[str(category.id)] = {
                "name": category.name,
                "channels": channels
            }
        return categories
    
    @ipc.server.route()
    async def send_message(self, data):
        guild = self.bot.get_guild(data.guild_id)
        channel = guild.get_channel(data.channel_id)
        content=data.message.get('content', None)
        embed_dict= data.message.get('embed', None)
        embed= discord.Embed.from_dict(embed_dict) if embed_dict is not None else None
        try:
            await channel.send(content=content, embed=embed)
            return True
        except Exception as e:
            print(e)
            return False
    
    @ipc.server.route()
    async def get_members(self, data):
        guild = self.bot.get_guild(data.guild_id)
        members = {}
        for member in guild.members:
            members[str(member.id)] = {
                "name":member.name,
                "color": str(member.color)
            }
        return members
    
    @ipc.server.route()
    async def get_roles(self, data):
        guild = self.bot.get_guild(data.guild_id)
        roles = {}
        for role in guild.roles:
            roles[str(role.id)] = {
                "name": role.name,
                "color": str(role.color)
            }
        return roles
    
def setup(bot):
    bot.add_cog(Ipc(bot))