from .._remodule import *

# Make sure tags are properly escaped
# --------- replace ---------
# \<h1>Heading\</h1>
# ---------- with -----------
# <h1\>Heading</h1\>

class Plugin (ReModule):
    name = 'tag'
    pattern = [re.compile(r'\\<(?P<tagname>.*?)>')]
        
    def handler(self, match:re.Match[str]) -> str:
        tag_name = str(match.group('tagname'))
        whitelist_tags = ['br', 'p']
        
        if tag_name in whitelist_tags:
            return match.string
        
        return f'<{tag_name}\\>'