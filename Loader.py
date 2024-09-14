from dedlib import rModule
import os
import sys
import types
import inspect
import importlib
import asyncio
import time
import datetime

@rModule.module(name="Loader")
class Loader:
    def __init__(self, client):
        self.client = client

    async def load_module(self, msg):
        if not msg.is_reply or not msg.reply_to_msg_id:
            await msg.edit('**Ответьте на сообщение с файлом ❌**')
            return

        reply_msg = await msg.client.get_messages(msg.to_id, ids=msg.reply_to_msg_id)
        if not reply_msg.file:
            await msg.edit('**Ответьте на сообщение с файлом ❌**')
            return

        loads_dir = 'loads'
        if not os.path.exists(loads_dir):
            os.makedirs(loads_dir)

        file_path = os.path.join(loads_dir, reply_msg.file.name)
        await reply_msg.download_media(file=file_path)

        with open(file_path, 'r') as file:
            module_code = file.read()

        if '@rModule.module(name="' not in module_code:
            await msg.edit('**Неправильный модуль ❌**')
            os.remove(file_path)
            return

        module_name = module_code.split('@rModule.module(name="')[1].split('"')[0]
        module_description = module_code.split('description="')[1].split('"')[0] if 'description="' in module_code else None
        module_author = module_code.split('author="')[1].split('"')[0] if 'author="' in module_code else None
        module_file = f"{module_name}.py"
        module_path = os.path.join('modules', module_file)

        module = types.ModuleType(module_name)
        try:
            exec(module_code, module.__dict__)
        except Exception as e:
            await msg.edit(f'**Ошибка при загрузке модуля: {str(e)}**')
            os.remove(file_path)
            return

        class_name = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if inspect.isclass(attr) and attr.__name__ == module_name:
                class_name = attr_name
                break

        if class_name is None:
            await msg.edit('**Класс с именем модуля не найден ❌**')
            os.remove(file_path)
            return

        try:
            class_instance = getattr(module, class_name)(self.client)
        except TypeError:
            class_instance = getattr(module, class_name)()

        commands = []
        for attr_name in dir(class_instance):
            attr = getattr(class_instance, attr_name)
            if callable(attr) and attr_name.startswith("cmd_"):
                cmd = attr_name[4:]
                commands.append((cmd, attr))

        for cmd, func in commands:
            if cmd in ['lmod', 'ulmod', 'helper']:
                await msg.edit('❗ **Модуль содержит системные команды.\nМодуль не может быть установлен.**')
                os.remove(file_path)
                return

        module_dir = 'modules'
        if not os.path.exists(module_dir):
            os.makedirs(module_dir)

        os.rename(file_path, module_path)

        response = f"**◾️ Модуль** `{module_name}` **загружен!**"
        
        if module_description:
            response += f"\nℹ️ {module_description}\n\n"
            
        for cmd, func in commands:
            bio = func.__doc__ or '**нет описания**'
            response += f"▫️ `.{cmd}` - **{bio}**\n"
        
        if not commands:
            response += f"▫️ **Нет команд**\n"
            
        if module_author:
            response += f"\n👨‍💻 **Разработчик**: `{module_author}`"

        for cmd, func in commands:
            print(cmd)
            self.client.loader.remove_command(cmd)
            self.client.loader.command(c=cmd, prefix=['.'])(func)

        await msg.edit(response)

    async def cmd_helper(self, msg):
        '''помощь'''
        module_dir = 'modules'
        modules = [f for f in os.listdir(module_dir) if f.endswith('.py')]
        num_modules = len(modules)

        response = f"▫️**Всего** `{num_modules}` **модулей доступно.**\n\n"

        for module in modules:
            module_name = os.path.splitext(module)[0]
            try:
                module_obj = importlib.import_module(f"{module_dir}.{module_name}")
                commands = []
                for attr_name in dir(module_obj):
                    attr = getattr(module_obj, attr_name)
                    if inspect.isclass(attr):
                        try:
                            class_instance = attr(self)
                        except TypeError:
                            class_instance = attr()
                        for cmd_attr_name in dir(class_instance):
                            cmd_attr = getattr(class_instance, cmd_attr_name)
                            if callable(cmd_attr) and cmd_attr_name.startswith("cmd_"):
                                cmd = cmd_attr_name[4:]
                                commands.append(f"**.{cmd}**")
                response += f"◾️ **{module_name}** | {' | '.join(commands)}\n"
            except Exception as e:
                print(f"Ошибка при загрузке модуля {module_name}: {str(e)}")

        await msg.edit(response)

    async def cmd_lmod(self, msg):
        '''загрузить модуль'''
        await self.load_module(msg)

    async def cmd_ulmod(self, msg):
        '''удалить модуль'''
        if not msg.is_reply or not msg.reply_to_msg_id:
            await msg.edit('**Ответьте на сообщение с именем модуля ❌**')
            return

        reply_msg = await msg.client.get_messages(msg.to_id, ids=msg.reply_to_msg_id)
        if not reply_msg.text:
            await msg.edit('**Ответьте на сообщение с именем модуля ❌**')
            return

        module_name = reply_msg.text.split()[0][1:]
        module_file = f"{module_name}.py"
        module_path = os.path.join('modules', module_file)

        if module_name == "Loader":
            await msg.edit('**Системный модуль не может быть удален ❌**')
            return

        if not os.path.exists(module_path):
            await msg.edit(f'**Модуль {module_name} не найден ❌**')
            return

        module_obj = importlib.import_module(f"modules.{module_name}")
        for attr_name in dir(module_obj):
            attr = getattr(module_obj, attr_name)
            if inspect.isclass(attr):
                try:
                    class_instance = attr(self)
                except TypeError:
                    class_instance = attr()
                for cmd_attr_name in dir(class_instance):
                    cmd_attr = getattr(class_instance, cmd_attr_name)
                    if callable(cmd_attr) and cmd_attr_name.startswith("cmd_"):
                        cmd = cmd_attr_name[4:]
                        print(cmd)
                        self.client.loader.remove_command(cmd)

        os.remove(module_path)
        await msg.edit(f'**Модуль {module_name} успешно удален ✅**')