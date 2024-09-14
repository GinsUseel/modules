from dedlib import rModule

@rModule.module(name="test", description="Модуль для загрузки и управления другими модулями", author="NewWayLabs")
class test:
    def __init__(self, client):
        self.client = client
    
    async def cmd_testav(self, msg):
        await msg.answer(f'чтоkdjdn')
        await self.client.send_message('me', 'чтаоагоа')