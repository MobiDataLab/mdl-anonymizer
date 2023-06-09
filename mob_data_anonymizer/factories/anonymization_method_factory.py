import importlib
import inspect
import json
import logging
import os

from mob_data_anonymizer.anonymization_methods.AnonymizationMethodInterface import AnonymizationMethodInterface
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.factories.aggregation_method_factory import AggregationMethodFactory
from mob_data_anonymizer.factories.clustering_method_factory import ClusteringMethodFactory
from mob_data_anonymizer.factories.trajectory_distance_factory import TrajectoryDistanceFactory
from mob_data_anonymizer import CONFIG_FILE, DEFAULT_TRAJECTORY_DISTANCE, DEFAULT_CLUSTERING, DEFAULT_AGGREGATION, \
    WRONG_METHOD_PARAMETER


class AnonymizationMethodFactory:
    @staticmethod
    def get(method_name: str, dataset: Dataset, params: dict = None) -> AnonymizationMethodInterface:

        if params is None:
            params = {}

        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        if method_name not in config['anonymization_methods']:
            raise ValueError(f'Anonymization method not valid: {method_name}')

        method_config = config['anonymization_methods'][method_name]
        module_name, class_name = method_config['class'].rsplit('.', 1)
        module = importlib.import_module(module_name)
        method_class = getattr(module, class_name)

        method_signature = inspect.signature(method_class.__init__)

        # Special parameters (if required):
        if 'trajectory_distance' in method_signature.parameters:
            if 'trajectory_distance' in params:
                method_name = params['trajectory_distance'].pop('name')
                method_params = params['trajectory_distance'].get('params', {})
                params['trajectory_distance'] = TrajectoryDistanceFactory.get(method_name, dataset, method_params)
                name = method_name
            else:
                # Default
                params['trajectory_distance'] = TrajectoryDistanceFactory.get(DEFAULT_TRAJECTORY_DISTANCE, dataset)
                name = DEFAULT_TRAJECTORY_DISTANCE
            logging.info(f"Trajectory distance for anonymization: {name}")

        if 'clustering_method' in method_signature.parameters:
            if 'clustering_method' in params:
                method_name = params['clustering_method'].pop('name')
                method_params = params['clustering_method'].get('params', {})
                params['clustering_method'] = ClusteringMethodFactory.get(method_name, dataset, method_params)
                name = method_name
            else:
                # Default
                params['clustering_method'] = ClusteringMethodFactory.get(DEFAULT_CLUSTERING, dataset)
                name = DEFAULT_CLUSTERING
            logging.info(f"Clustering method for anonymization: {name}")

        if 'aggregation_method' in method_signature.parameters:
            if 'aggregation_method' in params:
                method_name = params['aggregation_method'].pop('name')
                method_params = params['aggregation_method'].get('params', {})
                params['aggregation_method'] = AggregationMethodFactory.get(method_name, method_params)
                name = method_name
            else:
                # Default
                params['aggregation_method'] = AggregationMethodFactory.get(DEFAULT_AGGREGATION)
                name = DEFAULT_AGGREGATION
            logging.info(f"Aggregation method for anonymization: {name}")

        try:
            return method_class(dataset, **params)
        except TypeError:
            # Wrong parameter
            raise ValueError(WRONG_METHOD_PARAMETER) from None
