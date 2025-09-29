from .._remodule import *

# remove unnecessary <mark> tags around inline `code`
# --------- replace ---------
#   Type <mark style="color:orange;">`print()`</mark> to print
# ---------- with -----------
#   Type `print()` to print


class Plugin (ReModule):
    name = 'mark'
    pattern = [re.compile(r'<mark.*?>(?P<content>`.*?`)</mark>')]

    def handler(self, match: re.Match[str]) -> str:
        return match.group('content')
