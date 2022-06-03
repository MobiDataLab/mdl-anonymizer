import logging

import skmob

from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.utils.Measures import Measures
from mob_data_anonymizer.utils.Stats import Stats

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

original_file = "data/cabs_dataset_20080608_0800_1000.csv"
anonymized_file = "data/cabs_dataset_20080608_0800_1000_anony.csv"

logging.info("Loading original trajdataframe")
original_tdf = skmob.TrajDataFrame.from_file(original_file,
                                    latitude='lat',
                                    longitude='lon',
                                    user_id='user_id',
                                    datetime='timestamp')

logging.info("Loading anonymized trajdataframe")
anonymized_tdf = skmob.TrajDataFrame.from_file(anonymized_file,
                                    latitude='lat',
                                    longitude='lon',
                                    user_id='user_id',
                                    datetime='timestamp')


measures = Measures(original_tdf, anonymized_tdf, output_folder="output/")

#measures.cmp_mean_square_displacement()
measures.cmp_distance_straight_line(output="mean")

#measures.cmp_random_location_entropy(output='report')
#measures.cmp_visits_per_location(output='report')
