import re


class ReModule:
    name = '_default'
    # pattern: re.Pattern[str] = re.compile('')
    pattern: list[re.Pattern[str]] = []

    def __init__(self):
        self.local_dict: dict[str, object] = {}

    def apply(self, filedata: str) -> str:
        for p in self.pattern:
            filedata = p.sub(self.handler, filedata)
            
        return filedata

    def handler(self, match: re.Match[str]) -> str:
        return match[0]
