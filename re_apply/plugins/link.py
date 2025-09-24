from .._remodule import *

# Make sure (local) links to folders go to README.md's, and fix anchors
# --------- replace ---------
#   [text][link_folder/]
#   [test][./#heading]
# ---------- with -----------
#   [text][link_folder/README.md]
#   [test][#heading]


class Plugin (ReModule):
    name = 'link'
    pattern = re.compile(r'\[(?P<text>.*?)\]\((?P<url>(?P<path>(?<=\().*?)(?P<filename>[^/\n\(]*?)?(?P<anchor>#.+?(?=\)))?\))')

    def handler(self, match: re.Match[str]) -> str:
        link_text = str(match.group('text'))
        link_url = str(match.group('url'))

        link_path = str(match.group('path')) if match.group('path') else ''
        link_filename = str(match.group('filename')
                            ) if match.group('filename') else ''
        link_anchor = str(match.group('anchor')) if match.group('anchor') else ''

        # Detect urls leading to local folders
        if not link_path.startswith('http'):

            # Add README to folder links
            if link_filename == '':
                link_filename = 'README.md'

            # Remove periods from anchors
            link_anchor = link_anchor.replace('.', '')

        link_url = link_path + link_filename + link_anchor

        return f'[{link_text}]({link_url})'
