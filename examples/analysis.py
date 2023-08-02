import logging

from entities.Dataset import Dataset
from factories.analysis_method_factory import AnalysisMethodFactory

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)


dataset = Dataset()
dataset.from_file("data/mock_dataset.csv")

params = {
    "min_k": 3,
    "min_sector_length": 200,
    "merge_sectors": False
  }

method = AnalysisMethodFactory.get('QuadTreeHeatMap', dataset, params)
method.run()
result = method.get_result()

print(result)
print(result['geometry'])
print(result['geometry'][0])
