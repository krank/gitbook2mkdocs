#!/usr/bin/python3

import re
import os

# base_dir = '_csharp_ref_old'
nav_filename = '.nav.yml'
summary_filename = 'SUMMARY.md'

# TODO Add support for appending * to all ymls
# TODO Add support for hidden pages (must read contents of actual md, info is in frontmatter)
# TODO Add flag for using titles from SUMMARY even for normal pages

# Prepare regexp
name_trim_pattern = re.compile(r"^(##?|\*) ")
name_sub_pattern = re.compile(
    r"\[(?P<title>.*)\]\((?:(?P<path>.*)/)?(?P<filename>.*.md)\)")

# Set flags
flag_tag_print = False
flag_tag_write = False
flag_yml_print = False
tag_output_file = "tags.xml"
flag_include_star = False

def tag_print(text: str, indent: int) -> None:
    global flag_tag_print
    global flag_tag_write
    global tag_output_file

    line = indent * " " + f"<{text}>"

    if flag_tag_print:
        print(line)

    if flag_tag_write and tag_output_file:
        if indent == 0 and not text.startswith("/"):
            os.remove(tag_output_file)
        with open(tag_output_file, "a", encoding="utf-8") as file:
            file.write(line + "\n")

def parse(yml_dict: dict[str, list[str]],
          lines: list[str],
          current_line: int,
          current_indent: int) -> tuple[dict[str, list[str]], int, int]:

    # --------------------------------------------------------------------------
    # Title

    # Preliminary current title
    current_title = name_trim_pattern.sub("", lines[current_line].strip())

    # Check if chapter
    is_chapter = lines[current_line].strip().startswith("## ")

    # If title has a path, use that instead
    title_data = name_sub_pattern.match(current_title)
    if title_data != None and title_data.group('path') != None:
        current_title = os.path.join(title_data.group('path'), nav_filename)

    # If base title ("Table of contents"), just use ".nav.yml"
    if current_indent == 0:
        current_title = nav_filename

    # --------------------------------------------------------------------------
    # Prep

    yml_dict[current_title] = []
    paths = []

    # Add a README.md entry at start of every sub-category
    if title_data != None:
        if title_data.group('filename') == "README.md":
            yml_dict[current_title].append("README.md")

    tag_print(current_title, current_indent)

    current_line += 1

    # --------------------------------------------------------------------------
    # Loop through lines

    while current_line < len(lines):
        # Remove trailing \n
        line = lines[current_line].rstrip()

        # Skip line if empty
        if len(line.strip()) == 0:
            current_line += 1
            continue

        # Process line, extract usable data
        line_trimmed = name_trim_pattern.sub("", line.strip())
        line_indent = int(1 + (len(line) - len(line.strip())) / 2)

        # ----------------------------------------------------------------------
        # Handle recursion level & sectioning

        # If line starts a new chapter (## or ***) and we're at above level 0
        #  then end the current run
        if (line.startswith("## ") or line.startswith("***")) and current_indent > 0:
            tag_print("/" + current_title, current_indent)

            # We're going to end the current run.
            #  If we're in a chapter, fix its title by checking common
            #  path of subnodes
            if is_chapter:
                common_base_path = os.path.commonpath(paths)
                new_key = os.path.join(common_base_path, nav_filename)
                yml_dict[new_key] = yml_dict.pop(current_title)

            # Then return to previous level, but make it repeat this line
            return (yml_dict, current_line-1, current_indent-1)

        # If line starts a new chapter ("##") and we're at level 0
        #  then add this chapter's directory to main node's list
        #  and then recurse into a new run
        elif line.startswith("## ") and current_indent == 0:

            (yml_dict, current_line, current_indent) = parse(
                yml_dict, lines, current_line, current_indent + 1)
            
            # When the run's ended, the last key added should match
            #  this chapter, so combine the chapter's title with its path
            #  e.g. Chapter Title : chapter-title
            last_added_key = list(yml_dict)[-1]
            path_segment = os.path.split(last_added_key)[0]
            line_to_add = line_trimmed + ": " + path_segment
            
            yml_dict[current_title].append(line_to_add)

        # ------------------------------------------------------------------------------
        # Handle common lines

        if line.lstrip().startswith("* "):

            # If the line is more indented than the current run's level
            #  recurse into a new run, including the previous line as the first

            if line_indent > current_indent and current_indent > 0:
                (yml_dict, current_line, current_indent) = parse(
                    yml_dict, lines, current_line-1, current_indent + 1)

            # If the line is less indented than the current run's level
            #  return back to previous level

            elif line_indent < current_indent and current_indent > 0:
                tag_print("/" + current_title, current_indent)
                return (yml_dict, current_line-1, current_indent - 1)

            # Otherwise it should just be a normal line, with a filename
            #  and a path that we can extract using regex

            else:
                line_data = name_sub_pattern.match(line_trimmed)

                # If a filename can be extracted

                if line_data and line_data.group('filename'):
                    line_to_add = line_data.group('filename')

                    # For subsections, don't add the readme, add the last
                    #  section of the path instead
                    if line_to_add == "README.md" and line_data.group('path'):
                        line_to_add = line_data.group('title').replace('\\', "") \
                            + ": " \
                            + line_data.group('path').split('/')[-1]

                    tag_print(line_to_add + "/", current_indent + 1)

                    if is_chapter:
                        paths.append(line_data.group('path'))
                    yml_dict[current_title].append(line_to_add)

                # If it can't, something is seriously wrong but just add
                #  the trimmed line
                else:
                    # Should never happen
                    yml_dict[current_title].append(line_trimmed)

        current_line += 1

    # ------------------------------------------------------------------------------
    # Final cleanup after last line

    tag_print("/" + current_title, current_indent)
    return (yml_dict, current_line, current_indent-1)

def make_navyml(base_dir: str) -> dict[str, list[str]]:
    summary_full_filename = os.path.join(base_dir, summary_filename)
    print(summary_full_filename)

    if not os.path.isfile(summary_full_filename):
        print("... SUMMARY.md not found")
        return {}

    yml_dict = {}
    with open(summary_full_filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

        (yml_dict, current_line, current_indent) = parse(yml_dict, lines, 0, 0)

        if flag_yml_print:
            for key in yml_dict.keys():
                print("# " + key)
                for line in yml_dict[key]:
                    print("     > " + line)

    return yml_dict

def create_files(base_dir: str, yml_dict: dict[str, list[str]]) -> None:
    for filename, content in yml_dict.items():
        full_filename = os.path.join(base_dir, filename)

        res = list(map(lambda line: f"  - {line}\n", content))
        res.insert(0, "nav:\n")

        try:
            with open(full_filename, "w", encoding="utf-8") as file:
                file.writelines(res)
        except:
            print(f"Failed to create {full_filename}")

def generate_nav_ymls(base_dir: str):
    yml_dict = make_navyml(base_dir)
    create_files(base_dir, yml_dict)
