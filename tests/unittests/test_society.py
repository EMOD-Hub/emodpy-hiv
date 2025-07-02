import unittest
import pytest
import sys
from pathlib import Path

from emodpy_hiv.demographics.concurrency_parameters import ConcurrencyParameters
from emodpy_hiv.demographics.pair_formation_parameters import PairFormationParameters
from emodpy_hiv.demographics.relationship_parameters import RelationshipParameters
from emodpy_hiv.demographics.relationship_types import RelationshipTypes
from emodpy_hiv.demographics.society import Society

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))


@pytest.mark.unit
class HIVDemographicsTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_relationship_types(self):
        # ensure all relationship types are reported, even if not all of pfp/cp/rp parameters are set for all
        rp = {RelationshipTypes.commercial.value: RelationshipParameters()}
        pfp = {RelationshipTypes.commercial.value: PairFormationParameters(), RelationshipTypes.informal.value: PairFormationParameters}
        cp = {RelationshipTypes.transitory.value: {'LOW': ConcurrencyParameters()}}
        society = Society(relationship_parameters=rp, pair_formation_parameters=pfp, concurrency_parameters=cp)

        expected_types = {RelationshipTypes.commercial.value, RelationshipTypes.informal.value, RelationshipTypes.transitory.value}
        self.assertEqual(society.relationship_types, expected_types)


if __name__ == '__main__':
    unittest.main()
