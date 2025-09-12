import os, re

#region Declare regexp patterns & result handlers

# replace gitbook hint and file extensions to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% hint style="warning" %}
# some text
# {% endhint %}
# ---------- with -----------
# !!! warning
#     some text
gb_hint_pattern = re.compile(r'{% hint style=\"(?P<style>.*)\" %}(?P<content>.*|[\s\S]+?){% endhint %}')

def hint_group(match: re.Match) -> str:
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
gb_tab_pattern = re.compile(r'{% tab title=\"(?P<title>.*)\" %}(?P<content>.*|[\s\S]+?){% endtab %}')

def tab_group(match: re.Match) -> str:
    tab_title = match.group("title")
    tab_content = str(match.group("content")).replace("\n", "\n\t")
    
    return f'=== "{tab_title}"\n{tab_content}'


# replace gitbook embed to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% embed url="https://youtu.be/..." %}
# ---------- with -----------
# <iframe idth="560" height="315" src="https://youtu.be/..." title=\"YouTube video player\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>
gb_embed_yt_pattern = re.compile(r'{% embed url=\"https://w*\.*youtu.*/(?P<video_id>.*)\" %}')

def embed_yt_group(match: re.Match) -> str:
    video_id = match.group("video_id")
    return f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
    

# replace gitbook embed to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% embed url="..." %}
# ---------- with -----------
# <div class="embed"><i class="fas fa-link"></i><a href="...">...</a></div>
gb_embed_pattern = re.compile(r'{% embed url=\"(?P<url>.*)\" %}')

def embed_group(match: re.Match) -> str:
    embed_url = match.group("url")
    return f'<div class="embed"><i class="fas fa-link"></i><a href="{embed_url}">{embed_url}</a></div>"'


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
gb_code_pattern = re.compile(r'{% code ?(?:title=\"(?P<title>.*?)\" )?(?:lineNumbers=\"?(?P<linenums>.*?)\" )?%}\n```(?P<language>.*?)?\n(?P<code>.*|[\s\S]+?)```\n{% endcode %}')

def code_group(groups):
    code_title = f" title=\"{groups.group('title')}\"" if groups.group('title') else ""
    code_lineNumbers = " linenums=\"1\"" if groups.group('linenums') == "true" else ""
    code_language = groups.group('language') if groups.group('language') else ""
    code_actual_code = groups.group('code')
    return f"``` {code_language}{code_title}{code_lineNumbers}\n{code_actual_code}```"

#endregion

# ##############################################################################

def replacements(filedata: str) -> str:
    
    filedata = gb_hint_pattern.sub(hint_group, filedata)
    filedata = gb_tab_pattern.sub(tab_group, filedata)
    filedata = gb_embed_yt_pattern.sub(embed_yt_group, filedata)
    filedata = gb_embed_pattern.sub(embed_group, filedata)
    filedata = gb_code_pattern.sub(code_group, filedata)
    
    # Images
    # Figures
    # (Files)
    
    # Stuff to remove
    removals = [
        "{% tabs %}\n",
        "{% endtabs %}\n",
        "{% endembed %}\n"
    ]
    for rem in removals:
        filedata.replace(rem, "")
    
    # https://www.markdownguide.org/basic-syntax/#line-break-best-practices
    filedata = filedata.replace("\\\n", "  \n")
    
    # Replace tags
    filedata = filedata.replace("<", "&lt;")
    filedata = filedata.replace(">", "&gt;")
    
    
    return filedata


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

# # Find image
# gb_img_rg = r'\!\[.*\]\(<?(.*)/(.*)>?\)'
# def img_group(groups):
#     img_path = groups.group(1)
#     img_src = groups.group(2)

#     # Fix ending '>'
#     img_src = img_src.replace('>', '');
#     img = os.path.basename(img_src)
#     img_ext = os.path.splitext(os.path.basename(img_src))[1]

#     # Get assets_dict length
#     img_index = len(assets_dict) + 1

#     # if img_path not starting with http, and not in assets_dict, add to assets_dict
#     if not img_path.startswith("http") and img_path not in assets_dict:
#         assets_dict[img] = "image-" + str(img_index) + img_ext
#         #img_index += 1

#         print("... " + img_path + ", " + img_src + " >> " + assets_dict[img])
#         return "![](" + img_path + "/" + assets_dict[img] + ")"

# gb_figure_rg = r'<figure><img src=\"(.*)/(.*)\" alt=\"\"><figcaption></figcaption></figure>'
# def figure_group(groups):
#     img_path = groups.group(1)
#     img_src = groups.group(2)

#     # Fix ending '>'
#     img_src = img_src.replace('>', '');

#     img = os.path.basename(img_src)
#     img_ext = os.path.splitext(os.path.basename(img_src))[1]

#     # Get assets_dict length
#     img_index = len(assets_dict) + 1

#     # Add image to list if not found in array
#     if img not in assets_dict:
#         assets_dict[img] = "image-" + str(img_index) + img_ext
#         #img_index += 1

#     print("... " + img_path + ", " + img_src + " >> " + assets_dict[img])
#     return "![](" + img_path + "/" + assets_dict[img] + ")"