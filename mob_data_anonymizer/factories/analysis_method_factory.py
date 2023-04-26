import importlib
import json

from mob_data_anonymizer.analysis_methods.AnalysisMethodInterface import AnalysisMethodInterface
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer import CONFIG_FILE


class AnalysisMethodFactory:
    @staticmethod
    def get(method_name: str, dataset: Dataset, params: dict) -> AnalysisMethodInterface:

        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        if method_name not in config['analysis_methods']:
            raise ValueError(f'Analysis method not valid: {method_name}')

        method_config = config['analysis_methods'][method_name]
        module_name, class_name = method_config['class'].rsplit('.', 1)
        module = importlib.import_module(module_name)
        method_class = getattr(module, class_name)

        return method_class(dataset, **params)





