from functools import partial
from typing import Dict, Any


class ParameterizedCall:
    def __init__(self,
                 func: callable,
                 non_hyperparameters: Dict[str, Any] = None,
                 hyperparameters: Dict[str, Any] = None,
                 label: str = None):
        self.func = func
        self._non_hyperparameters = {} if non_hyperparameters is None else non_hyperparameters
        self.hyperparameters = {} if hyperparameters is None else hyperparameters
        self.label = label

    @property
    def _label_str(self):
        return "" if self.label is None else f"--{self.label}"

    def _label_hyperparameter(self, hyperparameter: str) -> str:
        labeled_hyperparameter = hyperparameter + self._label_str
        return labeled_hyperparameter

    def _unlabel_hyperparameter(self, labeled_hyperparameter: str) -> str:
        unlabeled_hyperparameter = labeled_hyperparameter.removesuffix(self._label_str)
        if self._label_str != "" and unlabeled_hyperparameter == labeled_hyperparameter:
            raise ValueError(f"Cannot remove label: {self.label} from labeled hyperparameter: {labeled_hyperparameter}")
        return unlabeled_hyperparameter

    @property
    def labeled_hyperparameters(self) -> Dict[str, Any]:
        return {self._label_hyperparameter(hp): value for hp, value in self.hyperparameters.items()}

    @property
    def _hyperparameters_none_filtered(self):
        return {hp: value for hp, value in self.hyperparameters.items() if value is not None}

    def _set_hyperparameter(self, hyperparameter: str, value: Any) -> None:
        if hyperparameter not in self.hyperparameters:
            raise ValueError(f"Cannot set unknown hyperparameter: {hyperparameter}")
        self.hyperparameters[hyperparameter] = value

    def set_labeled_hyperparameter(self, labeled_hyperparameter: str, value: Any) -> None:
        hyperparameter = self._unlabel_hyperparameter(labeled_hyperparameter=labeled_hyperparameter)
        self._set_hyperparameter(hyperparameter=hyperparameter, value=value)

    def prepare_call(self) -> callable:
        return partial(self.func, **self._non_hyperparameters, **self._hyperparameters_none_filtered)
