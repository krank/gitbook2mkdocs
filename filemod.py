import re
from pathlib import Path
from textwrap import indent
import yaml

# FIXME: Anchors with ä (ae), ö (oe), or using . (removed in mkdocs)
#   grundlaeggande/konsollen-console.md#console.writeline ->consolewriteline

# FIXME: Links to directories; "unrecognized relative link"
# TODO: divs = elements grouped / next to eachother. Handle?

# Local globals
local_assets_dict = {}

# region Declare regexp patterns & result handlers #############################
################################################################################

# replace gitbook hint and file extensions to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% hint style="warning" %}
# some text
# {% endhint %}
# ---------- with -----------
# !!! warning
#     some text
gb_hint_pattern = re.compile(
    r'{% hint style=\"(?P<style>.*)\" %}\n?(?P<content>.*|[\s\S]+?)\n?{% endhint %}')


def hint_handler(match: re.Match) -> str:
    hint_style = match.group("style")
    hint_content = indent(str(match.group("content")), '    ')

    return f"!!! {hint_style}\n{hint_content}"


# replace gitbook tab and file extensions to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% tab title="file.txt" %}
# some text
# {% endtab %}
# ---------- with -----------
# ### warning
#     some text
gb_tab_pattern = re.compile(
    r'{% tab title=\"(?P<title>.*)\" %}(?P<content>.*|[\s\S]+?){% endtab %}')


def tab_handler(match: re.Match) -> str:
    tab_title = match.group("title")
    tab_content = str(match.group("content")).replace("\n", "\n\t")

    return f'=== "{tab_title}"\n{tab_content}'


# replace gitbook embed to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% embed url="https://youtu.be/..." %}
# ---------- with -----------
# <iframe idth="560" height="315" src="https://youtu.be/..." title=\"YouTube video player\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>
gb_embed_yt_pattern = re.compile(
    r'{% embed url=\"https://w*\.*youtu.*/(?P<video_id>.*)\" %}')


def embed_yt_handler(match: re.Match) -> str:
    video_id = match.group("video_id")
    return f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'


# replace gitbook embed to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% embed url="..." %}
# ---------- with -----------
# <div class="embed"><i class="fas fa-link"></i><a href="...">...</a></div>
gb_embed_pattern = re.compile(r'{% embed url=\"(?P<url>.*)\" %}')


def embed_handler(match: re.Match) -> str:
    embed_url = match.group("url")
    return f'<div class="embed"><i class="fas fa-link"></i><a href="{embed_url}">{embed_url}</a></div>"'


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
gb_code_pattern = re.compile(
    r'{% code ?(?:title=\"(?P<title>.*?)\" )?(?:lineNumbers=\"?(?P<linenums>.*?)\" )?%}\n```(?P<language>.*?)?\n(?P<code>.*|[\s\S]+?)```\n{% endcode %}')


def code_handler(match: re.Match) -> str:
    code_title = f" title=\"{match.group('title')}\"" if match.group(
        'title') else ""
    code_lineNumbers = " linenums=\"1\"" if match.group(
        'linenums') == "true" else ""
    code_language = match.group(
        'language') if match.group('language') else ""
    code_actual_code = match.group('code')

    return f"``` {code_language}{code_title}{code_lineNumbers}\n{code_actual_code}```"


# replace images & figures with mkdocs-compatible format. e.g.
# --------- replace ---------
# ![Some text](<../.gitbook/assets/Image.png>)
#
# <figure><img src="../.gitbook/assets/Image.png" alt="Some text"><figcaption><p>Description</p></figcaption></figure>
# ---------- with -----------
# ![Some text](../images/image-12.png)

# ![Some text](../images/image-13.png)
# /// caption
# Description
# ///
gb_figure_pattern = re.compile(
    r'<figure>\s*?<img src=\"(?:<?)(?P<filename>.*?)(?:>?)\" alt=\"(?P<alt>.*?)\">\s*?(?:<figcaption>(?P<caption>[\S\s]*?)</figcaption>)?\s*?</figure>')
gb_image_pattern = re.compile(r'\!\[(?P<alt>.*)\]\(<?(?P<filename>.*)\)')
gb_img_pattern = re.compile(r'<img src=\"(?P<filename>.*?)\" alt=\"(?P<alt>.*?)\".*?>')


def image_handler(match: re.Match) -> str:

    img_filename = Path(
        str(match.group("filename"))
        .rstrip('>')
    )

    img_alt = match.group("alt")
    img_caption = match.group(
        "caption") if "caption" in match.groupdict() else ""

    img_index = len(local_assets_dict) + 1
    img_new_filename = f'image-{img_index}{img_filename.suffix}'

    if img_filename.name not in local_assets_dict:
        local_assets_dict[img_filename.name] = img_new_filename

    print(f'  {img_filename} >> {img_new_filename}')

    return f'![{img_alt}]({img_filename.parent.as_posix()}/{img_new_filename})\n' \
        + (f'///\n{img_caption}\n///\n' if img_caption != "" else '')


# replace gitbook embed to mkdocs-compatible format. e.g.
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
gb_file_pattern = re.compile(
    r'{% file src=\"(?P<filename>.*)\" %}(?:\n(?P<caption>.*?)\n{% endfile %})?')


def file_handler(match: re.Match) -> str:

    file_filename = Path(match.group("filename"))
    file_caption = match.group("caption") \
        if "caption" in match.groupdict() else ""

    if file_filename.name not in local_assets_dict:
        local_assets_dict[file_filename.name] = file_filename.name

    return '!!! file' \
        + f'\n    [{file_filename.name}]({file_filename})' \
        + (f'\n    {file_caption}' if file_caption != None else "")

# endregion ####################################################################
# ===============================================================================

# ##############################################################################


def replacements(filedata: str, images_dict: dict[str, str], asset_source_dir: str, asset_target_dir: str) -> tuple[str, dict[str, str]]:
    global local_assets_dict
    global local_assets_dict
    local_assets_dict = images_dict

    filedata = gb_hint_pattern.sub(hint_handler, filedata)
    filedata = gb_tab_pattern.sub(tab_handler, filedata)
    filedata = gb_embed_yt_pattern.sub(embed_yt_handler, filedata)
    filedata = gb_embed_pattern.sub(embed_handler, filedata)
    filedata = gb_code_pattern.sub(code_handler, filedata)

    # Images, figures and files
    filedata = filedata.replace(asset_source_dir, asset_target_dir)

    filedata = gb_image_pattern.sub(image_handler, filedata)
    filedata = gb_figure_pattern.sub(image_handler, filedata)
    filedata = gb_img_pattern.sub(image_handler, filedata)
    filedata = gb_file_pattern.sub(file_handler, filedata)

    # Stuff to remove
    removals = [
        "{% tabs %}\n",
        "{% endtabs %}\n",
        "{% endembed %}\n",
        "&#x20;"
    ]
    for rem in removals:
        filedata = filedata.replace(rem, "")

    # https://www.markdownguide.org/basic-syntax/#line-break-best-practices
    filedata = filedata.replace("\\\n", "  \n")

    return filedata, local_assets_dict


def read_frontmatter(mdfile: Path) -> dict[str, object]:
    pattern = re.compile(r'^---\n(?P<frontmatter>[\S\s]*?)\n---')

    match = pattern.match(mdfile.read_text())
    if match and match.group('frontmatter'):
        yml: dict[str, object] = yaml.safe_load(match.group('frontmatter'))
        return yml
    return {}
