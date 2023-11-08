import importlib
import json

from mdl_anonymizer.analysis_methods.AnalysisMethodInterface import AnalysisMethodInterface
from mdl_anonymizer.entities.Dataset import Dataset
from mdl_anonymizer import CONFIG_FILE, WRONG_METHOD_PARAMETER


class AnalysisMethodFactory:
    @staticmethod
    def get(method_name: str, dataset: Dataset, params: dict = None) -> AnalysisMethodInterface:
        if params is None:
            params = {}

        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        if method_name not in config['analysis_methods']:
            raise ValueError(f'Analysis method not valid: {method_name}')

        method_config = config['analysis_methods'][method_name]
        module_name, class_name = method_config['class'].rsplit('.', 1)
        module = importlib.import_module(module_name)
        method_class = getattr(module, class_name)

        try:
            return method_class(dataset, **params)
        except TypeError:
            # Wrong parameter
            raise ValueError(WRONG_METHOD_PARAMETER) from None





