"""Meaningful data-construction invariants; no model/API calls."""
import json
import unittest
from collections import Counter

from experiments.v3.prepare_api_dataset import controlled_scenario, prompt_row, geometry, FAMILIES, ROOT, validate_reference_semantics, validate_required_support
from experiments.v3.runtime.dataset import audit_scenario_specification


class DatasetPlanTests(unittest.TestCase):
    def test_ids_splits_and_closed_labels(self):
        seen=set()
        for family in range(1,25):
            for variant in range(1,6):
                s=controlled_scenario(family,variant)
                audit_scenario_specification(s)
                validate_reference_semantics(s)
                validate_required_support(s)
                self.assertNotIn(s['image_id'],seen)
                seen.add(s['image_id'])
                self.assertEqual(s['split'],'development' if family<=12 else 'validation')
                self.assertLessEqual(len(s['reference_entities']),4)
        self.assertEqual(len(seen),120)

    def test_every_planned_support_type_has_reference(self):
        layout=json.loads((ROOT/'experiments/v3/config/preregistration_v3_1.json').read_text())['dataset_support']['validation_plan_each_stratum']
        for f in range(1,25):
            for v in range(1,6):
                s=controlled_scenario(f,v)
                counts=Counter(a['atom_type'] for a in s['reference_atoms'])
                local=(f-1)%12+1
                for kind,rule in layout.items():
                    lo,hi=(int(x[1:]) for x in rule['families'].split('-'))
                    if lo<=local<=hi:
                        self.assertGreaterEqual(counts[kind],rule['per_contributing_image']['positive'],(s['image_id'],kind))

    def test_naturalistic_plan_is_not_reference(self):
        signatures={}
        for f in range(1,25):
            row=prompt_row(f,1)
            self.assertNotIn('reference_entities',row)
            self.assertNotIn('reference_atoms',row)
            self.assertEqual(row['seed'],925031+100*f+1)
            signature=FAMILIES[f-1]
            self.assertNotIn(signature,signatures)
            signatures[signature]=f

    def test_geometry_is_derived_not_prompted(self):
        e=[{'reference_id':'r1','category':'book','bbox_xyxy':[.1,.1,.2,.2]},
           {'reference_id':'r2','category':'cup','bbox_xyxy':[.7,.7,.9,.9]}]
        facts={(x['value'],x['source_reference_id'],x['target_reference_id']) for x in geometry(e)}
        self.assertIn(('left_of','r1','r2'),facts)
        self.assertIn(('above','r1','r2'),facts)
        self.assertNotIn(('overlap','r1','r2'),facts)

    def test_reference_authoring_rejects_inconsistent_count_or_geometry(self):
        for kind in ['count','geometry_relation']:
            s=controlled_scenario(1,1)
            row=next(a for a in s['reference_atoms'] if a['atom_type']==kind)
            row['value']='2' if kind=='count' else 'inside'
            with self.assertRaises(ValueError): validate_reference_semantics(s)

    def test_missing_planned_fact_is_a_shortfall_not_a_fabricated_reference(self):
        s=controlled_scenario(1,1)
        s['reference_atoms']=[a for a in s['reference_atoms'] if a['atom_type']!='binary_interaction']
        with self.assertRaisesRegex(ValueError,'missing planned visible support'):
            validate_required_support(s)


if __name__=='__main__': unittest.main()
