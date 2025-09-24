import re


class ReModule:
    name = '_default'
    pattern: re.Pattern[str] = re.compile('')

    def __init__(self):
        self.local_dict: dict[str, object] = {}

    def apply(self, filedata: str) -> str:
        return self.pattern.sub(self.handler, filedata)

    def handler(self, match: re.Match[str]) -> str:
        return match[0]
