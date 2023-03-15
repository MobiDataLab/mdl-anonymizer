__app_name__ = "mob_data_anonymizer"
__version__ = "0.1.0"

DEFAULT_PARAMETERS_FILE = "anonymization_parameters.json"
DEFAULT_OUTPUT_FILE = "output.json"
DEFAULT_SAVE_FILTERED_DATASET = True
DEFAULT_FILTERED_FILE = "filtered.json"
CONFIG_API_FILE = "mob_data_anonymizer/config_api.json"
CONFIG_DB_FILE = "mob_data_anonymizer/db/config_db.json"

(
    SUCCESS,
    PARAMETERS_FILE_DOESNT_EXIST,
    PARAMETERS_FILE_NOT_JSON,
    PARAMETERS_NOT_VALID,
    INPUT_FILE_NOT_EXIST,
    OUTPUT_FOLDER_NOT_EXIST,
    WRONG_METHOD,
    WRONG_MODE
) = range(8)

ERRORS = {
    PARAMETERS_FILE_DOESNT_EXIST: "Parameters file does not exist",
    PARAMETERS_FILE_NOT_JSON: "Parameters file has to be a valid JSON",
    PARAMETERS_NOT_VALID: "Some parameters are missing",
    INPUT_FILE_NOT_EXIST: "Input file does not exist",
    OUTPUT_FOLDER_NOT_EXIST: "Output folder does not exist",
    WRONG_METHOD: "A requested method is not supported (or it is misspelled)",
    WRONG_MODE: "The requested mode is not supported (or it is misspelled)",
}