from ._remodule import *

# replace gitbook code blocks to mkdocs-compatible format. e.g.
# --------- replace ---------
# {% code title="filename.cs" lineNumbers="true" %}
# ``` csharp
#  some code
# ```
# {% endcode %}
# ---------- with -----------
# ``` csharp title="filename.cs" linenums="1"
# some code
# ```

class Plugin (ReModule):
    name = 'code'
    pattern:re.Pattern[str] = re.compile(r'{% code ?(?:title=\"(?P<title>.*?)\" )?(?:lineNumbers=\"?(?P<linenums>.*?)\" )?%}\n```(?P<language>.*?)?\n(?P<code>.*|[\s\S]+?)```\n{% endcode %}')
        
    @staticmethod
    def handler(match:re.Match[str]) -> str:
        code_title = f" title=\"{match.group('title')}\"" if match.group(
            'title') else ""
        code_lineNumbers = " linenums=\"1\"" if match.group(
            'linenums') == "true" else ""
        code_language = match.group(
            'language') if match.group('language') else ""
        code_actual_code = match.group('code')

        return f"``` {code_language}{code_title}{code_lineNumbers}\n{code_actual_code}```"