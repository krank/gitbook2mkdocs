# gitbook2mkdocs

This is a python script to convert a gitbook project for use with Material for mkdocs.

It's quite opinionated and tailored to my specific use case.

It's always work in progress.

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