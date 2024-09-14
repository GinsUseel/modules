from dedlib import rModule
import time
import datetime

@rModule.module(name="Information")
class Information:
    def __init__(self):
        self.uptime_client = time.time()

    async def cmd_pinger(self, msg):
        tping = time.time()
        await msg.edit('🌖')
        endtime = time.time()
        ms = float((endtime - tping) * 1000)

        cctime = time.time()
        uptime = cctime - self.uptime_client

        year, new = divmod(uptime, 31536000)
        days, new = divmod(new, 86400)
        hours, new = divmod(new, 3600)
        minutes, seconds = divmod(new, 60)

        if year >= 1:
            trtime = f'{int(year)} год(а), {int(days)} дней, {int(hours)} часов, {int(minutes)} минут, {int(seconds)} секунд'
        elif days >= 1:
            trtime = f'{int(days)} дней, {int(hours)} часов, {int(minutes)} минут, {int(seconds)} секунд'
        elif hours >= 1:
            trtime = f'{int(hours)} часов, {int(minutes)} минут, {int(seconds)} секунд'
        elif minutes >= 1:
            trtime = f'{int(minutes)} минут, {int(seconds)} секунд'
        else:
            trtime = f'{int(seconds)} секунд'

        await msg.edit(f'**⚡ Отклик Telegram:** `{ms:.2f} мс`\n**️🚀 Время работы:** `{trtime}`')
   
    
    async def ggg(self):
        pass
    
    def hsha(self):
        txt = "hahaha"
        return txt
    
    async def cmd_info(self, msg):
        txt = self.hsha()
        await msg.edit(txt)
        