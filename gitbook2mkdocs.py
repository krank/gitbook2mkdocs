#!/usr/bin/python3

# TODO: Add support for hidden pages (must read contents of actual md, info is in frontmatter) (use .hidden.md filename)
# TODO: Add commandline parameters for source and dest directory
# TODO: Modularize

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
docs_target_dir = Path("_csharp_ref_old/docs")
# Root source folder
docs_source_dir = Path("_csharp_ref_old")

# Image subfolder names
asset_source_dir = ".gitbook/assets"
asset_target_dir = "assets"

# Dictionary to collect assets
assets_dict = {}

# region COPY FILES ############################################################
################################################################################


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
        shutil.copy(
            docs_source_dir / md_file,
            docs_target_dir / md_file
        )
        print(f'Copying {md_file}')

else:
    print("... please delete docs/")
    print("Aborting!")
    exit()

# endregion ####################################################################
# ===============================================================================

# region MODIFY FILES ##########################################################
################################################################################

print('== Modifying files ==')

# Recursiv replace in all *.md
print(f'\nStarting modifying md-pages in {docs_target_dir} ...')

for md_file in docs_target_dir.glob('**/*.md'):

    print(f'parsing: {md_file}')
    filedata = md_file.read_text(encoding='utf-8')

    filedata, assets_dict = filemod.replacements(
        filedata, assets_dict, asset_source_dir, asset_target_dir)

    md_file.write_text(filedata, encoding='utf-8')

print("... done copying md-pages tree")

# endregion ####################################################################
# ===============================================================================

# region NAV WRITING (disabled) ################################################

# Write nav changes to yml

# Add link to folder .git for mkdocs-git-revision-date-localized-plugin to work
# os.symlink("../.git", doc_root + ".git")
# print("... created: " + doc_root + ".git")

# Create new mkdocs.yml from head.yml an base.yml
# print("... creating mkdocs.yml")

# # Check if head.yml and base.yml exist
# if not os.path.isfile('head.yml'):
#     print("... head.yml not found")
#     exit()
# if not os.path.isfile('base.yml'):
#     print("... base.yml not found")
#     exit()

# with open('head.yml', 'r', encoding='utf-8') as file:
#     head_content = file.read()
# with open('base.yml', 'r', encoding='utf-8') as file:
#     base_content = file.read()
# with open('mkdocs.yml', 'w', encoding='utf-8') as file:
#     file.write(head_content + base_content)

#     # Add empty line
#     file.write("\n")

#     # Add nav
#     file.write(generate_nav(private))

#     # Print response
#     print("... done rebuilding nav")


# Check if assets.json exists
# if not os.path.isfile('assets.json'):
#     print("... assets.json not found")
#     exit()

# endregion #####################################################################
# ===============================================================================

summary_nav_yml.generate_nav_ymls(docs_target_dir)

# region ASSET MANAGEMENT ######################################################
################################################################################
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
# ===============================================================================

print("Done!")
