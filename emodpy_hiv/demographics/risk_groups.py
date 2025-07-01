from enum import Enum


class RiskGroups(Enum):
    """
    Aid to reduce direct string comparisons of standard HIV-model relationship types and associated errors.
    e.g. Use RiskGroups.high or RiskGroups.high.name in code depending on use and
    RiskGroups.high.value in json/dict values.
    """
    low = 'LOW'
    medium = 'MEDIUM'
    high = 'HIGH'
