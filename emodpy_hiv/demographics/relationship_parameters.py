from typing import Dict

from emod_api.demographics.Updateable import Updateable
from emodpy.utils.distributions import WeibullDistribution

from emodpy_hiv.demographics.condom_usage_parameters import CondomUsageParameters


class RelationshipParameters(Updateable):
    def __init__(self,
                 condom_usage: CondomUsageParameters = None,
                 coital_act_rate: float = 0,
                 duration: WeibullDistribution = None):
        """
        A RelationshipParameters object defines basic attributes such as relationship duration, what happens if one
        member of a relationship migrates, and condom usage. Only WeibullDistribution durations are accepted by EMOD.

        Args:
            condom_usage: (CondomUsageParameters) (optional) a CondomUsageParameters object defining condom usage over
                time
            coital_act_rate: (float) (optional) the number of coital acts per day in a relationship. Default is 0.
            duration: (WeibullDistribution) (optional) a weibull distribution used for determining relationship duration
                in days (default is a WeibullDistribution with lambda and kappa values of 0.1)
        """
        super().__init__()
        self.condom_usage = condom_usage if condom_usage is not None else CondomUsageParameters()
        self.coital_act_rate = coital_act_rate
        # TODO: do we need to allow alteration of migration actions??
        self.migration_actions = ["TERMINATE"]
        self.migration_actions_distribution = [1.0]

        default_duration = WeibullDistribution(weibull_lambda=0.1, weibull_kappa=0.1)
        self.duration = duration if duration is not None else default_duration

    def to_dict(self) -> Dict:
        duration_heterogeneity = self.duration.weibull_kappa ** -1
        parameters = {
            'Condom_Usage_Probability': self.condom_usage.to_dict(),
            'Coital_Act_Rate': self.coital_act_rate,
            'Duration_Weibull_Scale': self.duration.weibull_lambda,
            'Duration_Weibull_Heterogeneity': duration_heterogeneity,
            'Migration_Actions': self.migration_actions,
            'Migration_Actions_Distribution': self.migration_actions_distribution
        }
        return parameters

    @classmethod
    def from_dict(cls, d: Dict) -> '__class__':
        condom_usage = CondomUsageParameters.from_dict(d=d['Condom_Usage_Probability'])
        kappa = 0 if d['Duration_Weibull_Heterogeneity'] == 0 else d['Duration_Weibull_Heterogeneity'] ** -1
        duration = WeibullDistribution(weibull_lambda=d['Duration_Weibull_Scale'], weibull_kappa=kappa)
        return cls(condom_usage=condom_usage, coital_act_rate=d['Coital_Act_Rate'], duration=duration)
