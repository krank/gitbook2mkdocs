#!/usr/bin/python3

import re
import os

# TODO Add support for hidden pages (must read contents of actual md, info is in frontmatter)

# Prepare regexp
name_trim_pattern = re.compile(r"^(##?|\*) ")
name_sub_pattern = re.compile(
    r"\[(?P<title>.*)\]\((?:(?P<path>.*)/)?(?P<filename>.*.md)\)")

# Set flags
flag_tag_print = False
flag_tag_write = False
flag_yml_print = True
tag_output_file = "tags.xml"
flag_include_star = False


def tag_print(text: str, indent: int):
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


def parse(yml_dict: dict[str, list[str]], lines: list[str], current_line: int, current_indent: int):

    # --------------------------------------------------------------------------
    # Title

    # Preliminary current title
    current_title = name_trim_pattern.sub("", lines[current_line].strip())

    # Check if chapter
    is_chapter = lines[current_line].strip().startswith("## ")

    # If title has a path, use that instead
    title_data = name_sub_pattern.match(current_title)
    if title_data != None and title_data.group('path') != None:
        current_title = title_data.group('path') + "/.nav.yml"

    # If base title ("Table of contents"), just use ".nav.yml"
    if current_indent == 0:
        current_title = ".nav.yml"

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
        #

        # If line starts a new chapter (## or ***) and we're at above level 0
        #  then end the current run
        if (line.startswith("## ") or line.startswith("***")) and current_indent > 0:
            tag_print("/" + current_title, current_indent)

            # We're going to end the current run.
            #  If we're in a chapter, fix its title by checking common
            #  path of subnodes
            if is_chapter:
                new_key = os.path.commonpath(paths) + "/.nav.yml"
                yml_dict[new_key] = yml_dict.pop(current_title)

            # Then return to previous level, but make it repeat this line
            return (yml_dict, current_line-1, current_indent-1)

        # If line starts a new chapter ("##") and we're at level 0
        #  then add this chapter's directory to main node's list
        #  and then recurse into a new run
        elif line.startswith("## ") and current_indent == 0:
            yml_dict[current_title].append(line_trimmed)
            (yml_dict, current_line, current_indent) = parse(
                yml_dict, lines, current_line, current_indent + 1)

        # If it's just a common line
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
                
                if is_chapter:
                    print(current_title)
                return (yml_dict, current_line, current_indent - 1)

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
                        line_to_add = line_data.group('path').split('/')[-1]

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

    tag_print("/" + current_title, current_indent)
    if is_chapter:
        print(current_title)
    return (yml_dict, current_line, current_indent-1)


def make_navyml(base_dir: str):

    summary_filename = base_dir + "/" + "SUMMARY.md"

    if not os.path.isfile(summary_filename):
        print("... SUMMARY.md not found")
        return None

    with open(summary_filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

        yml_dict = {}

        (yml_dict, current_line, current_indent) = parse(yml_dict, lines, 0, 0)

        if flag_yml_print:
            for key in yml_dict.keys():
                print("# " + key)
                for line in yml_dict[key]:
                    print("     > " + line)


make_navyml('_csharp_ref_old/SUMMARY.md')
