import re


class Testclass:
    def __init__(self) -> None:
        self.boom:list[int] = []
        pass
    
    def hey(self) -> None:
        self.boom.append(1)
    
    def handler(self, match: re.Match[str]):
        return match[0].upper()


t = Testclass()

g = [5,6,7]

t.boom = g

t.hey()

print(g)