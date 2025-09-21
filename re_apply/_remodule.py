import re

class ReModule:
    name = '_default'
    pattern:re.Pattern[str] = re.compile('')

    def apply(self, filedata:str) -> str:
        return self.pattern.sub(self.handler, filedata)
    
    @staticmethod
    def handler(match:re.Match[str]) -> str:
        return match.string