from .._remodule import *

# Make sure indents in quotes are properly indented using spaces
# --------- replace ---------
# >     tal = slump()
# ---------- with -----------
# > &nbsp;&nbsp;&nbsp;&nbsp;tal = slump()


class Plugin (ReModule):
    name = 'mark'
    pattern = [re.compile(r'> (?P<indent> *)(?P<content>.+)')]

    def handler(self, match: re.Match[str]) -> str:
        quote_indent = str(match.group('indent'))
        quote_content = str(match.group('content'))

        quote_indent = '&nbsp;' * len(quote_indent)

        return f'> {quote_indent}{quote_content}'
