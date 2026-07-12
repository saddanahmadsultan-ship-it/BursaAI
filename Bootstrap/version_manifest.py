from dataclasses import dataclass,asdict
from typing import Dict,List

@dataclass
class VersionManifest:
    app_name:str="BursaAI"
    version:str="6.0"
    release:str="Sprint 6G.5"
    modules:List[str]=None
    def to_dict(self):
        d=asdict(self)
        d["modules"]=self.modules or []
        return d
