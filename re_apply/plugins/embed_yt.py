from .._remodule import *

# replace gitbook youtube embed to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% embed url="https://youtu.be/..." %}
# ---------- with -----------
# <iframe idth="560" height="315" src="https://youtu.be/..." title=\"YouTube video player\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>


class Plugin (ReModule):
    name = 'embed_yt'
    pattern: re.Pattern[str] = re.compile(
        r'{% embed url=\"https://w*\.*youtu.*/(?P<video_id>.*)\" %}')

    def handler(self, match: re.Match[str]) -> str:
        video_id = match.group("video_id")
        return '<iframe width="560" height="315" ' \
            + f'src="https://www.youtube.com/embed/{video_id}" ' \
            + 'title="YouTube video player" frameborder="0" ' \
            + 'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" ' \
            + 'allowfullscreen>' \
            + '</iframe>'
