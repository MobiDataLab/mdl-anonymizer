__app_name__ = "mob_data_anonymizer"
__version__ = "0.1.0"

DEFAULT_PARAMETERS_FILE = "anonymization_parameters.json"

(
    SUCCESS,
    PARAMETERS_FILE_DOESNT_EXIST,
    PARAMETERS_FILE_NOT_JSON,
    PARAMETERS_NOT_VALID,
    INPUT_FILE_NOT_EXIST,
    WRONG_METHOD
) = range(6)

ERRORS = {
    PARAMETERS_FILE_DOESNT_EXIST: "Parameters file does not exist",
    PARAMETERS_FILE_NOT_JSON: "Parameters file has to be a valid JSON",
    PARAMETERS_NOT_VALID: "Some parameters are missing",
    INPUT_FILE_NOT_EXIST: "Input file does not exist",
    WRONG_METHOD: "The requested method is not supported (or it is misspelled)",
}