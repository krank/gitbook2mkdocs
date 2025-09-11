#!/usr/bin/python3

import sys, glob, os, shutil, re, json, html, urllib.parse

# Import from folder .admin

sys.path.append(sys.path[0] + "/.admin") # using folder of script, not folder where script runs
from nav import generate_nav

# Read dash parameters
private = False
if len(sys.argv) > 1:
    if sys.argv[1] == "-p":
        private = True

print("Starting...")

# Root folder for mkdocs
# doc_root = "../docs/"
doc_root = "docs/"

# All assets files
img_source = ".gitbook/assets/"
img_dest = "images/"

# Dictionary to collect assets
assets_dict = {}


#region REGEXPS ################################################################
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
    code_title = f" title=\"{groups.group('title')}\"" if groups.group('title') else ""
    code_lineNumbers = " linenums=\"1\"" if groups.group('linenums') == "true" else ""
    code_language = groups.group('language') if groups.group('language') else ""
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
    #return "<div class=\"embed\">[" + embed_url  + "](" + embed_url + ")</div>"
    return "<div class=\"embed\"><i class=\"fas fa-link\"></i><a href=\"" + embed_url  + "\">" + embed_url + "</a></div>"

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

    return "!!! file\n\n\t[" + asset  + "](" + file_src + ")"

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
#img_index = 1
# Regex for image
gb_img_rg = r'\!\[.*\]\(<?(.*)/(.*)>?\)'
def img_group(groups):
    global assets_dict
    global img_index

    img_path = groups.group(1).replace('\\', '')
    img_src = groups.group(2).replace('\\', '')

    # Fix ending '>'
    img_src = img_src.replace('>', '');
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
    img_src = img_src.replace('>', '');

    img = os.path.basename(img_src)
    img_ext = os.path.splitext(os.path.basename(img_src))[1]
    img_index = len(assets_dict)

    # Add image to list if not found in array
    if img not in assets_dict:
        assets_dict[img] = "image-" + str(img_index) + img_ext

    print("... " + img_path + ", " + img_src + " >> " + assets_dict[img])
    return "![](" + img_path + "/" + assets_dict[img] + ")"

#endregion #####################################################################
################################################################################

# Delete docs/*
if os.path.exists(doc_root):
    shutil.rmtree(doc_root)
    print("... deleted: " + doc_root)

# Get all folders
folders = glob.glob("*/")

# Create docs/images
if not os.path.exists(doc_root + img_dest):
    os.makedirs(doc_root + img_dest)
    print("... created: " + doc_root + ", " + doc_root + img_dest)

    # Copy md-pages tree to docs/
    for md_file in glob.glob("*.md"):
        shutil.copy(md_file, "docs/" + md_file)

    # Copy all folders to docs/
    for folder in folders:
        shutil.copytree(folder, "docs/" + folder)
else:
    print("... please delete docs/")
    print("Aborting!")
    exit()

# Move into docs/
os.chdir(doc_root)

# Recursiv replace in all *.md
print("\nStarting copying md-pages to " + doc_root + " ...")
for md_file in glob.glob("**/*.md", recursive=True):
    with open(md_file, 'r') as file:
        print("parsing: " + md_file)
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
    filedata = filedata.replace("\<", "&lt;")
    filedata = filedata.replace("\>", "&gt;")
    
    # Find images
    filedata = re.sub(gb_img_rg, img_group, filedata)
    filedata = re.sub(gb_figure_rg, figure_group, filedata)
    
    with open(md_file, 'w') as file:
        file.write(filedata)

print("... done copying md-pages tree")

os.chdir('..')

#region NAV WRITING (disabled) #################################################

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

#endregion #####################################################################
################################################################################

# Write assets_dict to assets.json
with open('assets.json', 'w', encoding='utf-8') as file:
    json.dump(assets_dict, file, indent=4, ensure_ascii=False)
    print("\nWriting assets.json")

# Print number of assets_dict
print("\nFound " + str(len(assets_dict)) + " assets")

# Copy and rename images used i md-pages
print("\nStarting renaming images ...")
if os.path.exists(img_source):
    for key, value in assets_dict.items():
        # First decode html-entities
        file_name = urllib.parse.unquote(key)
        print(file_name + " >> " + value)

        # Check if image exists with html-entities name
        if os.path.exists(img_source + file_name):
            shutil.copy(img_source + file_name, doc_root + img_dest + value)
        else:
            print("... missing: " + img_source + file_name)
    print("... all images renamed and copied")
else:
    print("... could not copy images to docs/")

print("Done!")