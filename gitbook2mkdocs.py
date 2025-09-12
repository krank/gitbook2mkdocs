#!/usr/bin/python3

# TODO: Make it use summary_nav_yml

# TODO: Add commandline parameters for source and dest directory
# TODO: Modularize

import sys
import glob
import os
import shutil
import re
import json
import html
import urllib.parse

# Read dash parameters
private = False
if len(sys.argv) > 1:
    if sys.argv[1] == "-p":
        private = True

print("Starting...")

# Root folder for mkdocs
# doc_root = "../docs/"
target_dir = "_csharp_ref_old/docs"
source_dir = "_csharp_ref_old"

# All assets files
img_source = ".gitbook/assets/"
img_dest = "images/"

# Dictionary to collect assets
assets_dict = {}


# region REGEXPS ################################################################
################################################################################

# replace gitbook code blocks to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% code title="filename.cs" lineNumbers="true" %}
# ``` csharp
#  some code
# ```
# {% endcode %}
# --------- to ---------
# ``` csharp title="filename.cs" linenums="1"
# some code
# ```
gb_code_rg = r'{% code ?(?:title=\"(?P<title>.*?)\" )?(?:lineNumbers=\"?(?P<linenums>.*?)\" )?%}\n```(?P<language>.*?)?\n(?P<code>.*|[\s\S]+?)```\n{% endcode %}'


def code_group(groups):
    code_title = f" title=\"{groups.group('title')}\"" if groups.group(
        'title') else ""
    code_lineNumbers = " linenums=\"1\"" if groups.group(
        'linenums') == "true" else ""
    code_language = groups.group(
        'language') if groups.group('language') else ""
    code_actual_code = groups.group('code')
    return f"``` {code_language}{code_title}{code_lineNumbers}\n{code_actual_code}```"


# replace gitbook hint and file extensions to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% hint style="warning" %}
# some text
# {% endhint %}
# --------- to ---------
# !!! warning
#     some text
gb_hint_rg = r'{% hint style=\"(.*)\" %}(.*|[\s\S]+?){% endhint %}'


def hint_group(groups):
    hint_type = groups.group(1)
    hint_content = groups.group(2)
    hint_content = hint_content.replace("\n", "\n\t")
    return "!!! " + hint_type + "\n" + hint_content


# replace gitbook tab and file extensions to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% tab title="file.txt" %}
# some text
# {% endtab %}
# --------- to ---------
# ### warning
#     some text
gb_tab_rg = r'{% tab title=\"(.*)\" %}(.*|[\s\S]+?){% endtab %}'


def tab_group(groups):
    tab_type = groups.group(1)
    tab_content = groups.group(2)
    tab_content = tab_content.replace("\n", "\n\t")
    return "=== \"" + tab_type + "\"\n" + tab_content


# replace gitbook embed to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% embed url="https://youtu.be/..." %}
gb_embedY_rg = r'{% embed url=\"https://w*\.*youtu.*/(.*)\" %}'


def embedY_group(groups):
    embedY_url = groups.group(1)
    return "<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/" + embedY_url + "\" title=\"YouTube video player\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>"


# replace gitbook embed to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% embed url="..." %}
gb_embed_rg = r'{% embed url=\"(.*)\" %}'


def embed_group(groups):
    embed_url = groups.group(1)
    # return "<div class=\"embed\">[" + embed_url  + "](" + embed_url + ")</div>"
    return "<div class=\"embed\"><i class=\"fas fa-link\"></i><a href=\"" + embed_url + "\">" + embed_url + "</a></div>"


# replace gitbook embed to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% file src="..." %}
gb_file1_rg = r'{% file src=\"(.*)\" %}\n(.*|[\s\S]+?)\n{% endfile %}'


def file1_group(groups):
    global assets_dict

    file_src = groups.group(1).replace('\\', '')
    asset = groups.group(2).replace('\\', '')

    # Add asset to list if not found in array
    if not file_src.startswith("http") and asset not in assets_dict:
        assets_dict[asset] = asset

    return "!!! file\n\n\t[" + asset + "](" + file_src + ")"


gb_file2_rg = r'{% file src=\"(.*)\" %}'


def file2_group(groups):
    global assets_dict

    file_src = groups.group(1).replace('\\', '')
    asset = file_src.split('/')[-1].replace('\\', '')

    # Add asset to list if not found in array
    if not file_src.startswith("http") and asset not in assets_dict:
        assets_dict[asset] = asset

    return "!!! file\n\n\t[" + asset + "](" + file_src + ")"


# Find image
# img_index = 1
# Regex for image
gb_img_rg = r'\!\[.*\]\(<?(.*)/(.*)>?\)'


def img_group(groups):
    global assets_dict
    global img_index

    img_path = groups.group(1).replace('\\', '')
    img_src = groups.group(2).replace('\\', '')

    # Fix ending '>'
    img_src = img_src.replace('>', '')
    img = os.path.basename(img_src)
    img_ext = os.path.splitext(os.path.basename(img_src))[1]
    img_index = len(assets_dict)

    # if img_path not starting with http
    if img_path.startswith("http"):
        return "![](" + img_path + "/" + img + ")"

    # if not in assets_dict, add to assets_dict
    if not img_path.startswith("http") and img not in assets_dict:
        assets_dict[img] = "image-" + str(img_index) + img_ext
        print("... " + img_path + ", " + img_src + " >> " + assets_dict[img])

    return "![](" + img_path + "/" + assets_dict[img] + ")"


gb_figure_rg = r'<figure><img src=\"(.*)/(.*)\" alt=\"\"><figcaption></figcaption></figure>'


def figure_group(groups):
    global assets_dict
    global img_index

    img_path = groups.group(1).replace('\\', '')
    img_src = groups.group(2).replace('\\', '')

    # Fix ending '>'
    img_src = img_src.replace('>', '')

    img = os.path.basename(img_src)
    img_ext = os.path.splitext(os.path.basename(img_src))[1]
    img_index = len(assets_dict)

    # Add image to list if not found in array
    if img not in assets_dict:
        assets_dict[img] = "image-" + str(img_index) + img_ext

    print("... " + img_path + ", " + img_src + " >> " + assets_dict[img])
    return "![](" + img_path + "/" + assets_dict[img] + ")"

# endregion #####################################################################
################################################################################


# Delete target dir
if os.path.exists(target_dir):
    shutil.rmtree(target_dir)
    print("... deleted: " + target_dir)

# Get all folders


full_img_dest = os.path.join(target_dir, img_dest)

# Create docs/images
if not os.path.exists(full_img_dest):
    os.makedirs(full_img_dest)
    print(f'... created: {target_dir}, {full_img_dest}')

    # Copy md-pages tree to docs/
    for md_file in glob.glob("*.md", root_dir=source_dir):
        shutil.copy(
            os.path.join(source_dir, md_file),
            os.path.join(target_dir, md_file)
        )

    # Copy all folders to docs/
    for folder in glob.glob("*/", root_dir=source_dir):
        shutil.copytree(
            os.path.join(source_dir, folder),
            os.path.join(target_dir, folder)
        )
else:
    print("... please delete docs/")
    print("Aborting!")
    exit()

## TODO: CONTINUE WORKING HERE

# Recursiv replace in all *.md
print(f'\nStarting modifying md-pages in {target_dir} ...')
for md_file in glob.glob(os.path.join(target_dir, "**/*.md"), recursive=True):
    with open(md_file, 'r') as file:
        print(f'parsing: {md_file}')
        filedata = file.read()

    # Replace path for assets
    filedata = filedata.replace(img_source, img_dest)
    filedata = re.sub(gb_hint_rg, hint_group, filedata)
    filedata = re.sub(gb_tab_rg, tab_group, filedata)
    filedata = re.sub(gb_embedY_rg, embedY_group, filedata)
    filedata = re.sub(gb_embed_rg, embed_group, filedata)

    # Replace code blocks
    filedata = re.sub(gb_code_rg, code_group, filedata)

    # Long or short file description?
    filedataTuple = re.subn(gb_file1_rg, file1_group, filedata)
    if filedataTuple[1] == 0:
        filedata = re.sub(gb_file2_rg, file2_group, filedata)
    else:
        filedata = filedataTuple[0]

    filedata = filedata.replace("{% tabs %}\n", "")
    filedata = filedata.replace("{% endtabs %}\n", "")
    filedata = filedata.replace("{% endembed %}\n", "")

    # https://www.markdownguide.org/basic-syntax/#line-break-best-practices
    filedata = filedata.replace("\\\n", "  \n")

    # Replace tags
    filedata = filedata.replace("<", "&lt;")
    filedata = filedata.replace(">", "&gt;")

    # Find images
    filedata = re.sub(gb_img_rg, img_group, filedata)
    filedata = re.sub(gb_figure_rg, figure_group, filedata)

    with open(md_file, 'w') as file:
        file.write(filedata)

print("... done copying md-pages tree")


# region NAV WRITING (disabled) #################################################

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
################################################################################

# Write assets_dict to assets.json in source dir
with open(os.path.join(source_dir, 'assets.json'), 'w', encoding='utf-8') as file:
    json.dump(assets_dict, file, indent=4, ensure_ascii=False)
    print("\nWriting assets.json")

# Print number of assets_dict
print(f'\nFound {len(assets_dict)} assets')


# Copy and rename images used in md-pages
print("\nStarting renaming and copying images ...")
full_img_sourcedir = os.path.join(source_dir, img_source)

if os.path.exists(full_img_sourcedir):
    for original_name, new_name in assets_dict.items():
        # First decode html-entities
        original_name = urllib.parse.unquote(original_name)
        
        print(f' {original_name} >> {new_name}')

        # Prep new full names including paths
        full_original_name = os.path.join(full_img_sourcedir, original_name)
        full_new_name = os.path.join(full_img_dest, new_name)
        
        # Check if image exists with html-entities name
        if os.path.exists(full_original_name):
            shutil.copy(full_original_name, full_new_name)
        else:
            print(f' ... missing: {full_original_name}')
            
    print("... all images renamed and copied")
else:
    print("... could not copy images to docs/")

print("Done!")
