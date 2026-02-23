from typing import List, Dict

from emod_api.demographics.updateable import Updateable


# TODO: should we drop NO_GROUP support altogether? If so, group is always INDIVIDUAL_PROPERTY and the instantiation
#  argument should be removed. If NOT, then we need to ensure that an inconsistent state is not possible if calling
#  code toggles "things" e.g. group = 'NO_GROUP' and property_name = 'Risk'
#  https://github.com/InstituteforDiseaseModeling/emodpy-hiv/issues/216

class Assortivity(Updateable):
    def __init__(self,
                 matrix: List[List[float]] = None,
                 group: str = "INDIVIDUAL_PROPERTY"):
        super().__init__()
        self.axes = ['LOW', 'MEDIUM', 'HIGH']
        self.group = group
        self.property_name = 'Risk'
        self.matrix = matrix  # a None matrix is valid if group is 'NO_GROUP'

    def to_dict(self) -> Dict:
        assortivity = {
            'Axes': self.axes,
            'Group': self.group,
            'Property_Name': self.property_name
        }
        if self.matrix is not None:
            assortivity['Weighting_Matrix_RowMale_ColumnFemale'] = self.matrix

        return assortivity

    @classmethod
    def from_dict(cls, d: Dict) -> '__class__':
        keys_to_args = {'Group': 'group', 'Weighting_Matrix_RowMale_ColumnFemale': 'matrix'}
        kwargs = {arg: d[key] for key, arg in keys_to_args.items() if key in d}
        return cls(**kwargs)
