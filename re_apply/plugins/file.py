from pathlib import Path
from .._remodule import *

# replace gitbook file embeds to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% file src="https://example.com/example.pdf" %}
# {% file src="https://example.com/example2.pdf" %}
#   Caption
# {% endfile %}
# ---------- with -----------
# !!! file
#   [](https://example.com/example.pdf)
# # !!! file
#   [Caption](https://example.com/example 2.pdf)


class Plugin (ReModule):
    name = 'file'
    pattern = re.compile(
        r'{% file src=\"(?P<filename>.*)\" %}(?:\n(?P<caption>.*?)\n{% endfile %})?')

    def handler(self, match: re.Match[str]) -> str:
        file_filename = Path(match.group("filename"))
        file_caption = match.group("caption") \
            if "caption" in match.groupdict() else ""

        # if 'assets' in locals:
        if 'assets' in self.local_dict \
                and isinstance(self.local_dict['assets'], dict):

            # If there was type coersion or checking, I'd be able to do this
            #  without resorting to "ignore this error". Just trust me, bro
            # pyright: ignore[reportUnknownVariableType]
            local_assets: dict[str, str] = self.local_dict['assets'] # type: ignore

            if file_filename.name not in local_assets:
                local_assets[file_filename.name] = file_filename.name
                
            self.local_dict['assets'] = local_assets

        else:
            raise Exception("File module doesn't have the assets dict")

        return '!!! file' \
            + f'\n    [{file_filename.name}]({file_filename})' \
            + (f'\n    {file_caption}' if file_caption != None else "")