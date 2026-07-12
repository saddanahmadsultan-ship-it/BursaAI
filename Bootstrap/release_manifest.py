import json
from pathlib import Path
from Bootstrap.version_manifest import VersionManifest

class ReleaseManifestWriter:
    def write(self,manifest,output="Reports/Release/version_manifest.json"):
        p=Path(output); p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(manifest.to_dict(),indent=2),encoding="utf-8")
        return str(p)
