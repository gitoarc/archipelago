from __future__ import annotations
import json
import os.path
import re


class JsonParsed:
    IdStr:str
    Label:str
    Preface:str
    Category: int
    Aspects:dict[str, int]
    ConnectsTo:list[JsonParsed]
    Requires:dict[str, int]
    Rewards_Vanilla_to_IdStr:dict[str,str] # used by books

    def __init__(self, obj:dict[str, any]):
        self.IdStr = obj["IdStr"]
        self.Label = obj["Label"]
        self.Category = obj["Category"]
        self.Aspects = dict.get(obj, "Aspects", {})
        self.ConnectsTo = [JsonParsed(c) for c in dict.get(obj, "ConnectsTo", [])]
        self.TerrainUnlockRequirement = dict.get(obj,"Requires", {})
        self.Preface = dict.get(obj,"Preface", self.Label)
        self.Rewards_Vanilla_to_IdStr = dict.get(obj, "Rewards", {})
        pass

    def __repr__(self):
        return self.Label

    def contains_substr(self, s:str, check_connections:bool = False):
        b = (s in self.IdStr
                or s in self.Label
                or s in self.Preface
                or any([True for k in self.Aspects if s in k])
                or any([True for k in self.TerrainUnlockRequirement if s in k])
                or s in self.Rewards_Vanilla_to_IdStr
                )
        if b is False and check_connections:
            for c in self.ConnectsTo:
                b = b or c.contains_substr(s) # do not recurse
        return b


class SimplePredicate:
    All = False
    Any = False
    comparer:str
    number:int

    def __init__(self, s:str):
        slicedByMiddle = re.split("<|<=|==|>=|>", s)
        slice1 = slicedByMiddle[0]
        slice3 = slicedByMiddle[1] if len(slicedByMiddle) > 1 else "0"
        slice2 = s.replace(slice1, "").replace(slice3, "")
        if slice2 == "":
            pass

        self.All = slice1 == "all"
        self.Any = slice1 == "any"
        self.comparer = slice2
        self.number = int(slice3)

    def use_comparer(self, i:int) -> bool:
        if self.comparer == "<": return i < self.number
        if self.comparer == "<=": return i <= self.number
        if self.comparer == "==": return i == self.number
        if self.comparer == ">=": return i >= self.number
        if self.comparer == ">": return i > self.number
        return NotImplemented

    # to use on Aspect / requirements dict
    # [a for a in list:JsonParsed if evaluate_on_dict(a.Aspect)]
    def evaluate_on_dict(self, dic:dict[str, int]) -> bool:
        if len(dic) == 0: return False

        score = 0
        compar = self.use_comparer
        for v in dic.values():
            if compar(v):
                score += 1
        if self.All: return score == len(dic)
        elif self.Any: return score > 0
        return False

    def __repr__(self):
        quan = "ERROR"
        if self.All:
            quan = "All"
        elif self.Any:
            quan = "Any"

        return f"{quan} {self.comparer} {self.number}"


memories:list[JsonParsed]=[]
souls:list[JsonParsed]=[]
terrains:list[JsonParsed]=[]
books:list[JsonParsed]=[]
wisdomtree:list[JsonParsed]=[]
lessons:list[JsonParsed]=[]
skills:list[JsonParsed]=[]

with open(os.path.join(__file__, "..", 'dump.json'), mode='r', encoding='utf-8') as f:
    data = json.load(f)
    for a in data:
        j = JsonParsed(a)
        match j.Category:
            case 1: memories.append(j);
            case 2: souls.append(j);
            case 3: terrains.append(j);
            case 4: wisdomtree.append(j);
            case 5: books.append(j);
            case 6: lessons.append(j);
            case 7: skills.append(j);

memories_basic = [a for a in memories if "mem." in a.IdStr]
memories_basic_daily_weather = [a for a in memories if "weather" in a.Aspects and not "quake" in a.IdStr]
memories_music = [a for a in memories if "sound" in a.Aspects]
memories_persistent = [a for a in memories if "persistent" in a.Aspects]
memories_leftovers = [a for a in memories if a not in memories_basic and a not in memories_basic_daily_weather
                      and a not in memories_music and a not in memories_persistent]
memories_pre_house = memories_basic + memories_basic_daily_weather
memories_post_house = [a for a in memories if a not in memories_pre_house]
###################
#memories += lessons

everything = memories + souls + terrains + books + wisdomtree + lessons + skills

# more background than game element, also: can not be interacted with, so its best to fire and fhuget abbat id
terrains = [a for a in terrains if a.Label != "The Atlantic Ocean"]
