#!/usr/bin/python3

# Related links:
# - https://lukasgeiter.github.io/mkdocs-awesome-nav/

# TODO: Can asset managing regexes also be moved to plugin system?
# TODO: Proper instructions in README

from pathlib import Path
from argparse import ArgumentParser

import filemod
import summary_nav_yml
import fileman
import ux


# region HANDLE ARGUMENTS ######################################################
# ------------------------------------------------------------------------------

parser = ArgumentParser()
parser.add_argument('source_path', nargs='?', default='src', type=str)
parser.add_argument('target_path', nargs='?', default='docs', type=str)
parser.add_argument('--generate-nav', '-n',
                    required=False,
                    type=bool,
                    default=True,
                    choices=(True, False),
                    help='Using SUMMARY.md, generate .nav.yml files for root and all subdirectories. Used by awesome-nav plugin')
parser.add_argument('--silent', '-s',
                    action='store_true',
                    help='Run silently'
                    )

# Parse args into dict
args = vars(parser.parse_args())

# endregion --------------------------------------------------------------------
# ##############################################################################

# region INITIALIZE ############################################################
# ------------------------------------------------------------------------------

ux.set_visible(not args['silent'])

ux.print("Starting...")

# Root folders for gitbook (source) and mkdocs (target)
docs_source_dir = Path(args['source_path'])
docs_target_dir = Path(args['target_path'])

# Stylesheet source folder
extra_source_dir = Path("extra")

# Image subfolder names
asset_source_dir = Path(".gitbook/assets")
asset_target_dir = Path("assets")

# Autogen
full_asset_targetdir = Path(docs_target_dir, asset_target_dir)
full_asset_sourcedir = Path(docs_source_dir, asset_source_dir)


ux.print("Checking source directory...")
if docs_source_dir.exists():
    ux.print(" Source directory exists")
else:
    ux.print(" Source directory doesn't exist, aborting")
    exit()

# endregion --------------------------------------------------------------------
# ##############################################################################


# COPY FILES -------------------------------------------------------------------

ux.header('Copying files...')
fileman.copy_files(docs_source_dir, docs_target_dir, full_asset_targetdir)


# MODIFY FILES -----------------------------------------------------------------

ux.header('Modifying files...')
# Recursive replace in all *.md, extracting an assets dictionary
assets_dict = filemod.modify_files(
    docs_target_dir, asset_source_dir, asset_target_dir)


# GENERATE NAV YML -------------------------------------------------------------

if args['generate_nav']:
    ux.header('Generate .nav.yml files for "awesome nav" plugin...')

    summary_nav_yml.generate_nav_ymls(docs_target_dir,
                                      include_star=True,
                                      always_use_titles=False)

# COPY AND RENAME ASSETS -------------------------------------------------------

ux.header('Copy and rename assets...')

fileman.write_assets_json(docs_source_dir, assets_dict)

ux.print(f'\nFound {len(assets_dict)} assets')

fileman.copy_assets(assets_dict, full_asset_sourcedir, full_asset_targetdir)


# FINISHING TOUCHES ------------------------------------------------------------

ux.header('Finishing touches...')

fileman.copy_extra_files(docs_target_dir, extra_source_dir)


ux.print("Done!")
