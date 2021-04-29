from discord.ext import commands
def seconvert(hours, minutes, seconds):
    h = int(hours) * 3600
    m = int(minutes) * 60
    s = int(seconds)
    
    total_sec = h + m + s
    return total_sec


def convert(seconds): 

    seconds = seconds % (24 * 3600) 

    hour = seconds // 3600

    seconds %= 3600

    minutes = seconds // 60

    seconds %= 60

    if "%d" %(hour) == "0":
        if "%d" %(minutes) == "0":
            if int("%d" %(seconds)) < 20:
                return "few seconds"
            else:
                return "%ds" % (seconds)
        elif "%d"%(seconds) == '0':
            return "%dm"%(minutes)
        else:
            return "%dm %ds" % (minutes, seconds)
        
    elif "%d" %(minutes) == "0":
        if "%d"%(seconds) == "0":
            return "%dh"%(hour)
        else:
            return "%dh %ds" % (hour, seconds)
        
    elif "%d"%(seconds) == '0':
        return "%dh %dm"%(hour, minutes)

    else:
        return "%dh %dm %ds" % (hour, minutes, seconds) 
    
class NotInHex(Exception):
    def __init__(self):
        Exception.__init__(self, "Color Not Found")
    def __repr__(self):
        return "NotInHex"
class ColorConvertor(commands.Converter):
    async def convert(self, ctx, color_str):
        self.color_str = color_str.lstrip("#").lower().strip()
        color_str = self.color_str
        str_list = []
        for text in "abcdef01234567890":
            str_list.append(text)
        r = True
        for text in color_str:
            if not text in str_list:
                r = False
        if not r:
            raise NotInHex
        color = int(color_str, 16)
        if color > 16777215:
            raise NotInHex
        return color
    def __repr__(self):
        return f"<ColorConverter color = {self.color_str}"
        