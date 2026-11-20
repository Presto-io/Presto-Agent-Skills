#!/usr/bin/env python3
"""Synthetic integration tests; no production files or network access."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('sync', Path(__file__).with_name('skill_sync.py'))
s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)

class SyncTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.remote = self.root/'remote.git'
        self.git('init','--bare','--initial-branch=main',str(self.remote))
        seed = self.root/'seed'; self.git('clone',str(self.remote),str(seed))
        skill=seed/'skills/sample'; skill.mkdir(parents=True)
        (skill/'SKILL.md').write_text('---\nname: sample\ndescription: Synthetic test\n---\n')
        (skill/'data.txt').write_text('one\n'+'unchanged\n'*10+'last\n')
        (skill/'image.bin').write_bytes(b'\x00image')
        self.git('-C',str(seed),'add','.');self.git('-C',str(seed),'commit','-m','seed');self.git('-C',str(seed),'push','origin','main')
        self.ends=[]
        for n in ['a','b']:
            root=self.root/n;root.mkdir();shutil.copytree(skill,root/'sample')
            config=self.root/(n+'.json')
            s.dump(config,{'state_dir':str(self.root/(n+'-state')),'roots':[{'path':str(root),'install_missing':True}]})
            self.ends.append({'id':n,'config':str(config)})
        self.config={'state_dir':str(self.root/'controller'),'repository':str(self.remote),'endpoints':self.ends,'resolution_file':str(self.root/'resolve.json')}
    def git(self,*args):
        return subprocess.check_output(['git','-c','user.name=Test','-c','user.email=test@example.invalid',*args],stderr=subprocess.DEVNULL)
    def edit(self,side,filename,data):
        p=self.root/side/'sample'/filename
        p.write_bytes(data if isinstance(data,bytes) else data.encode())
    def head(self):return self.git('--git-dir='+str(self.remote),'rev-parse','main')
    def test_roundtrip_and_nonoverlap(self):
        self.assertEqual(s.fleet(self.config)['status'],'complete')
        self.edit('a','data.txt','ONE\n'+'unchanged\n'*10+'last\n')
        self.edit('b','data.txt','one\n'+'unchanged\n'*10+'LAST\n')
        result=s.fleet(self.config); self.assertEqual(result['changed_skills'],['sample'])
        self.assertEqual((self.root/'a/sample/data.txt').read_text(),'ONE\n'+'unchanged\n'*10+'LAST\n')
        self.assertEqual(s.snapshot(self.root/'a/sample'),s.snapshot(self.root/'b/sample'))
        self.assertEqual(s.fleet(self.config)['changed_skills'],[])
    def test_overlap_and_explicit_resolution(self):
        s.fleet(self.config); before=self.head()
        self.edit('a','data.txt','A\n');self.edit('b','data.txt','B\n')
        with self.assertRaises(s.Blocked):s.fleet(self.config)
        self.assertEqual(self.head(),before)
        report=s.load(s.load(self.root/'controller/last-result.json')['report'])
        s.dump(self.root/'resolve.json',{c['id']:{'take':'local'} for c in report})
        self.assertEqual(s.fleet(self.config)['status'],'complete')
        self.assertEqual((self.root/'a/sample/data.txt').read_text(),'B\n')
    def test_binary_conflict(self):
        s.fleet(self.config);before=self.head()
        self.edit('a','image.bin',b'\x00A');self.edit('b','image.bin',b'\x00B')
        with self.assertRaises(s.Blocked):s.fleet(self.config)
        self.assertEqual(before,self.head())
    def test_initial_drift_and_private(self):
        self.edit('a','data.txt','unreviewed')
        with self.assertRaises(s.Blocked):s.fleet(self.config)
        conf=s.load(self.ends[0]['config'])
        with self.assertRaises(s.Blocked):s.endpoint_export(conf,{'names':['uws-workspace']})
        with self.assertRaises(s.Blocked):s.endpoint_export(conf,{'names':['jiaoan-jihua']})
    def test_cas_and_rename_failure_keep_original(self):
        conf=s.load(self.ends[0]['config']); blobs={};target=self.root/'a/sample'
        before=s.snapshot(target,blobs); desired=dict(before)
        data=b'updated';sha=s.digest(data);blobs[sha]=data;desired['data.txt']={'sha':sha,'mode':420}
        req={'actions':[{'root':str(self.root/'a'),'name':'sample','expected':before,'tree':desired}],'blobs':{k:s.base64.b64encode(v).decode() for k,v in blobs.items()}}
        original=s.os.replace
        def fail_source(src,dst):
            if Path(src)==target:raise OSError('injected rename failure')
            return original(src,dst)
        with patch.object(s.os,'replace',fail_source):
            with self.assertRaises(OSError):s.endpoint_apply(conf,req)
        self.assertEqual(s.snapshot(target),before)
        self.edit('a','data.txt','concurrent')
        with self.assertRaises(s.Blocked):s.endpoint_apply(conf,req)
        self.assertEqual((target/'data.txt').read_text(),'concurrent')
    def test_second_target_failure_rolls_back(self):
        conf=s.load(self.ends[0]['config']);second=self.root/'extra';second.mkdir();shutil.copytree(self.root/'a/sample',second/'sample')
        conf['roots'].append({'path':str(second)})
        blobs={};before=s.snapshot(self.root/'a/sample',blobs); desired=dict(before)
        sha=s.digest(b'new');blobs[sha]=b'new';desired['data.txt']={'sha':sha,'mode':420}
        actions=[{'root':str(r),'name':'sample','expected':before,'tree':desired} for r in [self.root/'a',second]]
        original=s.os.replace
        def fail(src,dst):
            if Path(src)==second/'sample':raise OSError('injected second failure')
            return original(src,dst)
        with patch.object(s.os,'replace',fail):
            with self.assertRaises(OSError):s.endpoint_apply(conf,{'actions':actions,'blobs':{k:s.base64.b64encode(v).decode() for k,v in blobs.items()}})
        self.assertEqual(s.snapshot(self.root/'a/sample'),before);self.assertEqual(s.snapshot(second/'sample'),before)
    def test_offline_stops_before_push(self):
        s.fleet(self.config);self.edit('a','data.txt','edited');before=self.head()
        self.config['endpoints'].append({'id':'offline','command':['false']})
        with self.assertRaises(s.Blocked):s.fleet(self.config)
        self.assertEqual(before,self.head());self.assertEqual((self.root/'a/sample/data.txt').read_text(),'edited')

    def test_push_race_recollects_and_merges(self):
        s.fleet(self.config);self.edit('a','data.txt','ONE\n'+'unchanged\n'*10+'last\n')
        original=s.git; injected=[False]
        def racing(repo,*args):
            if args and args[0]=='push' and not injected[0]:
                injected[0]=True
                seed=self.root/'seed'
                (seed/'skills/sample/remote.txt').write_text('concurrent GitHub change')
                self.git('-C',str(seed),'add','.');self.git('-C',str(seed),'commit','-m','race');self.git('-C',str(seed),'push','origin','main')
            return original(repo,*args)
        with patch.object(s,'git',racing):result=s.fleet(self.config)
        self.assertEqual(result['status'],'complete')
        self.assertTrue((self.root/'a/sample/remote.txt').exists())
        self.assertTrue((self.root/'a/sample/data.txt').read_text().startswith('ONE'))

    def test_apply_reuses_verified_local_assets(self):
        conf=s.load(self.ends[0]['config']);target=self.root/'a/sample';before=s.snapshot(target)
        desired=dict(before);data=b'only changed bytes travel';sha=s.digest(data)
        desired['data.txt']={'sha':sha,'mode':420}
        result=s.endpoint_apply(conf,{'actions':[{'root':str(self.root/'a'),'name':'sample','expected':before,'tree':desired}],'blobs':{sha:s.base64.b64encode(data).decode()}})
        self.assertEqual(result['status'],'applied');self.assertEqual(s.snapshot(target),desired)

if __name__=='__main__':unittest.main(verbosity=2)
