#pylint:disable=W0312
import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashCommandOptionType as OptionType
from module.game import TicTacToe, HangMan
import asyncio, pyfiglet, random
from typing import Optional
class Fun(commands.Cog):
    """
Some FUN commands\
    """
    def __init__(self, bot):
	    self.bot = bot

    @commands.command(name = 'roll', aliases = ["dice"], help = "Roll a dice for given number. Default is six as real dice.", brief = "Roll a dice")
    async def roll(self, ctx, number:Optional[int] = 6):
        if number < 2:
            return await ctx.send("Number cannot be 1 or less than 1")
        await ctx.send(f"You rolled {random.randint(1, number)}")
    
    @cog_ext.cog_slash(name="roll", description="Roll a dice", options=[
        {
            "name": "number",
            "description": "Number",
            "type": OptionType.INTEGER,
            "required": False
        }
    ])
    async def _roll(self, ctx, number=6):
        if number<2:
            return await ctx.send("Number cannot be 1 or less than 1")
        await ctx.send(f"You rolled {random.randint(1, number)}")
    
    @commands.command(name = "ascii", help = "ASCII", brief = "ASCII")
    async def ascii(self, ctx, *, text):
        t = 0
        msg = ""
        lenn = 10
        if len(text) < 10:
            lenn = len(text) - 1
        for i in range(lenn, len(text) +1 , 10):
            if i == len(text) -1:
                msg += pyfiglet.figlet_format(text[t: i+1], "small") +"\n"
            else:
                msg += pyfiglet.figlet_format(text[t: i], 'small') + "\n"
            t = i 
        if t != len(text) - 1:
            msg += pyfiglet.figlet_format(text[t:], 'small') + "\n"
        if msg.strip()== "":
            await ctx.send("Couldnt convert that")
        else:
            await ctx.send(f"""```
{msg}```""")
    
    @commands.command(name = 'tictactoe', aliases = ["ttt"], brief = "Play TicTactoe", help ="Play Tictactoe with your friends")
    @commands.guild_only()
    async def ttt(self, ctx, player: discord.Member):
        if ctx.author == player:
            await ctx.send("You cant play with yourself")
        elif player.bot:
            await ctx.send("You cant play with bots.They cant reply lol!")
        else:
            player1 = random.choice([ctx.author, player])
            for p in [ctx.author, player]:
                if not p == player1:
                    player2 = p
            game = TicTacToe(player1, player2)
            tttem = discord.Embed(title = "TicTacToe",
                                          description = f"""```
{player1.name} vs {player2.name}
———————————————————————
|   |  1  |  2  |  3  |
|—————————————————————|
| a |  {game.start["a1"]}  |  {game.start["a2"]}  |  {game.start["a3"]}  |
|   |—————————————————|
| b |  {game.start["b1"]}  |  {game.start["b2"]}  |  {game.start["b3"]}  |
|   |—————————————————|
| c |  {game.start["c1"]}  |  {game.start["c2"]}  |  {game.start["c3"]}  |
———————————————————————
```""")
            message = await ctx.send(embed = tttem)
            await ctx.send(f"**{game.players[game.player].name}**'s turn")
            while game.winner() is None:
                player = game.player
                try:
                    def check(m):
                        return m.channel == ctx.channel and m.author == game.players[player]
                    msg = await self.bot.wait_for("message", check = check, timeout = 30)
                    game_bool = game.game(msg.content.lower())
                    
                    if game.draw():
                        await ctx.send(embed = tttem)
                        await ctx.send("Draw! Noone one")
                        break
                        return
                    
                    elif game_bool:
                        tttem = discord.Embed(title = f"TicTacToe",
                                              description = f"""```
{player1.name} vs {player2.name}
———————————————————————
|   |  1  |  2  |  3  |
|—————————————————————|
| a |  {game.start["a1"]}  |  {game.start["a2"]}  |  {game.start["a3"]}  |
|   |—————————————————|
| b |  {game.start["b1"]}  |  {game.start["b2"]}  |  {game.start["b3"]}  |
|   |—————————————————|
| c |  {game.start["c1"]}  |  {game.start["c2"]}  |  {game.start["c3"]}  |
———————————————————————
```""")

                        game.player = game.turn(player)
                        message = await ctx.send(embed = tttem)
                        await ctx.send(f"**{game.players[game.player].name}**'s turn")
                    
                    else:
                        await ctx.send(embed = tttem)
                        await ctx.send(f"""Wrong Move!
{game.players[game.player]}'s turn""")
                except asyncio.TimeoutError:
                    await ctx.send(f"""Time Over!
**{game.players[game.turn(game.player)].name}** won!""")
                    break
                except KeyError:
                    pass

            else:
                await ctx.send(f"**{game.winner().name}** is the winner...")
    
    @commands.command(name = "hangman", aliases = ["hm"], pass_context = False, brief = "Play HangMan", help = "Play Hangman Alone. Idk why?😂")
    @commands.guild_only()
    async def hangman(self, ctx):
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        a = None
        a = HangMan()
        a.restart()
        a.start()
        a.guess(".")
        hangman = discord.Embed(title = "Hangman", description = f"""```
{a.hang_word}

_____________
|           {a.person['hanger']}
|         {a.person['head']}
|          {a.person['left_hand']}{a.person['body']}{a.person['right_hand']}
|           {a.person['body']}
|          {a.person['left_leg']} {a.person['right_leg']}```""")
        msg = await ctx.send(embed = hangman)
        while a.ans() != "Won" or a.ans() != "Lose":
            try:
                
                g = await self.bot.wait_for("message", check = check, timeout = 20)
                cctx =await self.bot.get_context(g)
                if g.content.lower() == "cancel":
                    await ctx.send("Cancelled current game")
                    break
                elif not cctx.valid:
                    a.guess(g.content.lower()[0])
                    hang = f"""
_____________
|           {a.person['hanger']}
|         {a.person['head']}
|          {a.person['left_hand']}{a.person['body']}{a.person['right_hand']}
|           {a.person['body']}
|          {a.person['left_leg']} {a.person['right_leg']}"""
                    hangman = discord.Embed(title = "Hangman", description = f"""```
{a.hang_word}
{hang}```""")
                    await msg.edit(embed = hangman)
                elif cctx.valid:
                    await ctx.send("Closed the HangMan Game!")
                    break
            except asyncio.TimeoutError:
                hangman.set_footer(text = 'TimeOut')
                await msg.edit(embed = hangman)
                break
            if a.ans() == "Won":
                hangman.set_footer(text = 'Won')
                await msg.edit(embed = hangman)
                break
            elif a.ans() == "Lose":
                hangman.description += f"\n```The word was {a.word}```"
                hangman.set_footer(text = 'Lost! Better Luck Next Time!!')
                await msg.edit(embed = hangman)
                break
        
    
    @commands.command(name = "rps", brief= "Rock Paper Scissors", help = "Play Rock Paper Scissors with Bot")
    @commands.guild_only()
    async def rps(self, ctx, choice:str):
        choice = choice.lower()
        rps_abb = {
            "r" : "rock",
            "p" : "paper",
            "s" : "scissors",
            "scissor" : "scissors"
        }
        if choice in rps_abb.keys():
            choice = rps_abb[choice]
        rps_win = {
            "rock": "scissors",
            "paper": "rock",
            "scissors": "paper"
        }
        rps_emoji = {
            "rock": "✊",
            "paper": "✋",
            "scissors": "✌️"
        }
        rps_choices = ["rock", "paper", "scissors"]
        if choice in rps_choices:
            bot_choice = random.choice(rps_choices)
            
            if bot_choice == rps_win[choice]:
                rps_desc = f"**{ctx.author.name}** won🎉🎉."
                rps_foot = "🎉 GG"
                pass
            
            elif choice == rps_win[bot_choice]:
                rps_desc = f"**BOT** won."
                rps_foot = "😰 Better Luck Next Time!!"
                pass
            elif choice == bot_choice:
                rps_desc = f"Both chose **{choice.capitalize()}**."
                rps_foot = "NOONE won.."
                
                pass
            else:
                pass
            rps_embed = discord.Embed(title = "Rock Paper Scissors", description = rps_desc)
            rps_embed.add_field(name = ctx.author.name+ ": ", value = f"{rps_emoji[choice]} {choice.capitalize()}", inline = True)
            rps_embed.add_field(name = "BOT: ", value = f"{rps_emoji[bot_choice]} {bot_choice.capitalize()}", inline = True)
            rps_embed.set_footer(text = rps_foot)
            await ctx.send(embed = rps_embed)
    

def setup(bot):
    bot.add_cog(Fun(bot))