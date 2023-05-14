import discord
from discord.ext import commands

import dotenv, os
from typing import Optional
import pkgutil, sys, traceback

from core import plugins

import logging
logger = logging.getLogger('discord')


def load_module(module_path : str, module_prefix : Optional[str] = None) -> list[str]:
    if module_prefix is None:
        module_prefix = ""
    
    module = [module.name for module in pkgutil.iter_modules([module_path], prefix=module_prefix)]
    return module



class BotExtentionsLoader:
    def __init__(self) -> None:
        
        self.extentions : list[str] = []
    
    def add_new_extention(self, plugin : plugins.Plugin) -> None:
        extention = load_module(plugin.path, plugin.prefix)
        
        self.extentions.extend(extention)
        
        
    def add_multiple_extentions(self, plugins : list[plugins.Plugin]) -> None:
        for plugin in plugins:
            self.add_new_extention(plugin)
        
        
    async def load_extensions(self, bot : commands.Bot) -> None:
        for plugin in self.extentions:
            try:
                await bot.load_extension(plugin)
            except Exception as e:
                logger.error(f'Failed to load extension {plugin}.')




class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
        command_prefix='!',
        intents=discord.Intents.all()
        )
        
        self.plugin_loader = plugins.PluginLoader()
        
        all_plugins_name = ["gamification"]
        for plugin in all_plugins_name:
            self.plugin_loader.add_plugin(plugins.Plugin.create(plugin))
            
        self.extention_loader = BotExtentionsLoader()
        self.extention_loader.add_multiple_extentions(self.plugin_loader.plugins)

    async def setup_hook(self) -> None:
        
        await self.extention_loader.load_extensions(self)
        
        await self.tree.sync()
        

    async def on_ready(self):
        print('-------------')
        print(f'Logged in as {self.user}')
        print(f'Bot is ready.')
        
    
    


def main() -> None:
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO) 
    
    date_format = "%d/%m/%Y %H:%M:%S"
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('[{asctime}] [{levelname}] {name}: {message}', date_format, style='{'))
    logger.addHandler(handler)
    
    
    bot = MyBot()
    
    
    dotenv.load_dotenv()
    token = os.getenv('DISCORD_TOKEN')

    if token is None:
        raise ValueError('Token not found')

    bot.run(token)
    
    



if __name__ == '__main__':
    main()