import copy
from datetime import datetime, timezone
import hashlib
import json
import unittest
from scripts.verify_live_rankings import verify_inseason


class VerifyInseasonTests(unittest.TestCase):
    def setUp(self):
        positions=('QB','RB','WR','TE')
        rows=[dict(player_id=str(i),position=positions[i%4],rank=i+1,position_rank=i//4+1,
                   projected_points=100-i,projected_ppg=10,team='BUF',rationale='Observed baseline') for i in range(40)]
        self.data=dict(release_status='validated_experimental',schema_version='1.0',model_version='v1',season=2026,
                       source_cutoff='Week 2 observed games',coverage_warnings=['One game pending'],as_of_week=2,target_week=3,
                       generated_at=datetime.now(timezone.utc).isoformat(),profiles={},aggregate_validation={})
        for profile in ('standard','ppr','half_ppr','gng_keeper'):
            self.data['profiles'][profile]={'weekly':copy.deepcopy(rows),'ros':copy.deepcopy(rows)}
            self.data['aggregate_validation'][profile]={'weekly':{'validated':True},'ros':{'validated':True}}

    def verify(self):
        raw=json.dumps(self.data).encode()
        return verify_inseason(raw,dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),source_generated_at=self.data['generated_at']))

    def test_verified_release_retains_coverage_warning(self):
        self.assertEqual(self.verify()['coverage_warnings'],['One game pending'])

    def test_missing_horizon_and_failed_gate_are_rejected(self):
        self.data['profiles']['standard'].pop('ros')
        with self.assertRaises(ValueError):self.verify()
        self.setUp();self.data['aggregate_validation']['ppr']['weekly']['validated']=False
        with self.assertRaises(ValueError):self.verify()

    def test_bad_identity_order_and_nonfinite_projection_rejected(self):
        for field,value in [('player_id',''),('rank',2),('projected_points',float('nan'))]:
            self.setUp();self.data['profiles']['ppr']['weekly'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):self.verify()

    def test_unreviewed_release_rejected(self):
        self.data['release_status']='candidate'
        with self.assertRaises(ValueError):self.verify()
