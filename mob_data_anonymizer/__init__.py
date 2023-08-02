import os

__app_name__ = "mob_data_anonymizer"
__version__ = "0.1.0"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'

DEFAULT_PARAMETERS_FILE = "anonymization_parameters.json"
DEFAULT_ANONYMIZE_OUTPUT_FILE = "output.csv"
DEFAULT_ANALYSIS_OUTPUT_FILE = "output.json"
DEFAULT_MEASURES_OUTPUT_FILE = "output.json"

CONFIG_FILE = ROOT_DIR + "config.json"
CONFIG_API_FILE = "mob_data_anonymizer/server/config_api.json"
CONFIG_DB_FILE = "mob_data_anonymizer/db/config_db.json"

(
    SUCCESS,
    PARAMETERS_FILE_DOESNT_EXIST,
    PARAMETERS_FILE_NOT_JSON,
    PARAMETERS_NOT_VALID,
    INPUT_FILE_NOT_EXIST,
    OUTPUT_FOLDER_NOT_EXIST,
    WRONG_METHOD,
    WRONG_MODE,
    WRONG_METHOD_PARAMETER
) = range(9)

ERRORS = {
    PARAMETERS_FILE_DOESNT_EXIST: "Parameters file does not exist",
    PARAMETERS_FILE_NOT_JSON: "Parameters file has to be a valid JSON",
    PARAMETERS_NOT_VALID: "Some required parameter is missing",
    INPUT_FILE_NOT_EXIST: "Input file does not exist",
    OUTPUT_FOLDER_NOT_EXIST: "Output folder does not exist",
    WRONG_METHOD: "A requested method is not supported (or it is misspelled)",
    WRONG_MODE: "The requested mode is not supported (or it is misspelled)",
    WRONG_METHOD_PARAMETER: "A method parameter is wrong"
}

# Default methods
DEFAULT_ANONYMIZATION = "SimpleGeneralization"
DEFAULT_TRAJECTORY_DISTANCE = "Martinez2021"
DEFAULT_CLUSTERING = "SimpleMDAV"
DEFAULT_AGGREGATION = "Mean_trajectory"

DEFAULT_CRS = 'epsg:4326'