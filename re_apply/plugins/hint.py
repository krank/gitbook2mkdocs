from .._remodule import *
from textwrap import indent

# replace gitbook hint and file extensions to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% hint style="warning" %}
# some text
# {% endhint %}
# ---------- with -----------
# !!! warning
#     some text


class Plugin (ReModule):
    name = 'hint'
    pattern = [re.compile(
        r'{% hint style=\"(?P<style>.*)\" %}\n?(?P<content>.*|[\s\S]+?)\n?{% endhint %}')]

    def handler(self, match: re.Match[str]) -> str:
        hint_style = match.group("style")
        hint_content = indent(str(match.group("content")), '    ')

        return f"!!! {hint_style}\n{hint_content}"
