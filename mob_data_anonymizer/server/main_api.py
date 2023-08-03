import logging

from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
import uuid

from mob_data_anonymizer import CONFIG_FILE, ERRORS, WRONG_METHOD
import json

from mob_data_anonymizer.server.server_functions import return_task, anonymize, analyze, measures, filter_dataset

app = FastAPI()

PROCESSING_MESSAGE = "Your task is being processed. Use the 'GET /task/' endpoint to obtain the results later"
OK = "OK"
ERROR = "ERROR"
NOT_AVAILABLE = "NOT_AVAILABLE"

@app.get("/task/")
def get(task_id: str):
    response_file_path = return_task(task_id)
    if response_file_path is None:
        task_message = f"task {task_id} not available or still processing"
        return {"status": NOT_AVAILABLE, "message": task_message}
    else:
        response = FileResponse(response_file_path, filename=response_file_path)
        return response


@app.post("/anonymize/")
def post(input_dataset: UploadFile = File(...),
         config_file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    params = json.load(config_file.file)

    method = params["method"]
    if method not in config['anonymization_methods']:
        return {"status": ERROR, "message": ERRORS[WRONG_METHOD]}

    task_id = str(uuid.uuid4().hex)
    logging.info(f'Task id: {task_id}')
    background_tasks.add_task(anonymize, input_dataset.file, input_dataset.filename, params, task_id)

    return {"status": OK, "message": PROCESSING_MESSAGE, "task_id": task_id}


@app.post("/analyze/")
def post(input_dataset: UploadFile = File(...),
         config_file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    params = json.load(config_file.file)
    method = params["method"]
    if method not in config['analysis_methods']:
        return {"status": ERROR, "message": ERRORS[WRONG_METHOD]}

    task_id = str(uuid.uuid4().hex)
    logging.info(f'Task id: {task_id}')
    background_tasks.add_task(analyze, input_dataset.file, input_dataset.filename, params, task_id)

    return {"status": OK, "message": PROCESSING_MESSAGE, "task_id": task_id}


@app.post("/compute_measures/")
def post(original_dataset: UploadFile = File(...), anonymized_dataset: UploadFile = File(...),
         config_file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    params = json.load(config_file.file)
    task_id = str(uuid.uuid4().hex)
    logging.info(f'Task id: {task_id}')
    background_tasks.add_task(measures, original_dataset.file, anonymized_dataset.file,
                              original_dataset.filename, anonymized_dataset.filename, params, task_id)

    return {"status": OK, "message": PROCESSING_MESSAGE, "task_id": task_id}


@app.post("/filter/")
def post(input_dataset: UploadFile = File(...), config_file: UploadFile = File(...),
         background_tasks: BackgroundTasks = None):
    params = json.load(config_file.file)
    task_id = str(uuid.uuid4().hex)
    logging.info(f'Task id: {task_id}')
    background_tasks.add_task(filter_dataset, input_dataset.file, input_dataset.filename, params, task_id)

    return {"status": OK, "message": PROCESSING_MESSAGE, "task_id": task_id}
