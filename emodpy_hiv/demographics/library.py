from typing import List

from emodpy_hiv.demographics.hiv_demographics import HIVDemographics


def set_concurrency_parameters(demographics: HIVDemographics,
                               relationship_type: str,
                               risk_group: str,
                               max_simul_rels_male: float = None,
                               max_simul_rels_female: float = None,
                               prob_xtra_rel_male: float = None,
                               prob_xtra_rel_female: float = None,
                               node_ids: List[int] = None) -> None:

    demographics.set_concurrency_params_by_type_and_risk(relationship_type=relationship_type,
                                                         risk_group=risk_group,
                                                         max_simul_rels_male=max_simul_rels_male,
                                                         max_simul_rels_female=max_simul_rels_female,
                                                         prob_xtra_rel_male=prob_xtra_rel_male,
                                                         prob_xtra_rel_female=prob_xtra_rel_female,
                                                         node_ids=node_ids)


def set_pair_formation_parameters(demographics: HIVDemographics,
                                  relationship_type: str,
                                  formation_rate: float = None,
                                  risk_assortivity: float = None,
                                  node_ids: List[int] = None) -> None:
    def _ra_matrix(v: float):
        if v is None:
            matrix = None
        elif v == -1:
            matrix = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        else:
            matrix = [[v, 1 - v, 0], [1 - v, v, v], [0, v, 1 - v]]
        return matrix

    assortivity_matrix = _ra_matrix(v=risk_assortivity)
    demographics.set_pair_formation_parameters(relationship_type=relationship_type,
                                               formation_rate=formation_rate,
                                               assortivity_matrix=assortivity_matrix,
                                               node_ids=node_ids)


def set_relationship_parameters(demographics: HIVDemographics,
                                relationship_type: str,
                                coital_act_rate: float = None,
                                condom_usage_min: float = None,
                                condom_usage_mid: float = None,
                                condom_usage_max: float = None,
                                condom_usage_rate: float = None,
                                duration_scale: float = None,
                                duration_heterogeneity: float = None,
                                node_ids: List[int] = None) -> None:
    demographics.set_relationship_parameters(relationship_type=relationship_type,
                                             coital_act_rate=coital_act_rate,
                                             condom_usage_min=condom_usage_min,
                                             condom_usage_mid=condom_usage_mid,
                                             condom_usage_max=condom_usage_max,
                                             condom_usage_rate=condom_usage_rate,
                                             duration_scale=duration_scale,
                                             duration_heterogeneity=duration_heterogeneity,
                                             node_ids=node_ids)


#
# INITIAL IP DISTRIBUTION METHODS
#


def set_initial_risk_distribution(demographics: HIVDemographics, initial_risk_distribution_low: float,
                                  node_ids: List[int] = None) -> None:
    def _risk_distribution(low: float):
        return None if low is None else [low, 1 - low, 0]

    distribution = _risk_distribution(low=initial_risk_distribution_low)
    demographics.add_or_update_initial_risk_distribution(distribution=distribution, node_ids=node_ids)


def set_initial_cascade_state_distribution(demographics: HIVDemographics,
                                           cascade_state_distribution: List[float],
                                           node_ids: List[int] = None) -> None:
    demographics.add_or_update_initial_cascade_state_distribution(distribution=cascade_state_distribution,
                                                                  node_ids=node_ids)


def set_initial_health_care_accessibility_distribution(demographics: HIVDemographics,
                                                       initial_accessibility: float,
                                                       node_ids: List[int] = None) -> None:
    distribution = [initial_accessibility, 1 - initial_accessibility]
    demographics.add_or_update_initial_health_care_accessibility_distribution(distribution=distribution,
                                                                              node_ids=node_ids)
