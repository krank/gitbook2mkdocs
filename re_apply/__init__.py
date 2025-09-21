import importlib
import types
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

plugins: list[_remodule.ReModule] = []

for plugin_name in plugins_to_use:
    plugin_name = f'{__name__}.{plugin_name}'
    module: types.ModuleType = importlib.import_module(plugin_name, '.')

    if issubclass(module.Plugin, _remodule.ReModule):
        m: type[_remodule.ReModule] = module.Plugin
        plugins.append(m())


def apply(text: str, inc: list[str] = [], exc: list[str] = []):
    for plugin in plugins:
        if (len(inc) > 0 and plugin.name not in inc) \
                or (len(exc) > 0 and plugin.name in exc):
            continue

        text = plugin.apply(text)

    return text

# https://dev.to/charlesw001/plugin-architecture-in-python-jla
