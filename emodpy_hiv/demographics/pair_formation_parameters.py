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
        PairFormationParameters defines the rate at which new relationships are formed and partnership
        preference using the main pair forming algorithm that finds potential partners based on their
        age and the Joint_Probabilities matrix.

        Args:
            Assortivity (AssortivityClass): Defines how people will preferentially form pairs based on their membership in different groups.
            Formation_Rate_Constant (float): If Formation_Rate_Type is set to CONSTANT, the number of new relationships per day for this relationship type.
            Age_of_First_Bin_Edge_Female (int): The maximum age for the first age bin when dividing the female population into age bins for pair formation.
            Age_of_First_Bin_Edge_Male (int): The maximum age for the first age bin when dividing the male population into age bins for pair formation.
            Extra_Relational_Rate_Ratio_Female (int): For women, the rate ratio for having extra-relational sex for this relationship type,
                where the ratio is the event over the period of time defined in Update_Period.
            Extra_Relational_Rate_Ratio_Male (int): For males, the rate ratio for having extra-relational sex for this relationship type,
                where the ratio is the event over the period of time defined in Update_Period.
            Number_Age_Bins_Female (int): The number of age bins to divide the female population into for pair formation.
            Number_Age_Bins_Male (int): The number of age bins to divide the male population into for pair formation.
            Update_Period (float): The period, in days, to wait before an individual is eligible to seek out new relationships.
            Years_Between_Bin_Edges_Female (float): For the female population, the number of years covered in each age bin.
            Years_Between_Bin_Edges_Male (float): For the male population, the number of years covered in each age bin.
            Joint_Probabilities (List[List[float]]): The relative preference of members of one age bin to form relationships
                with members of another age bin. The columns represent female bins and rows represent male bins.
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
