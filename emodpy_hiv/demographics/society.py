from typing import Dict, Set

from emodpy_hiv.demographics.assortivity import Assortivity
from emodpy_hiv.demographics.concurrency_parameters import ConcurrencyParameters
from emodpy_hiv.demographics.pair_formation_parameters import PairFormationParameters
from emodpy_hiv.demographics.relationship_parameters import RelationshipParameters


class Society:
    def __init__(self,
                 concurrency_configuration: Dict = None,
                 relationship_parameters: Dict[str, RelationshipParameters] = None,
                 pair_formation_parameters: Dict[str, PairFormationParameters] = None,
                 concurrency_parameters: Dict[str, Dict[str, ConcurrencyParameters]] = None):
        """
        The Society object defines the behavioral-based parameters of a relationship type in the STI and HIV models,
        such as rates of partnership formation, partner preference, relationship duration, and concurrent partnerships.
        It must contain the (argument listed)) sets of relationship type parameters and the concurrency configuration.

        https://docs.idmod.org/projects/emod-hiv/en/latest/parameter-demographics.html#society

        Args:
            concurrency_configuration: a non-default concurrency configuration dict, if provided. A broadly applicable
                default is provided in method _default_concurrency_configuration() .
            relationship_parameters: a dict of RelationshipParameters objects, each key: value pair being
                relationship_type: RelationshipParameters()
            pair_formation_parameters: a dict of PairFormationParameters objects, each key: value pair being
                relationship_type: PairFormationParameters()
            concurrency_parameters: a nested dict of ConcurrencyParameters objects, indexed by type then risk, e.g.:
            {
                "INFORMAL": {
                    "HIGH": ConcurrencyParameter object,
                    "MED": ConcurrencyParameter object,
                    "LOW": ConcurrencyParameter object
                },
                "TRANSITORY": {
                    "HIGH": ConcurrencyParameter object,
                    "MED": ConcurrencyParameter object,
                    "LOW": ConcurrencyParameter object
                },
                ...
            }
        """
        super().__init__()
        self.concurrency_configuration = concurrency_configuration if concurrency_configuration is not None \
            else self._default_concurrency_configuration
        self.relationship_parameters = relationship_parameters if relationship_parameters is not None else {}
        self.pair_formation_parameters = pair_formation_parameters if pair_formation_parameters is not None else {}
        self.concurrency_parameters = concurrency_parameters if concurrency_parameters is not None else {}

    @property
    def relationship_types(self) -> Set[str]:
        return {*self.relationship_parameters.keys(),
                *self.pair_formation_parameters.keys(),
                *self.concurrency_parameters.keys()}

    @property
    def _default_concurrency_configuration(self):
        return {
            "Probability_Person_Is_Behavioral_Super_Spreader": 0,
            "Individual_Property_Name": "Risk",
            "LOW": {
                "Extra_Relational_Flag_Type": "Correlated",
                "Correlated_Relationship_Type_Order": [
                    "COMMERCIAL",
                    "TRANSITORY",
                    "INFORMAL",
                    "MARITAL"
                ]
            },
            "MEDIUM": {
                "Extra_Relational_Flag_Type": "Correlated",
                "Correlated_Relationship_Type_Order": [
                    "COMMERCIAL",
                    "TRANSITORY",
                    "INFORMAL",
                    "MARITAL"
                ]
            },
            "HIGH": {
                "Extra_Relational_Flag_Type": "Correlated",
                "Correlated_Relationship_Type_Order": [
                    "COMMERCIAL",
                    "TRANSITORY",
                    "INFORMAL",
                    "MARITAL"
                ]
            }
        }

    def get_pair_formation_parameters_by_relationship_type(self, relationship_type: str) -> PairFormationParameters:
        if relationship_type not in self.pair_formation_parameters:
            self.pair_formation_parameters[relationship_type] = PairFormationParameters()
        return self.pair_formation_parameters[relationship_type]

    def get_concurrency_parameters_by_relationship_type_and_risk(self, relationship_type: str,
                                                                 risk: str) -> ConcurrencyParameters:
        if relationship_type not in self.concurrency_parameters:
            self.concurrency_parameters[relationship_type] = {}
        if risk not in self.concurrency_parameters[relationship_type]:
            self.concurrency_parameters[relationship_type][risk] = ConcurrencyParameters()
        return self.concurrency_parameters[relationship_type][risk]

    def get_relationship_parameters_by_relationship_type(self, relationship_type: str) -> RelationshipParameters:
        if relationship_type not in self.relationship_parameters:
            self.relationship_parameters[relationship_type] = RelationshipParameters()
        return self.relationship_parameters[relationship_type]

    def set_pair_formation_parameters(self, relationship_type: str,
                                      formation_rate: float = None,
                                      assortivity: Assortivity = None) -> None:
        pair_formation_parameters = self.get_pair_formation_parameters_by_relationship_type(relationship_type=relationship_type)
        if formation_rate is not None:
            pair_formation_parameters.Formation_Rate_Constant = formation_rate
        if assortivity is not None:
            if len(assortivity.matrix) != 3:
                raise ValueError("You need to have 3 rows in your assortivity matrix.")
            if any(len(row) != 3 for row in assortivity.matrix):
                raise ValueError("You need to have 3 columns in each row of your assortivity matrix.")
            pair_formation_parameters.Assortivity = assortivity

    def set_concurrency_parameters(self, relationship_type: str,
                                   risk: str,
                                   max_simul_rels_male: float = None,
                                   max_simul_rels_female: float = None,
                                   prob_xtra_rel_male: float = None,
                                   prob_xtra_rel_female: float = None) -> None:
        concurrency_parameters = self.get_concurrency_parameters_by_relationship_type_and_risk(relationship_type=relationship_type, risk=risk)
        if max_simul_rels_male is not None:
            concurrency_parameters.max_simultaneous_relationships_male = max_simul_rels_male
        if max_simul_rels_female is not None:
            concurrency_parameters.max_simultaneous_relationships_female = max_simul_rels_female
        if prob_xtra_rel_male is not None:
            concurrency_parameters.probability_extra_relationship_male = prob_xtra_rel_male
        if prob_xtra_rel_female is not None:
            concurrency_parameters.probability_extra_relationship_female = prob_xtra_rel_female

    def set_relationship_parameters(self, relationship_type: str,
                                    coital_act_rate: float = None,
                                    condom_usage_min: float = None,
                                    condom_usage_mid: float = None,
                                    condom_usage_max: float = None,
                                    condom_usage_rate: float = None,
                                    duration_scale: float = None,
                                    duration_heterogeneity: float = None) -> None:
        relationship_parameters = self.get_relationship_parameters_by_relationship_type(relationship_type=relationship_type)
        if coital_act_rate is not None:
            relationship_parameters.coital_act_rate = coital_act_rate
        if condom_usage_min is not None:
            relationship_parameters.condom_usage.min = condom_usage_min
        if condom_usage_mid is not None:
            relationship_parameters.condom_usage.mid = condom_usage_mid
        if condom_usage_max is not None:
            relationship_parameters.condom_usage.max = condom_usage_max
        if condom_usage_rate is not None:
            relationship_parameters.condom_usage.rate = condom_usage_rate
        if duration_scale is not None:
            relationship_parameters.duration.weibull_lambda = duration_scale
        if duration_heterogeneity is not None:
            relationship_parameters.duration.weibull_kappa = duration_heterogeneity ** -1

    def to_dict(self) -> Dict:
        society = {'Concurrency_Configuration': self.concurrency_configuration}
        for relationship_type in self.relationship_types:
            relationship_configuration = {}

            relationship_parameters = self.relationship_parameters.get(relationship_type, None)
            if relationship_parameters is not None:
                relationship_configuration['Relationship_Parameters'] = relationship_parameters.to_dict()

            pair_formation_parameters = self.pair_formation_parameters.get(relationship_type, None)
            if pair_formation_parameters is not None:
                relationship_configuration['Pair_Formation_Parameters'] = pair_formation_parameters.to_dict()

            concurrency_parameters = self.concurrency_parameters.get(relationship_type, None)
            if concurrency_parameters is not None:
                if 'Concurrency_Parameters' not in relationship_configuration:
                    relationship_configuration['Concurrency_Parameters'] = {}
                for risk_group, cp_by_risk in concurrency_parameters.items():
                    relationship_configuration['Concurrency_Parameters'][risk_group] = cp_by_risk.to_dict()

            society[relationship_type] = relationship_configuration
        return society

    @classmethod
    def from_dict(cls, d: Dict) -> '__class__':
        concurrency_configuration = d['Concurrency_Configuration']
        relationship_parameters = {}
        pair_formation_parameters = {}
        concurrency_parameters = {}

        relationship_types = d.keys() - ['Concurrency_Configuration']
        for relationship_type in relationship_types:
            relationship_params = d[relationship_type].get('Relationship_Parameters', None)
            if relationship_params is not None:
                relationship_parameters[relationship_type] = RelationshipParameters.from_dict(relationship_params)

            pair_formation_params = d[relationship_type].get('Pair_Formation_Parameters', None)
            if pair_formation_params is not None:
                pair_formation_parameters[relationship_type] = PairFormationParameters.from_dict(pair_formation_params)

            concurrency_params = d[relationship_type].get('Concurrency_Parameters', None)
            if concurrency_params is not None:
                cp_by_risk = {risk: ConcurrencyParameters.from_dict(by_risk_parameters)
                              for risk, by_risk_parameters in concurrency_params.items()}
                concurrency_parameters[relationship_type] = cp_by_risk

        return cls(concurrency_configuration=concurrency_configuration, relationship_parameters=relationship_parameters,
                   pair_formation_parameters=pair_formation_parameters, concurrency_parameters=concurrency_parameters)
