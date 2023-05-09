from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from server.server_functions import anonymize
from server.server_functions import analyze
from server.server_functions import measures
from server.server_functions import filter
from server.server_functions import return_task
import uuid
from mob_data_anonymizer import CONFIG_FILE
import json


app = FastAPI()


@app.get("/task/")
def get(task_id: str):
    response_file_path = return_task(task_id)
    if response_file_path is None:
        task_message = f"task {task_id} not available or still processing"
        print(task_message)
        return {"message": task_message}
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
        task_message = f"Anonymization method not valid: {method}"
        return {"message": task_message}
    task_id = str(uuid.uuid4().hex)
    background_tasks.add_task(anonymize, input_dataset.file, input_dataset.filename, params, task_id)
    task_message = f"task {task_id} requested"
    return {"message": task_message}


@app.post("/analyze/")
def post(input_dataset: UploadFile = File(...),
         config_file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    params = json.load(config_file.file)
    method = params["method"]
    if method not in config['analysis_methods']:
        task_message = f"Analysis method not valid: {method}"
        return {"message": task_message}
    task_id = str(uuid.uuid4().hex)
    print(task_id)
    background_tasks.add_task(analyze, input_dataset.file, input_dataset.filename, params, task_id)
    task_message = f"task {task_id} requested"
    return {"message": task_message}


@app.post("/compute_measures/")
def post(original_dataset: UploadFile = File(...), anonymized_dataset: UploadFile = File(...),
         config_file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    params = json.load(config_file.file)
    task_id = str(uuid.uuid4().hex)
    print(task_id)
    background_tasks.add_task(measures, original_dataset.file, anonymized_dataset.file,
                              original_dataset.filename, anonymized_dataset.filename, params, task_id)
    task_message = f"task {task_id} requested"
    return {"message": task_message}


@app.post("/filter/")
def post(input_dataset: UploadFile = File(...), config_file: UploadFile = File(...),
         background_tasks: BackgroundTasks = None):
    params = json.load(config_file.file)
    task_id = str(uuid.uuid4().hex)
    print(task_id)
    background_tasks.add_task(filter, input_dataset.file, input_dataset.filename, params, task_id)
    task_message = f"task {task_id} requested"
    return {"message": task_message}
