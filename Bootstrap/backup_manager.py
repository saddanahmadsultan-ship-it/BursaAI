from pathlib import Path
import shutil,datetime

class ReleaseBackupManager:
    def create_backup(self,source,backup_root="Backups"):
        source=Path(source)
        backup=Path(backup_root)/(source.name+"_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        shutil.copytree(source,backup)
        return str(backup)
    def rollback(self,backup,target):
        backup=Path(backup); target=Path(target)
        if target.exists(): shutil.rmtree(target)
        shutil.copytree(backup,target)
        return str(target)
