import re
from pathlib import Path
from textwrap import indent
import uuid

from fileman import Asset_dict_type
import ux

import re_apply

# Local globals
local_assets_dict: Asset_dict_type = {}

code_block_dict: dict[str, str] = {}


# region Declare regexp patterns & result handlers #############################
################################################################################


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


# endregion ####################################################################
# ===============================================================================

# ##############################################################################


def make_replacements(filedata: str, asset_source_dir: Path, asset_target_dir: Path) -> str:

    global local_assets_dict

    # Images, figures and files
    filedata = filedata.replace(
        asset_source_dir.as_posix(), asset_target_dir.as_posix())

    # Symbol replacements
    filedata = filedata.replace('&#x20;', ' ')

    # Reset dict of uuids and code block contents
    global code_block_dict
    code_block_dict = {}

    # Fix code blocks
    filedata = re_apply.apply(filedata, inc=['code'])

    # Replace all code blocks' contents with uuids
    filedata = gb_codeblock_pattern.sub(code_block_to_uuid, filedata)

    # Apply a bunch of replacements (code, tags, etc)
    filedata = re_apply.apply(filedata, exc=['code'])

    filedata = gb_image_pattern.sub(image_handler, filedata)
    filedata = gb_figure_pattern.sub(image_handler, filedata)
    filedata = gb_img_pattern.sub(image_handler, filedata)
    filedata = gb_file_pattern.sub(file_handler, filedata)

    # Replace uuids within code blocks with their contents
    filedata = gb_codeblock_pattern.sub(code_uuid_to_block, filedata)

    # TODO: This could probably be done by a regex
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
        ux.print(f' parsing: {md_file}')
        filedata = md_file.read_text(encoding='utf-8')

        filedata = make_replacements(
            filedata, asset_source_dir, asset_target_dir)

        md_file.write_text(filedata, encoding='utf-8')
        f_count += 1

    ux.print(f'... done modifying md-pages tree ({f_count} pages)')
    return local_assets_dict
