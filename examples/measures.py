import logging
import warnings

from entities.Dataset import Dataset
from factories.analysis_method_factory import AnalysisMethodFactory
from factories.anonymization_method_factory import AnonymizationMethodFactory
from factories.measures_method_factory import MeasuresMethodFactory
from factories.trajectory_distance_factory import TrajectoryDistanceFactory

warnings.filterwarnings("ignore")
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)


dataset = Dataset()
dataset.from_file("data/mock_dataset.csv")

a_dataset = Dataset()
a_dataset.from_file("data/mock_dataset_anonymized.csv")


params = {
    'trajectory_distance': {
        'name': 'Martinez2021'
    }
}

measure = MeasuresMethodFactory.get('Rsme', dataset, a_dataset, params)
measure.run()
result = measure.get_result()

print(result)
