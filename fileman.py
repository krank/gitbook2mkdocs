import json
import re
import shutil
import yaml
import urllib.parse
from pathlib import Path

import ux

Asset_dict_type = dict[str, str]


def read_frontmatter(mdfile: Path) -> dict[str, object]:
    pattern = re.compile(r'^---\n(?P<frontmatter>[\S\s]*?)\n---')

    match = pattern.match(mdfile.read_text())
    if match and match.group('frontmatter'):
        yml: dict[str, object] = yaml.safe_load(match.group('frontmatter'))
        return yml
    return {}


def copy_files(docs_source_dir: Path, docs_target_dir: Path, full_asset_target_dir: Path):

    # Delete target dir
    if docs_target_dir.exists():
        shutil.rmtree(docs_target_dir)
        ux.print(f'... deleted: {docs_target_dir}')

    # Original folders declared here so if destination is a subfolder it's not included
    original_folders = docs_source_dir.glob("*/")

    if not full_asset_target_dir.exists():
        full_asset_target_dir.mkdir(parents=True, exist_ok=True)
        ux.print(f'... created: {docs_target_dir}, {full_asset_target_dir}')
        ux.print('== Copying files and folders ==')

        # Copy all folders to docs/
        for folder in original_folders:
            folder = folder.relative_to(docs_source_dir)

            # Ignore .git folder
            if (folder.name.startswith('.')):
                continue
            ux.print(f' Ignoring {folder}')

            ux.print(f' Copy {folder}')
            shutil.copytree(
                docs_source_dir / folder,
                docs_target_dir / folder
            )

        # Copy md-pages tree to docs/

        for md_file in docs_source_dir.glob("*.md"):
            md_file = md_file.relative_to(docs_source_dir)

            source_file = docs_source_dir / md_file
            target_file: Path = docs_target_dir / md_file

            frontmatter = read_frontmatter(source_file)

            if 'hidden' in frontmatter and frontmatter['hidden'] == True:
                target_file = Path(
                    target_file.parent / (target_file.stem + ".hidden" + target_file.suffix))

            shutil.copy(
                source_file,
                target_file
            )

        ux.print('... done copying md-pages tree')
    else:
        ux.print("... please delete docs/")
        ux.print("Aborting!")
        exit()


def copy_assets(assets_dict: Asset_dict_type, full_asset_sourcedir: Path, full_asset_targetdir: Path):

    # Copy and rename assets used in md-pages
    ux.print("\nStarting renaming and copying assets ...")

    if full_asset_sourcedir.exists():
        for original_name, new_name in assets_dict.items():
            # First decode html-entities
            original_name = urllib.parse.unquote(original_name)

            ux.print(f' {original_name} >> {new_name}')

        # Prep new full names including paths
            full_original_name = full_asset_sourcedir / original_name
            full_new_name = full_asset_targetdir / new_name

        # Check if image exists with html-entities name
            if full_original_name.exists():
                shutil.copy(str(full_original_name), str(full_new_name))
            else:
                ux.print(f' ... missing: {full_original_name}')

        ux.print('... all assets renamed and copied')
    else:
        ux.print(f'... could not copy assets to {full_asset_targetdir}')


def write_assets_json(docs_source_dir: Path, assets_dict: Asset_dict_type):
    # Write assets_dict to assets.json in source dir
    asset_file = Path(docs_source_dir, 'assets.json')

    with asset_file.open('w', encoding='utf-8') as file:
        json.dump(assets_dict, file, indent=4, ensure_ascii=False)
        ux.print("\nWriting assets.json")


def copy_extra_files(docs_target_dir: Path, extra_source_dir: Path):
    if extra_source_dir.exists():
        ux.print('Copying extra files')
        for source_file in extra_source_dir.glob('**/*.*'):
            target_file: Path = docs_target_dir / \
                source_file.relative_to(extra_source_dir)
            ux.print(f' {source_file} >> {target_file}')

            target_file.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy(
                source_file,
                target_file
            )
        ux.print("...copied extra files")
    else:
        ux.print(
            f'\'Extra\' file directory "{extra_source_dir}" not found, skipping...')
