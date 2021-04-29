import discord
def ping(arg, role, memb):
    msg = arg
    while "<@" in arg.strip() and ">" in arg[arg.index("<@")+ 2:].strip():
        indping = arg.index("<@")
        argping1 = arg[indping+2:]
        indping2 = argping1.index(">")
        argping = argping1[:indping2]
        if argping[0]== "&":
            msg = msg.replace(f"<@{argping}>", "@"+discord.utils.get(role, id = int(argping[1:])).name)
        elif argping[0] == "!":
            msg = msg.replace(f"<@{argping}>", "@"+discord.utils.get(memb, id = int(argping[1:])).name)
        else:
            msg = msg.replace(f"<@{argping}>", "@"+discord.utils.get(memb, id = int(argping)).name)
        arg = argping1[indping2:]
    return str(msg)