from typing import Dict, Type
from services.ml_engine.fairness.metrics import Metric

class MetricRegistry:
    def __init__(self):
        self._metrics: Dict[str, Type[Metric]] = {}
        
    def register(self, metric_class: Type[Metric]) -> None:
        metadata = metric_class.metadata()
        self._metrics[metadata.name] = metric_class
        
    def get(self, name: str) -> Type[Metric]:
        if name not in self._metrics:
            raise ValueError(f"Metric '{name}' not found in registry.")
        return self._metrics[name]
        
    def get_all_metadata(self) -> list:
        return [m.metadata() for m in self._metrics.values()]
