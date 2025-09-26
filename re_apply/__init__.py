import importlib
import types
import typing
from ._remodule import *

# https://dev.to/charlesw001/plugin-architecture-in-python-jla

# Initialize; load all plugins

plugins_to_use: list[str] = ['tag',
                             'hint',
                             'tab',
                             'embed_yt',
                             'embed',
                             'code',
                             'mark',
                             'link',
                             'quote',
                             'images',
                             'file',
                             'listitem',
                             ]

loaded_plugins: dict[str, _remodule.ReModule] = {}

for plugin_name in plugins_to_use:
    plugin_path_name = f'{__name__}.plugins.{plugin_name}'
    module: types.ModuleType = importlib.import_module(plugin_path_name, '.')

    if issubclass(module.Plugin, _remodule.ReModule):
        m: type[_remodule.ReModule] = module.Plugin
        loaded_plugins[plugin_name] = m()


def apply(text: str, inc: list[str] = [], exc: list[str] = [], callback: typing.Callable[[str], None] | None = None):
    for plugin_name in loaded_plugins:
        if (len(inc) > 0 and plugin_name not in inc) \
                or (len(exc) > 0 and plugin_name in exc):
            continue
        plugin = loaded_plugins[plugin_name]

        text = plugin.apply(text)

        if callback:
            callback(plugin_name)

    return text


def set_global(key: str, value: object):
    for plugin in loaded_plugins:
        plugin = loaded_plugins[plugin_name]
        plugin.local_dict[key] = value


def set_local(plugin_name: str, key: str, value: object):
    if plugin_name in loaded_plugins:
        plugin = loaded_plugins[plugin_name]
        plugin.local_dict[key] = value


def get_local(plugin_name: str, key: str) -> object:
    if plugin_name in loaded_plugins:
        plugin = loaded_plugins[plugin_name]
        if key in plugin.local_dict:
            return plugin.local_dict[key]

    return ''
