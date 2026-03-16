# gitbook2mkdocs

This is a python script to convert a gitbook project for use with Material for mkdocs.

It's quite opinionated and tailored to my specific use case.

It's always work in progress.

## Preparations

Clone this repo to any location.

Create a basic mkdocs project folder. Its "docs" subfolder will be the *target*

Clone *source* (gitbook) repo. It is recommended to make it a subfolder named "src" in the mkdocs project folder.

Run the gitbook2mkdocs script. If it's run in the mkdocs project folder (with src and docs subfolders), it should use those automatically and not require any additional commandline switches.

## Usage

```
usage: gitbook2mkdocs.py [-h] [--generate-nav {True,False}] [source_path] [target_path]

positional arguments:
  source_path
  target_path

options:
  -h, --help            show this help message and exit
  --generate-nav, -n {True,False}
                        Using SUMMARY.md, generate .nav.yml files for root and all subdirectories. Used by awesome-nav plugin
```