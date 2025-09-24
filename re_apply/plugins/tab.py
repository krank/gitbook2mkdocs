from .._remodule import *

# replace gitbook tab and titles to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% tab title="file.txt" %}
# some text
# {% endtab %}
# ---------- with -----------
# ### file.txt
#     some text


class Plugin (ReModule):
    name = 'tab'
    pattern: re.Pattern[str] = re.compile(
        r'{% tab title=\"(?P<title>.*)\" %}(?P<content>[\s\S]*?){% endtab %}')

    def handler(self, match: re.Match[str]) -> str:
        tab_title = match.group("title")
        tab_content = str(match.group("content")).replace("\n", "\n    ")

        return f'=== "{tab_title}"\n{tab_content}'
