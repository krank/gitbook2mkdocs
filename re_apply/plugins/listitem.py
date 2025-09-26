from .._remodule import *

# make sure lists have the right indent size
# (gitbook prefers 2x spaces, mkdocs 4x)
# --------- replace ---------
#   Type <mark style="color:orange;">`print()`</mark> to print
# ---------- with -----------
#   Type `print()` to print


class Plugin (ReModule):
    name = 'listitem'
    pattern = re.compile(r'(?P<indent>(?:  )*)(?P<prefix>[\*\+\-] |\d. )(?P<text>.*)')

    def handler(self, match: re.Match[str]) -> str:
        item_indent:str = match.group('indent')
        item_prefix:str = match.group('prefix')
        item_text:str = match.group('text')
        
        item_indent *= 2
        
        return f'{item_indent}{item_prefix}{item_text}'
