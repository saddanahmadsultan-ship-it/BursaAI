from __future__ import annotations
import hashlib,json,os
from pathlib import Path
from Research.candidate import utc_now_iso
from Research.experiment import Experiment
class CheckpointError(RuntimeError):pass
class CheckpointManager:
    def __init__(self,checkpoint_dir):self.checkpoint_dir=Path(checkpoint_dir);self.checkpoint_dir.mkdir(parents=True,exist_ok=True)
    def checkpoint_path(self,eid):return self.checkpoint_dir/f'{eid}.checkpoint.json'
    def checksum_path(self,eid):return self.checkpoint_dir/f'{eid}.checkpoint.sha256'
    def save(self,experiment,reason='manual'):
        p=self.checkpoint_path(experiment.experiment_id);tmp=p.with_suffix(p.suffix+'.tmp');payload=json.dumps({'schema_version':1,'saved_at':utc_now_iso(),'reason':reason,'experiment':experiment.to_dict()},indent=2,ensure_ascii=False,sort_keys=True).encode()
        with open(tmp,'wb') as f:f.write(payload);f.flush();os.fsync(f.fileno())
        os.replace(tmp,p);self.checksum_path(experiment.experiment_id).write_text(hashlib.sha256(payload).hexdigest(),encoding='utf-8');return p
    def load(self,eid,verify_checksum=True):
        p=self.checkpoint_path(eid)
        if not p.exists():raise FileNotFoundError(f'Checkpoint tidak ditemui: {p}')
        payload=p.read_bytes()
        if verify_checksum:
            cp=self.checksum_path(eid)
            if not cp.exists() or cp.read_text(encoding='utf-8').strip()!=hashlib.sha256(payload).hexdigest():raise CheckpointError('Checksum checkpoint tidak sepadan.')
        d=json.loads(payload.decode())
        if d.get('schema_version')!=1:raise CheckpointError('Schema checkpoint tidak disokong.')
        return Experiment.from_dict(d['experiment'])
    def exists(self,eid):return self.checkpoint_path(eid).exists()
    def delete(self,eid):
        for p in (self.checkpoint_path(eid),self.checksum_path(eid)):
            if p.exists():p.unlink()
