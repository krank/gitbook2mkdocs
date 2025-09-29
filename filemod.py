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

# endregion ####################################################################
# ===============================================================================

# ##############################################################################


gb_removals = re.compile(r'{% tabs %}|{% endtabs %}|{% endembed %}|<\/?div>')


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

    # Replace uuids within code blocks with their contents
    filedata = gb_codeblock_pattern.sub(code_uuid_to_block, filedata)

    # Stuff to remove
    filedata = gb_removals.sub('', filedata)

    # https://www.markdownguide.org/basic-syntax/#line-break-best-practices
    filedata = filedata.replace('\\\n', '  \n')

    return filedata


def modify_files(docs_target_dir: Path, asset_source_dir: Path, asset_target_dir: Path) -> Asset_dict_type:
    local_assets_dict.clear()

    ux.print(f'\nStarting to modify md-pages in {docs_target_dir} ...')

    re_apply.set_local('images', 'assets', local_assets_dict)
    re_apply.set_local('file', 'assets', local_assets_dict)


    f_count = 0

    for md_file in docs_target_dir.glob('**/*.md'):
        # Skip summary file
        if md_file.name == 'SUMMARY.md':
            continue
        ux.print(f' parsing: {md_file}')
        re_apply.set_local('link', 'file', md_file)
            
        filedata = md_file.read_text(encoding='utf-8')

        filedata = make_replacements(
            filedata, asset_source_dir, asset_target_dir)

        md_file.write_text(filedata, encoding='utf-8')
        f_count += 1

    # re_apply.set_local('images', 'assets', local_assets_dict)
    # local_assets_dict: dict[str, str] = re_apply.get_local('images', 'assets')

    ux.print(f'... done modifying md-pages tree ({f_count} pages)')
    return local_assets_dict
