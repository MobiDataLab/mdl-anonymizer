import importlib
import json

from mob_data_anonymizer.distances.trajectory.DistanceInterface import DistanceInterface
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer import CONFIG_FILE


class TrajectoryDistanceFactory:
    @staticmethod
    def get(distance_name: str, dataset: Dataset, params: dict = None) -> DistanceInterface:
        if params is None:
            params = {}

        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        if distance_name not in config['trajectory_distances']:
            raise ValueError(f'Trajectory distance not valid: {distance_name}')

        method_config = config['trajectory_distances'][distance_name]
        module_name, class_name = method_config['class'].rsplit('.', 1)
        module = importlib.import_module(module_name)
        method_class = getattr(module, class_name)

        # Some distances need the whole dataset
        params['dataset'] = dataset

        return method_class(**params)





