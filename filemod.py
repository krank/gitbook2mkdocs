import re
from pathlib import Path
from textwrap import indent
from fileman import Asset_dict_type
import uuid

import ux

# Local globals
local_assets_dict: Asset_dict_type = {}

code_block_dict: dict[str, str] = {}


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


def hint_handler(match: re.Match[str]) -> str:
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
    r'{% tab title=\"(?P<title>.*)\" %}(?P<content>[\s\S]*?){% endtab %}')


def tab_handler(match: re.Match[str]) -> str:
    tab_title = match.group("title")
    tab_content = str(match.group("content")).replace("\n", "\n    ")

    return f'=== "{tab_title}"\n{tab_content}'


# replace gitbook embed to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% embed url="https://youtu.be/..." %}
# ---------- with -----------
# <iframe idth="560" height="315" src="https://youtu.be/..." title=\"YouTube video player\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>
gb_embed_yt_pattern = re.compile(
    r'{% embed url=\"https://w*\.*youtu.*/(?P<video_id>.*)\" %}')


def embed_yt_handler(match: re.Match[str]) -> str:
    video_id = match.group("video_id")
    return f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'


# replace gitbook embed to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% embed url="..." %}
# ---------- with -----------
# <div class="embed"><i class="fas fa-link"></i><a href="...">...</a></div>
gb_embed_pattern = re.compile(r'{% embed url=\"(?P<url>.*)\" %}')


def embed_handler(match: re.Match[str]) -> str:
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


def code_handler(match: re.Match[str]) -> str:
    code_title = f" title=\"{match.group('title')}\"" if match.group(
        'title') else ""
    code_lineNumbers = " linenums=\"1\"" if match.group(
        'linenums') == "true" else ""
    code_language = match.group(
        'language') if match.group('language') else ""
    code_actual_code = match.group('code')

    return f"``` {code_language}{code_title}{code_lineNumbers}\n{code_actual_code}```"


gb_codeblock_pattern = re.compile(
    r'(?P<indent> *?)```(?P<content>[\S\s]*?)```')


def code_block_to_uuid(match: re.Match[str]) -> str:
    block_content = str(match.group('content'))
    block_uuid = str(uuid.uuid4())
    code_block_dict[block_uuid] = block_content

    return f'```{block_uuid}```'


def code_uuid_to_block(match: re.Match[str]) -> str:
    block_uuid = str(match.group('content'))
    block_indent = str(match.group('indent'))
    if block_uuid in code_block_dict:
        block_content = code_block_dict[block_uuid]
    else:
        block_content = block_uuid

    # Take the opportunity to match indent of all lines
    return indent(f'```{block_content}```', block_indent)


# replace images & figures with mkdocs-compatible format. e.g.
# --------- replace ---------
# ![Some text](<../.gitbook/assets/Image.png>)
#
# <figure><img src="../.gitbook/assets/Image.png" alt="Some text"><figcaption><p>Description</p></figcaption></figure>
# ---------- with -----------
# ![Some text](../images/image-12.png)
#
# ![Some text](../images/image-13.png)
# /// caption
# Description
# ///
gb_figure_pattern = re.compile(
    r'<figure>\s*?<img src=\"(?:<?)(?P<filename>.*?)(?:>?)\" alt=\"(?P<alt>.*?)\">\s*?(?:<figcaption>(?P<caption>[\S\s]*?)</figcaption>)?\s*?</figure>')
gb_image_pattern = re.compile(r'\!\[(?P<alt>.*)\]\(<?(?P<filename>.*)\)')
gb_img_pattern = re.compile(
    r'<img src=\"(?P<filename>.*?)\" alt=\"(?P<alt>.*?)\".*?>')


def image_handler(match: re.Match[str]) -> str:
    global local_assets_dict
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

    ux.print(f'  {img_filename} >> {img_new_filename}')

    return f'![{img_alt}]({img_filename.parent.as_posix()}/{img_new_filename})\n' \
        + (f'/// caption\n{img_caption}\n///\n' if img_caption != "" else '')


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


def file_handler(match: re.Match[str]) -> str:

    file_filename = Path(match.group("filename"))
    file_caption = match.group("caption") \
        if "caption" in match.groupdict() else ""

    if file_filename.name not in local_assets_dict:
        local_assets_dict[file_filename.name] = file_filename.name

    return '!!! file' \
        + f'\n    [{file_filename.name}]({file_filename})' \
        + (f'\n    {file_caption}' if file_caption != None else "")


# remove unnecessary <mark> tags around inline `code`
# --------- replace ---------
#   Type <mark style="color:orange;">`print()`</mark> to print
# ---------- with -----------
#   Type <mark style="color:orange;">`print()`</mark> to print
gb_mark_pattern = re.compile(
    r'<mark.*?>(?P<content>`.*?`)</mark>')


def strip_handler(match: re.Match[str]):
    return match.group("content")

# Make sure (local) links to folders go to README.md's, and fix anchors
# --------- replace ---------
#   [text][link_folder/]
#   [test][./#heading]
# ---------- with -----------
#   [text][link_folder/README.md]
#   [test][#heading]


# gb_link_pattern = re.compile(r'\[(?P<text>.*?)\]\((?P<url>.*?)\)')

gb_link_pattern = re.compile(
    r'\[(?P<text>.*?)\]\((?P<url>(?P<path>(?<=\().*?)(?P<filename>[^/\n\(]*?)?(?P<anchor>#.+?(?=\)))?\))')


def link_handler(match: re.Match[str]):
    link_text = str(match.group('text'))
    link_url = str(match.group('url'))

    link_path = str(match.group('path')) if match.group('path') else ''
    link_filename = str(match.group('filename')
                        ) if match.group('filename') else ''
    link_anchor = str(match.group('anchor')) if match.group('anchor') else ''

    # Detect urls leading to local folders
    if not link_path.startswith('http'):

        # Add README to folder links
        if link_filename == '':
            link_filename = 'README.md'

        # Remove periods from anchors
        link_anchor = link_anchor.replace('.', '')

    link_url = link_path + link_filename + link_anchor

    return f'[{link_text}]({link_url})'


# Make sure tags are properly escaped
# --------- replace ---------
# \<h1>Heading\</h1>
# ---------- with -----------
# <h1\>Heading</h1\>
gb_tag_pattern = re.compile(r'\\<(?P<tagname>.*?)>')


def tag_handler(match: re.Match[str]):
    tag_name = str(match.group('tagname'))
    return f'<{tag_name}\\>'


# Make sure indents in quotes are properly indented using spaces
# --------- replace ---------
# >     tal = slump()
# ---------- with -----------
# > &nbsp;&nbsp;&nbsp;&nbsp;tal = slump()
gb_quote_pattern = re.compile(r'> (?P<indent> *)(?P<content>.+)')


def quote_handler(match: re.Match[str]):
    quote_indent = str(match.group('indent'))
    quote_content = str(match.group('content'))

    quote_indent = '&nbsp;' * len(quote_indent)

    return f'> {quote_indent}{quote_content}'


# endregion ####################################################################
# ===============================================================================

# ##############################################################################


def make_replacements(filedata: str, asset_source_dir: Path, asset_target_dir: Path) -> str:
    global local_assets_dict

    # Reset dict of uuids and code block contents
    global code_block_dict
    code_block_dict = {}

    # Fix code blocks
    filedata = gb_code_pattern.sub(code_handler, filedata)

    # Replace all code blocks' contents with uuids
    filedata = gb_codeblock_pattern.sub(code_block_to_uuid, filedata)

    # Symbol replacements
    filedata = filedata.replace('&#x20;', ' ')

    # hints/admonishments, tabs, embeds
    filedata = gb_hint_pattern.sub(hint_handler, filedata)
    filedata = gb_tab_pattern.sub(tab_handler, filedata)
    filedata = gb_embed_yt_pattern.sub(embed_yt_handler, filedata)
    filedata = gb_embed_pattern.sub(embed_handler, filedata)
    filedata = gb_link_pattern.sub(link_handler, filedata)
    filedata = gb_mark_pattern.sub(strip_handler, filedata)

    # https://github.com/mkdocs/mkdocs/issues/3563
    filedata = gb_tag_pattern.sub(tag_handler, filedata)

    # Quotes
    filedata = gb_quote_pattern.sub(quote_handler, filedata)

    # Images, figures and files
    filedata = filedata.replace(
        asset_source_dir.as_posix(), asset_target_dir.as_posix())

    filedata = gb_image_pattern.sub(image_handler, filedata)
    filedata = gb_figure_pattern.sub(image_handler, filedata)
    filedata = gb_img_pattern.sub(image_handler, filedata)
    filedata = gb_file_pattern.sub(file_handler, filedata)

    # Replace uuids within code blocks with their contents
    filedata = gb_codeblock_pattern.sub(code_uuid_to_block, filedata)

    # Stuff to remove
    removals = [
        '{% tabs %}\n',
        '{% endtabs %}\n',
        '{% endembed %}\n',
        '<div>',
        '</div>'
    ]
    for rem in removals:
        filedata = filedata.replace(rem, '')

    # https://www.markdownguide.org/basic-syntax/#line-break-best-practices
    filedata = filedata.replace('\\\n', '  \n')

    return filedata


def modify_files(docs_target_dir: Path, asset_source_dir: Path, asset_target_dir: Path) -> Asset_dict_type:

    local_assets_dict.clear()

    ux.print(f'\nStarting to modify md-pages in {docs_target_dir} ...')

    f_count = 0

    for md_file in docs_target_dir.glob('**/*.md'):
        # Skip summary file
        if md_file.name == 'SUMMARY.md':
            continue
        ux.print(f'parsing: {md_file}')
        filedata = md_file.read_text(encoding='utf-8')

        filedata = make_replacements(
            filedata, asset_source_dir, asset_target_dir)

        md_file.write_text(filedata, encoding='utf-8')
        f_count += 1

    ux.print(f'... done modifying md-pages tree ({f_count} pages)')
    return local_assets_dict
