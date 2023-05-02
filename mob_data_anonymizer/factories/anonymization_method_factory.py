import importlib
import inspect
import json
import os

from mob_data_anonymizer.anonymization_methods.AnonymizationMethodInterface import AnonymizationMethodInterface
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.factories.aggregation_method_factory import AggregationMethodFactory
from mob_data_anonymizer.factories.clustering_method_factory import ClusteringMethodFactory
from mob_data_anonymizer.factories.trajectory_distance_factory import TrajectoryDistanceFactory
from mob_data_anonymizer import CONFIG_FILE, DEFAULT_TRAJECTORY_DISTANCE, DEFAULT_CLUSTERING, DEFAULT_AGGREGATION


class AnonymizationMethodFactory:
    @staticmethod
    def get(method_name: str, dataset: Dataset, params: dict) -> AnonymizationMethodInterface:

        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        if method_name not in config['anonymization_methods']:
            raise ValueError(f'Anonymization method not valid: {method_name}')

        method_config = config['anonymization_methods'][method_name]
        module_name, class_name = method_config['class'].rsplit('.', 1)
        module = importlib.import_module(module_name)
        method_class = getattr(module, class_name)

        # Constructor solo con defaults?
        # Qué pasa con el constructor que acepta una distancia, agregación, etc...?
        # Params: probar un dict con un parámetro que no sea de los válidos, con uno que sí

        # kwargs = method_config['defaults']
        method_signature = inspect.signature(method_class.__init__)

        # Special parameters (if required):
        # print(method_signature.parameters)
        if 'trajectory_distance' in method_signature.parameters:
            print("TD required")
            if 'trajectory_distance' in params:
                print("TD")
                distance_name = params['trajectory_distance'].pop('name')
                params['trajectory_distance'] = TrajectoryDistanceFactory.get(distance_name, dataset,
                                                                                  params['trajectory_distance']['params'])
                print(params['trajectory_distance'])
            else:
                # Default
                params['trajectory_distance'] = TrajectoryDistanceFactory.get(DEFAULT_TRAJECTORY_DISTANCE, dataset,
                                                                                  {})

        if 'clustering_method' in method_signature.parameters:
            if 'clustering_method' in params:
                print("CM")
                method_name = params['clustering_method'].pop('name')
                params['clustering_method'] = ClusteringMethodFactory.get(method_name, dataset,
                                                                              params['clustering_method']['params'])
                print(params['clustering_method'])
            else:
                # Default
                params['clustering_method'] = ClusteringMethodFactory.get(DEFAULT_CLUSTERING, dataset,
                                                                              {})

        if 'aggregation_method' in method_signature.parameters:
            if 'aggregation_method' in params:
                print("AM")
                method_name = params['aggregation_method'].pop('name')
                    
                params['aggregation_method'] = AggregationMethodFactory.get(method_name)
                print(params['aggregation_method'])
            else:
                # Default
                params['aggregation_method'] = AggregationMethodFactory.get(DEFAULT_AGGREGATION)

        return method_class(dataset, **params)





