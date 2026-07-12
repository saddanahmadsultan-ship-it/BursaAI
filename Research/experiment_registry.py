from __future__ import annotations
import json,os,time
from contextlib import contextmanager
from pathlib import Path
from Research.candidate import utc_now_iso
from Research.checkpoint import CheckpointManager
from Research.enums import ExperimentStatus
from Research.experiment import Experiment
class RegistryError(RuntimeError):pass
class ExperimentRegistry:
    def __init__(self,base_dir='Experiments'):
        self.base_dir=Path(base_dir);self.records_dir=self.base_dir/'records';self.checkpoints_dir=self.base_dir/'checkpoints';self.locks_dir=self.base_dir/'locks'
        for p in (self.base_dir,self.records_dir,self.checkpoints_dir,self.locks_dir):p.mkdir(parents=True,exist_ok=True)
        self.manifest_path=self.base_dir/'registry_manifest.json';self.checkpoints=CheckpointManager(self.checkpoints_dir)
        if not self.manifest_path.exists():self._write_manifest({'schema_version':1,'experiments':{}})
    def _record_path(self,eid):return self.records_dir/f'{eid}.json'
    def _read_manifest(self):
        try:
            d=json.loads(self.manifest_path.read_text(encoding='utf-8'));d.setdefault('experiments',{});return d
        except Exception as e:raise RegistryError(f'Manifest rosak: {e}') from e
    def _write_manifest(self,d):
        d['schema_version']=1;d['updated_at']=utc_now_iso();tmp=self.manifest_path.with_suffix('.json.tmp');payload=json.dumps(d,indent=2,ensure_ascii=False,sort_keys=True)
        with open(tmp,'w',encoding='utf-8') as f:f.write(payload);f.flush();os.fsync(f.fileno())
        os.replace(tmp,self.manifest_path)
    @contextmanager
    def _lock(self,eid,timeout_seconds=5.0):
        p=self.locks_dir/f'{eid}.lock';start=time.monotonic()
        while True:
            try:
                fd=os.open(str(p),os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,f'{os.getpid()}|{utc_now_iso()}'.encode());os.close(fd);break
            except FileExistsError:
                if time.monotonic()-start>=timeout_seconds:raise RegistryError(f'Lock timeout: {eid}')
                time.sleep(.05)
        try:yield
        finally:
            if p.exists():p.unlink()
    @staticmethod
    def _entry(e):return {'experiment_id':e.experiment_id,'name':e.name,'status':e.status.value,'mode':e.mode.value,'search_method':e.search_method.value,'total_candidates':e.total_candidates,'completed_candidates':e.completed_candidates,'failed_candidates':e.failed_candidates,'progress_percentage':e.progress_percentage(),'created_at':e.created_at,'updated_at':e.updated_at,'started_at':e.started_at,'completed_at':e.completed_at,'record_file':f'records/{e.experiment_id}.json','checkpoint_file':f'checkpoints/{e.experiment_id}.checkpoint.json'}
    def register(self,e,overwrite=False):
        if not isinstance(e,Experiment):raise TypeError('experiment mesti Experiment.')
        with self._lock(e.experiment_id):
            p=self._record_path(e.experiment_id)
            if p.exists() and not overwrite:raise RegistryError(f'Experiment sudah didaftarkan: {e.experiment_id}')
            e.save_json(p);m=self._read_manifest();m['experiments'][e.experiment_id]=self._entry(e);self._write_manifest(m);self.checkpoints.save(e,'register');return p
    def save(self,e,checkpoint_reason='update'):
        with self._lock(e.experiment_id):
            p=self._record_path(e.experiment_id)
            if not p.exists():raise RegistryError('Experiment belum didaftarkan.')
            e.save_json(p);m=self._read_manifest();m['experiments'][e.experiment_id]=self._entry(e);self._write_manifest(m);self.checkpoints.save(e,checkpoint_reason);return p
    def load(self,eid,prefer_checkpoint=False):
        if prefer_checkpoint and self.checkpoints.exists(eid):return self.checkpoints.load(eid)
        p=self._record_path(eid)
        if not p.exists():raise FileNotFoundError(f'Experiment tidak ditemui: {eid}')
        return Experiment.load_json(p)
    def recover(self,eid):
        e=self.checkpoints.load(eid)
        if e.status==ExperimentStatus.RUNNING:e.status=ExperimentStatus.PAUSED;e.metadata['recovered_from_interruption']=True;e.metadata['recovered_at']=utc_now_iso();e._touch()
        self.save(e,'recovery');return e
    def list(self,status=None):
        items=list(self._read_manifest()['experiments'].values())
        if status is not None:
            v=status.value if isinstance(status,ExperimentStatus) else str(status);items=[x for x in items if x.get('status')==v]
        return sorted(items,key=lambda x:x.get('updated_at',''),reverse=True)
    def pause(self,eid):e=self.load(eid);e.pause();self.save(e,'pause');return e
    def resume(self,eid):e=self.load(eid);e.resume();self.save(e,'resume');return e
    def cancel(self,eid):e=self.load(eid);e.cancel();self.save(e,'cancel');return e
    def create_checkpoint(self,eid,reason='manual'):return self.checkpoints.save(self.load(eid),reason)
    def delete(self,eid,delete_checkpoint=True):
        with self._lock(eid):
            p=self._record_path(eid);existed=p.exists()
            if p.exists():p.unlink()
            if delete_checkpoint:self.checkpoints.delete(eid)
            m=self._read_manifest();m['experiments'].pop(eid,None);self._write_manifest(m);return existed
    def rebuild_manifest(self):
        exps={};count=0
        for p in self.records_dir.glob('EXP-*.json'):
            try:e=Experiment.load_json(p);exps[e.experiment_id]=self._entry(e);count+=1
            except Exception:pass
        self._write_manifest({'schema_version':1,'experiments':exps});return count
