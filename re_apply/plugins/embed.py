from .._remodule import *

# replace gitbook embed to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% embed url="..." %}
# ---------- with -----------
# <div class="embed"><i class="fas fa-link"></i><a href="...">...</a></div>


class Plugin (ReModule):
    name = 'embed'
    pattern = [re.compile(
        r'{% embed url=\"(?P<url>.*)\" %}')]

    def handler(self, match: re.Match[str]) -> str:
        embed_url = match.group("url")
        return '<div class="embed"><i class="fas fa-link"></i>' \
            + f'<a href="{embed_url}">{embed_url}</a>'\
            + '</div>"'
