from pathlib import Path
from .._remodule import *

# replace gitbook code blocks to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% code title="filename.cs" lineNumbers="true" %}
# ``` csharp
#  some code
# ```
# {% endcode %}
# ---------- with -----------
# ``` csharp title="filename.cs" linenums="1"
# some code
# ```


class Plugin (ReModule):
    name = 'code'

    # Order is important here!
    pattern = [
        # Markdown images ![]()
        re.compile(r'\!\[(?P<alt>.*)\]\((?P<filename>[^<].*[^>])\)'),
        re.compile(r'\!\[(?P<alt>.*)\]\(<(?P<filename>.*)>\)'),
        
        # figures <figure><img><figcaption></figcaption></figure>
        re.compile(
            r'<figure>\s*?<img src=\"(?:<?)(?P<filename>.*?)(?:>?)\" alt=\"(?P<alt>.*?)\">\s*?(?:<figcaption>(?P<caption>[\S\s]*?)</figcaption>)?\s*?</figure>'),
        
        # pure img-tags
        re.compile(
            r'<img src=\"(?P<filename>.*?)\" alt=\"(?P<alt>.*?)\".*?>'),
    ]

    def handler(self, match: re.Match[str]) -> str:
        img_filename = Path(
            str(match.group("filename"))
        )

        img_alt = match.group("alt")
        img_caption = match.group(
            "caption") if "caption" in match.groupdict() else ""

        # if 'assets' in locals:
        if 'assets' in self.local_dict \
                and isinstance(self.local_dict['assets'], dict):

            # If there was type coersion or checking, I'd be able to do this
            #  without resorting to "ignore this error". Just trust me, bro
            # pyright: ignore[reportUnknownVariableType]
            local_assets: dict[str, str] = self.local_dict['assets'] # type: ignore

            img_index = len(local_assets) + 1
            img_new_filename = f'image-{img_index}{img_filename.suffix}'

            if img_filename.name not in local_assets:
                local_assets[img_filename.name] = img_new_filename

            self.local_dict['assets'] = local_assets
        else:
            raise Exception("Images module doesn't have the assets dict")

        return f'![{img_alt}]({img_filename.parent.as_posix()}/{img_new_filename})\n' \
            + (f'/// caption\n{img_caption}\n///\n' if img_caption != "" else '')
