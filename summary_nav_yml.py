#!/usr/bin/python3

import re
import os
from pathlib import Path

import yaml

import ux

# TODO: parse function is _very_ long. Can it be shortened?

Yml_dict_type = dict[str, list[str | dict[str, str]]]

# base_dir = '_csharp_ref_old'
nav_filename = Path('.nav.yml')
summary_filename = Path('SUMMARY.md')
tag_output_file = Path("tags.xml")

# Prepare regexp
name_trim_pattern = re.compile(r"^(##?|\*) ")
name_sub_pattern = re.compile(
    r'\[(?P<title>.*)\]\((?P<filename>.*.md)\)')

# Set flags
flag_tag_write = False
flag_include_star = True
flag_always_use_titles = True


def tag_print(text: str, indent: int) -> None:
    global flag_tag_write
    global tag_output_file

    line = indent * " " + f"<{text}>"

    if flag_tag_write and tag_output_file:
        if indent == 0 and not text.startswith("/"):
            tag_output_file.unlink()
        with tag_output_file.open("a", encoding="utf-8") as file:
            file.write(line + "\n")


def parse(yml_dict: Yml_dict_type,
          lines: list[str],
          current_line: int,
          current_indent: int) -> tuple[Yml_dict_type, int, int]:

    # --------------------------------------------------------------------------
    # Title

    # Preliminary current title
    current_title = name_trim_pattern.sub("", lines[current_line].strip())

    # Check if chapter
    is_chapter = lines[current_line].strip().startswith("## ")

    # If title has a path, use that instead
    title_data = name_sub_pattern.match(current_title)

    title_filename = Path(title_data.group('filename')) \
        if title_data and 'filename' in title_data.groupdict() \
        else None

    if title_data and title_filename:
        current_title = (title_filename.parent /
                         nav_filename).as_posix()

    # If base title ("Table of contents"), just use ".nav.yml"
    if current_indent == 0:
        current_title = nav_filename

    # --------------------------------------------------------------------------
    # Prep

    if (isinstance(current_title, Path)):
        current_title = current_title.as_posix()

    yml_dict[current_title] = []
    paths: list[Path] = []

    # Add a README.md entry at start of every sub-category
    if title_filename:
        if title_filename.name == "README.md":
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
                new_key = Path(common_base_path, nav_filename).as_posix()
                yml_dict[new_key] = yml_dict.pop(current_title)

            # Then return to previous level, but make it repeat this line
            return (yml_dict, current_line-1, current_indent-1)

        # If line starts a new chapter ("##") and we're at level 0
        #  then recurse into a new run
        #  and then add this chapter's directory to main node's list
        elif line.startswith("## ") and current_indent == 0:

            (yml_dict, current_line, current_indent) = parse(
                yml_dict, lines, current_line, current_indent + 1)

            # When the run's ended, the last key added should match
            #  this chapter, so combine the chapter's title with its path
            #  e.g. Chapter Title : chapter-title
            last_added_key = Path(list(yml_dict)[-1])
            line_to_add = {
                line_trimmed: last_added_key.parent.as_posix()}

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
                return (yml_dict, current_line - 1, current_indent - 1)

            # Otherwise it should just be a normal line, with a filename
            #  and a path that we can extract using regex

            else:
                line_data = name_sub_pattern.match(line_trimmed)

                # If a filename can be extracted

                if line_data and line_data.group('filename'):
                    entry_filename = Path(line_data.group('filename')) \
                        if line_data.group('filename') else Path("")
                    entry_title = str(
                        line_data.group('title')
                    ).replace('\\', "")

                    if ":" in entry_title:
                        entry_title = '"' + entry_title + '"'

                    line_to_add = ""

                    # For subsections, don't add the readme, add the last
                    #  section of the path instead, with the title
                    if entry_filename.name == 'README.md' and entry_filename.parents and current_indent > 0:
                        line_to_add = {
                            entry_title: entry_filename.parent.name}

                    elif flag_always_use_titles:
                        line_to_add = {
                            entry_title: entry_filename.as_posix()}
                    else:
                        line_to_add = entry_filename.name

                    tag_print(str(line_to_add) + "/", current_indent + 1)

                    if is_chapter:
                        paths.append(entry_filename.parent)

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


def make_nav_yml(base_dir: Path) -> Yml_dict_type:
    summary_full_filename = base_dir / summary_filename

    if not summary_full_filename.is_file():
        ux.print("... SUMMARY.md not found")
        return {}

    yml_dict: Yml_dict_type = {}

    lines = summary_full_filename \
        .read_text(encoding='utf-8') \
        .splitlines()

    yml_dict = parse(yml_dict, lines, 0, 0)[0]

    return yml_dict


def create_files(base_dir: Path, yml_dict: Yml_dict_type) -> None:
    for filename, content in yml_dict.items():
        full_filename = base_dir / filename

        yml_structure: dict[str, object] = {
            'ignore': '*.hidden.md'
        }

        if flag_include_star:
            content.append('*')

        yml_structure["nav"] = content

        yml_str = yaml.safe_dump(yml_structure) \
            .replace("'*'", '"*"')

        try:
            with full_filename.open("w", encoding="utf-8") as file:
                file.write(yml_str)
            ux.print(f' Created {full_filename}')
        except:
            ux.print(f' Failed to create {full_filename}')


def generate_nav_ymls(base_dir: Path, include_star: bool = True, always_use_titles: bool = False):
    global flag_include_star
    global flag_always_use_titles

    flag_include_star = include_star
    flag_always_use_titles = always_use_titles

    yml_dict = make_nav_yml(base_dir)
    create_files(base_dir, yml_dict)
    ux.print(f'... {len(yml_dict)} nav yml files created')
