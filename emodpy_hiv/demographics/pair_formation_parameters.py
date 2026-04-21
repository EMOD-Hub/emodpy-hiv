from typing import Dict, List

from emod_api.demographics.updateable import Updateable

from emodpy_hiv.demographics.assortivity import Assortivity as AssortivityClass


class PairFormationParameters(Updateable):
    def __init__(self,
                 Assortivity: AssortivityClass = None,
                 Formation_Rate_Constant: float = None,
                 Age_of_First_Bin_Edge_Female: int = None,
                 Age_of_First_Bin_Edge_Male: int = None,
                 Extra_Relational_Rate_Ratio_Female: int = None,
                 Extra_Relational_Rate_Ratio_Male: int = None,
                 Number_Age_Bins_Female: int = None,
                 Number_Age_Bins_Male: int = None,
                 Update_Period: float = None,
                 Years_Between_Bin_Edges_Female: float = None,
                 Years_Between_Bin_Edges_Male: float = None,
                 Joint_Probabilities: List[List[float]] = None):
        """
        https://emod.idmod.org/emodpy-hiv/emod/parameter-demographics.html#pair-formation-parameters

        Args:
            Assortivity:
            Formation_Rate_Constant:
            Age_of_First_Bin_Edge_Female:
            Age_of_First_Bin_Edge_Male:
            Extra_Relational_Rate_Ratio_Female:
            Extra_Relational_Rate_Ratio_Male:
            Number_Age_Bins_Female:
            Number_Age_Bins_Male:
            Update_Period:
            Years_Between_Bin_Edges_Female:
            Years_Between_Bin_Edges_Male:
            Joint_Probabilities:
        """
        super().__init__()
        self.Assortivity = Assortivity if Assortivity is not None else AssortivityClass()
        self.Formation_Rate_Constant = Formation_Rate_Constant
        self.Age_of_First_Bin_Edge_Female = Age_of_First_Bin_Edge_Female
        self.Age_of_First_Bin_Edge_Male = Age_of_First_Bin_Edge_Male
        self.Extra_Relational_Rate_Ratio_Female = Extra_Relational_Rate_Ratio_Female
        self.Extra_Relational_Rate_Ratio_Male = Extra_Relational_Rate_Ratio_Male
        self.Number_Age_Bins_Female = Number_Age_Bins_Female
        self.Number_Age_Bins_Male = Number_Age_Bins_Male
        self.Update_Period = Update_Period
        self.Years_Between_Bin_Edges_Female = Years_Between_Bin_Edges_Female
        self.Years_Between_Bin_Edges_Male = Years_Between_Bin_Edges_Male
        self.Joint_Probabilities = Joint_Probabilities

    def to_dict(self) -> Dict:
        parameters = {
            'Formation_Rate_Type': 'CONSTANT',
        }
        for var, value in vars(self).items():
            parameters[var] = value.to_dict() if hasattr(value, 'to_dict') else value
        return parameters

    @classmethod
    def from_dict(cls, d: Dict) -> '__class__':
        assortivity = d.get('Assortivity', None)
        assortivity = None if assortivity is None else AssortivityClass.from_dict(d=assortivity)
        return cls(Assortivity=assortivity,
                   Formation_Rate_Constant=d.get('Formation_Rate_Constant', None),
                   Age_of_First_Bin_Edge_Female=d.get('Age_of_First_Bin_Edge_Female', None),
                   Age_of_First_Bin_Edge_Male=d.get('Age_of_First_Bin_Edge_Male', None),
                   Extra_Relational_Rate_Ratio_Female=d.get('Extra_Relational_Rate_Ratio_Female', None),
                   Extra_Relational_Rate_Ratio_Male=d.get('Extra_Relational_Rate_Ratio_Male', None),
                   Number_Age_Bins_Female=d.get('Number_Age_Bins_Female', None),
                   Number_Age_Bins_Male=d.get('Number_Age_Bins_Male', None),
                   Update_Period=d.get('Update_Period', None),
                   Years_Between_Bin_Edges_Female=d.get('Years_Between_Bin_Edges_Female', None),
                   Years_Between_Bin_Edges_Male=d.get('Years_Between_Bin_Edges_Male', None),
                   Joint_Probabilities=d.get('Joint_Probabilities', None))
