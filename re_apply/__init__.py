import importlib
import types
import typing
from ._remodule import *

# Initialize; load all plugins

plugins_to_use: list[str] = ['tag',
                             'hint',
                             'tab',
                             'embed_yt',
                             'embed',
                             'code',
                             'mark',
                             'link',
                             'quote'
                             ]

loaded_plugins: list[_remodule.ReModule] = []

for plugin_name in plugins_to_use:
    plugin_name = f'{__name__}.plugins.{plugin_name}'
    module: types.ModuleType = importlib.import_module(plugin_name, '.')

    if issubclass(module.Plugin, _remodule.ReModule):
        m: type[_remodule.ReModule] = module.Plugin
        loaded_plugins.append(m())


def apply(text: str, inc: list[str] = [], exc: list[str] = [], callback: typing.Callable[[str], None] | None = None):
    for plugin in loaded_plugins:
        if (len(inc) > 0 and plugin.name not in inc) \
                or (len(exc) > 0 and plugin.name in exc):
            continue

        text = plugin.apply(text)

        if callback:
            callback(plugin.name)

    return text

# https://dev.to/charlesw001/plugin-architecture-in-python-jla
