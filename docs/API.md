# MobiDataLab anonymization module

## API

### End points

- **POST /anonymize/** 
    - Upload a dataset to be anonymized.
    - Params: 
      - Input_dataset
      - config_file
- **POST /analyze/** 
  -	Upload a dataset to be analyzed.
  - Params: 
        - Input_dataset
        - config_file
- **POST /compute_measures/**
  - Compute measures over the original and the anonymized dataset
  - Params:
    - original_dataset
    -	anonymized_dataset
    -	config_file 
- **POST /filter/**
  - Upload a dataset to be filtered
  - Params:
    - Input_dataset
    - config_file

Sometimes the previous tasks take some time to compute. For this reason, all the previous endpoints return a task_id: 

```
{
  "status": "OK",
  "message": "Your task is being processed. Use the 'GET /task/' endpoint to obtain the results later",
  "task_id": "30c2ad9df0f9470abfd8198b4cb4f86a"
}
```

After some time, the result can be obtained from the following endpoint:
- **GET /task/**?task_id={task_id}

### Using the command line interface to query the API

The command line interface can also be used to send requests to the API.

First, define the server API address in the [/server/config_api.json](../mdl_anonymizer/server/config_api.json) file:

```
{
    "api_server": "http://127.0.0.1:8000"
}
```

These are the available commands: 

```
python -m mob_data_anonymizer anonymize-api -f parameters_file.json
python -m mob_data_anonymizer analysis-api -f parameters_file.json
python –m mob_data_anonymizer measures-api -f parameter_file.json 
python –m mob_data_anonymizer filter-api -f parameter_file.json
```

The same parameter files than used in the standalone use case can be used in this case. 

After some time, the result can be obtained by using the following command:

```
python -m mob_data_anonymizer get-task -t {task_id}
```

