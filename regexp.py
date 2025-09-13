import os
import re
from pathlib import Path

# Local globals
local_assets_dict = {}
local_img_source_dir = ""
local_img_target_dir = ""


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
    r'{% hint style=\"(?P<style>.*)\" %}(?P<content>.*|[\s\S]+?){% endhint %}')


def hint_handler(match: re.Match) -> str:
    hint_style = match.group("style")
    hint_content = str(match.group("content")).replace("\n", "\n\t")

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


# replace figures with mkdocs-compatible format. e.g.
# --------- replace ---------
# <figure><img src="../.gitbook/assets/Image.png" alt="Some text"><figcaption><p>Description</p></figcaption></figure>
# ---------- with -----------
# ![Some text](../images/image-13.png)
# /// caption
# Description
# ///
gb_figure_pattern = re.compile(
    r'<figure><img src=\"(?:<?)(?P<filename>.*?)(?:>?)\" alt=\"(?P<alt>.*?)\"><figcaption>(?P<caption>.*?)</figcaption></figure>\n')

# replace images with mkdocs-compatible format. e.g.
# --------- replace ---------
# ![Some text](<../.gitbook/assets/Image.png>)
# ---------- with -----------
# ![Some text](../images/image-13.png)
gb_image_pattern = re.compile(r'\!\[(?P<alt>.*)\]\(<?(?P<filename>.*?)>?\)\n')


def image_handler(match: re.Match) -> str:
    global local_assets_dict
    img_filename = Path(match.group("filename"))
    img_alt = match.group("alt")
    img_caption = match.group(
        "caption") if "caption" in match.groupdict() else ""

    # img_basename = os.path.basename(img_filename)
    # img_ext = os.path.splitext(img_basename)[1]

    img_index = len(local_assets_dict) + 1
    img_new_filename = f'image-{img_index}{img_filename.suffix}'

    if img_filename.name not in local_assets_dict:
        local_assets_dict[img_filename.name] = img_new_filename

    print('  {img_path}, {img_filename} >> {img_new_filename}')

    return f'![{img_alt}]({img_filename.parent.as_posix()}/{img_new_filename})\n' \
        + (f'///\n{img_caption}\n///\n' if img_caption != "" else '')


# endregion ####################################################################
# ===============================================================================

# ##############################################################################


def replacements(filedata: str, assets: dict[str, str], img_source_dir: str, img_target_dir: str) -> tuple[str, dict[str, str]]:
    global local_assets_dict
    local_assets_dict = assets

    filedata = gb_hint_pattern.sub(hint_handler, filedata)
    filedata = gb_tab_pattern.sub(tab_handler, filedata)
    filedata = gb_embed_yt_pattern.sub(embed_yt_handler, filedata)
    filedata = gb_embed_pattern.sub(embed_handler, filedata)
    filedata = gb_code_pattern.sub(code_handler, filedata)

    # Images & figures
    filedata = filedata.replace(img_source_dir, img_target_dir)

    filedata = gb_image_pattern.sub(image_handler, filedata)
    filedata = gb_figure_pattern.sub(image_handler, filedata)

    # (Files)

    # Stuff to remove
    removals = [
        "{% tabs %}\n",
        "{% endtabs %}\n",
        "{% endembed %}\n"
    ]
    for rem in removals:
        filedata = filedata.replace(rem, "")

    # https://www.markdownguide.org/basic-syntax/#line-break-best-practices
    filedata = filedata.replace("\\\n", "  \n")

    return filedata, local_assets_dict


# # replace gitbook embed to mkdocs-compatible format. e.g.
# # --------- replace ---------
# # {% file src="..." %}
# #assets_dict = {}
# gb_file1_rg = r'{% file src=\"(.*)\" %}\n(.*|[\s\S]+?)\n{% endfile %}'
# def file1_group(groups):
#     file_src = groups.group(1)
#     asset = groups.group(2)

#     # Add asset to list if not found in array
#     if asset not in assets_dict:
#         assets_dict[asset] = asset

#     return "!!! file\n\n\t[" + asset  + "](" + urllib.parse.quote(file_src) + ")"

# gb_file2_rg = r'{% file src=\"(.*)\" %}'
# def file2_group(groups):
#     file_src = groups.group(1)
#     asset = file_src.split('/')[-1]

#     # Add asset to list if not found in array
#     if asset not in assets_dict:
#         assets_dict[asset] = asset

#     return "!!! file\n\n\t[" + asset + "](" + urllib.parse.quote(file_src) + ")"
