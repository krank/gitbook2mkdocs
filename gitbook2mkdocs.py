#!/usr/bin/python3

# TODO: Add commandline parameters for source and dest directory
# TODO: Modularize
# TODO: Fix it so .hidden files' names are properly changed everywhere

# Related links:
# - https://lukasgeiter.github.io/mkdocs-awesome-nav/

import sys
import glob
import os
import shutil
import json
import urllib.parse
from pathlib import Path

import filemod
import summary_nav_yml

# Read dash parameters
private = False
if len(sys.argv) > 1:
    if sys.argv[1] == "-p":
        private = True

print("Starting...")

# Root folder for mkdocs
docs_target_dir = Path("docs")
# docs_target_dir = Path("_csharp_ref_old/docs")

# Root source folder
docs_source_dir = Path("_csharp_ref_old")

# Stylesheet source folder
css_source_dir = Path("css")

# Image subfolder names
asset_source_dir = ".gitbook/assets"
asset_target_dir = "assets"

# Dictionary to collect assets
assets_dict = {}

def print_header(text: str):
    print('\n################################################################################')
    print(f'   {text}')
    print('--------------------------------------------------------------------------------')


# region COPY FILES ############################################################
################################################################################

print_header('Copying files...')

# Delete target dir
if docs_target_dir.exists():
    shutil.rmtree(docs_target_dir)
    print(f'... deleted: {docs_target_dir}')

full_img_target_dir = Path(docs_target_dir, asset_target_dir)

# Original folders declared here so if destination is a subfolder it's not included
original_folders = glob.glob("*/", root_dir=docs_source_dir)

if not os.path.exists(full_img_target_dir):
    os.makedirs(full_img_target_dir)
    print(f'... created: {docs_target_dir}, {full_img_target_dir}')
    print('== Copying files and folders ==')

    
    # Copy all folders to docs/
    for folder in original_folders:
        print(f'Copy {folder}')
        # Ignore .git folder

        shutil.copytree(
            docs_source_dir / folder,
            docs_target_dir / folder
        )

    # Copy md-pages tree to docs/

    for md_file in glob.glob("*.md", root_dir=docs_source_dir):
        source_file = docs_source_dir / md_file
        target_file: Path = docs_target_dir / md_file

        frontmatter = filemod.read_frontmatter(source_file)

        if 'hidden' in frontmatter and frontmatter['hidden'] == True:
            target_file = Path(
                target_file.parent / (target_file.stem + ".hidden" + target_file.suffix))

        shutil.copy(
            source_file,
            target_file
        )

    print('... done copying md-pages tree')
else:
    print("... please delete docs/")
    print("Aborting!")
    exit()

# endregion ####################################################################
# ==============================================================================

# region MODIFY FILES ##########################################################
################################################################################

print_header('Modifying files...')

# Recursiv replace in all *.md
print(f'\nStarting modifying md-pages in {docs_target_dir} ...')

f_count = 0
for md_file in docs_target_dir.glob('**/*.md'):

    print(f'parsing: {md_file}')
    filedata = md_file.read_text(encoding='utf-8')

    filedata, assets_dict = filemod.replacements(
        filedata, assets_dict, asset_source_dir, asset_target_dir)

    md_file.write_text(filedata, encoding='utf-8')
    f_count += 1

print(f'... done modifying md-pages tree ({f_count} pages)')

# endregion ####################################################################
# ==============================================================================

# region NAV WRITING ###########################################################
################################################################################

print_header('Generate .nav.yml files for "awesome nav" plugin...')

summary_nav_yml.generate_nav_ymls(docs_target_dir,
                                  include_star=True,
                                  always_use_titles=False)

# endregion ####################################################################
# ==============================================================================

# region ASSET MANAGEMENT ######################################################
################################################################################

print_header('Copy and rename assets...')

# Write assets_dict to assets.json in source dir
asset_file = Path(docs_source_dir, 'assets.json')

with asset_file.open('w', encoding='utf-8') as file:
    json.dump(assets_dict, file, indent=4, ensure_ascii=False)
    print("\nWriting assets.json")

# Print number of assets_dict
print(f'\nFound {len(assets_dict)} assets')


# Copy and rename assets used in md-pages
print("\nStarting renaming and copying assets ...")

full_asset_sourcedir = Path(docs_source_dir, asset_source_dir)

if full_asset_sourcedir.exists():
    for original_name, new_name in assets_dict.items():
        # First decode html-entities
        original_name = urllib.parse.unquote(original_name)

        print(f' {original_name} >> {new_name}')

        # Prep new full names including paths
        full_original_name = full_asset_sourcedir / original_name
        full_new_name = full_img_target_dir / new_name

        # Check if image exists with html-entities name
        if full_original_name.exists():
            shutil.copy(str(full_original_name), str(full_new_name))
        else:
            print(f' ... missing: {full_original_name}')

    print("... all assets renamed and copied")
else:
    print("... could not copy assets to docs/")

# endregion ####################################################################
# ==============================================================================

# region FINISHING TOUCHES #####################################################
################################################################################

print_header('Finishing touches...')

# CSS
print('Copying css files')
for source_file in css_source_dir.glob('*.css'):

    target_file: Path = docs_target_dir / source_file.name
    print(f' {source_file} >> {target_file}')

    shutil.copy(
        source_file,
        target_file
    )
print("...copied css files")

print("Done!")
