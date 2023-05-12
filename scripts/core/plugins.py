from dataclasses import dataclass

DEFAULT_PLUGIN_PREFIX = 'plugins.'
DEFAULT_PLUGIN_PATH = 'scripts/plugins/'

@dataclass
class Plugin:
    name: str
    
    def __post_init__(self) -> None:
        self.__path = DEFAULT_PLUGIN_PATH + self.name
        self.__prefix = DEFAULT_PLUGIN_PREFIX + self.name + '.'
        
    
    def modify_path(self, new_path : str) -> "Plugin":
        self.__path = new_path + self.name
        return self
        
    def modify_prefix(self, new_prefix : str) -> "Plugin":
        self.__prefix = new_prefix + self.name + '.'
        return self
    
        
    @property
    def path(self) -> str:
        return self.__path
    
    @property
    def prefix(self) -> str:
        return self.__prefix
    
    
    @staticmethod
    def create(name : str) -> "Plugin":
        return Plugin(name)
    
    
    
    
class PluginLoader:
    def __init__(self) -> None:
        """Simple plugin loader."""
        self.plugins : list[Plugin] = []
        
        
    def add_plugin(self, plugin : Plugin) -> None:
        self.plugins.append(plugin)
        
    
    def remove_plugin(self, plugin_name : str) -> None:
        for plugin in self.plugins:
            if plugin.name == plugin_name:
                self.plugins.remove(plugin)
                break
            
        else:
            raise ValueError(f'Plugin {plugin_name} not found.')