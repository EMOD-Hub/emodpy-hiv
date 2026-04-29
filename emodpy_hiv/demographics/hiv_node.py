from typing import Dict

from emod_api.demographics.node import Node

from emodpy_hiv.demographics.society import Society


class HIVNode(Node):
    def __init__(self, society: Society = None, **kwargs: Any):
        """
        An extension of emod-api Node that adds society representation of interpersonal relationships for HIV
        simulations. HIVNode can be used to represent individual simulation nodes and an EMOD 'Defaults' node. To be
        used with HIVDemographics objects, which require HIVNodes.

        Args:
            society: an initialized Society object to be used with this simulation node.
            **kwargs: arguments passed along to the Node constructor
        """
        super().__init__(**kwargs)
        self.society = Society() if society is None else society

    def to_dict(self) -> Dict:
        result = super().to_dict()
        result['Society'] = self.society.to_dict()
        return result
