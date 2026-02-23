from typing import Dict

from emod_api.demographics.updateable import Updateable


class CondomUsageParameters(Updateable):
    def __init__(self,
                 min: float = 0,
                 mid: float = 0,
                 max: float = 0,
                 rate: float = 0):
        """
            Parameterizes condom usage over time, a component of EMOD relationship parameters.

            https://docs.idmod.org/projects/emod-hiv/en/latest/sti-model-relationships.html#condom-usage
            https://docs.idmod.org/projects/emod-hiv/en/latest/parameter-demographics.html#relationship-parameters

            Args:
                min: minimum condom usage probability (pre-inflection point)
                mid: inflection point in condom usage (a year)
                max: maximum condom usage probability (post-inflection point)
                rate: slope of condom usage at inflection point
        """
        super().__init__()
        self.min = min
        self.mid = mid
        self.max = max
        self.rate = rate

    def to_dict(self) -> Dict:
        usage = {
            'Min': self.min,
            'Mid': self.mid,
            'Max': self.max,
            'Rate': self.rate
        }
        return usage

    @classmethod
    def from_dict(cls, d: Dict) -> '__class__':
        return cls(min=d['Min'], mid=d['Mid'], max=d['Max'], rate=d['Rate'])
