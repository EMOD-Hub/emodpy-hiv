from typing import Dict

from emod_api.demographics.Updateable import Updateable


class ConcurrencyParameters(Updateable):
    def __init__(self,
                 probability_extra_relationship_male: float = 0,
                 probability_extra_relationship_female: float = 0,
                 max_simultaneous_relationships_male: float = 0,
                 max_simultaneous_relationships_female: float = 0):
        """
        A ConcurrencyParameters object represents the likelihood and maximum count of additional concurrent
        relationships for males and females in a simulation. One ConcurrencyParameters object typically is created
        per relationship type and risk group (e.g. one for Commercial HIGH risk relationships, one for
        Transitory MED risk relationships, etc.).

        https://docs.idmod.org/projects/emod-hiv/en/latest/parameter-demographics.html#concurrency-parameters

        Args:
            probability_extra_relationship_male: the probability of having extra relationships for males
            probability_extra_relationship_female: the probability of extra relationships for females
            max_simultaneous_relationships_male: the maximum simultaneous relationships for males
            max_simultaneous_relationships_female: the maximum simultaneous relationships for females
        """
        super().__init__()
        self.probability_extra_relationship_male   = probability_extra_relationship_male   # noqa: E221
        self.probability_extra_relationship_female = probability_extra_relationship_female
        self.max_simultaneous_relationships_male   = max_simultaneous_relationships_male   # noqa: E221
        self.max_simultaneous_relationships_female = max_simultaneous_relationships_female

    def to_dict(self) -> Dict:
        concurrency = { 'Prob_Extra_Relationship_Male':          self.probability_extra_relationship_male,   # noqa: E241
                        'Prob_Extra_Relationship_Female':        self.probability_extra_relationship_female, # noqa: E241
                        'Max_Simultaneous_Relationships_Male':   self.max_simultaneous_relationships_male,   # noqa: E241
                        'Max_Simultaneous_Relationships_Female': self.max_simultaneous_relationships_female }
        return concurrency

    @classmethod
    def from_dict(cls, d: Dict) -> '__class__':
        return cls(probability_extra_relationship_male  =d['Prob_Extra_Relationship_Male'         ], # noqa: E221, E251
                   probability_extra_relationship_female=d['Prob_Extra_Relationship_Female'       ], # noqa: E251
                   max_simultaneous_relationships_male  =d['Max_Simultaneous_Relationships_Male'  ], # noqa: E221, E251
                   max_simultaneous_relationships_female=d['Max_Simultaneous_Relationships_Female'])
