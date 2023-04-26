from fastapi import FastAPI, Depends, File, UploadFile, BackgroundTasks, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from mob_data_anonymizer.utils.actions import anonymize
from mob_data_anonymizer.utils.actions import anonymize_back
from mob_data_anonymizer.utils.actions import anonymize_factory
from mob_data_anonymizer.utils.actions import analyze
from mob_data_anonymizer.utils.actions import analyze_back
from mob_data_anonymizer.utils.actions import analyze_factory
from mob_data_anonymizer.utils.actions import measures
from mob_data_anonymizer.utils.actions import measures_back
from mob_data_anonymizer.utils.actions import filter_back
from mob_data_anonymizer import tasks_manager
from mob_data_anonymizer.methodName import MethodName
import uuid
from mob_data_anonymizer import CONFIG_FILE
import json


class Params(BaseModel):
    input_file: str
    output_folder: str
    main_output_file: str
    save_preprocessed_dataset: bool
    preprocessed_file: str
    k: Optional[int] = 3
    interval: Optional[int] = 900
    landa: Optional[float] = 0


class ParamsMicro(BaseModel):
    input_file: Optional[str]
    output_folder: str = "examples/output"
    main_output_file: str = "anonymized_Microaggregation_CLI.csv"
    save_preprocessed_dataset: bool = True
    preprocessed_file: str = "preprocessed_dataset_CLI.csv"
    k: int = 3
    landa: Optional[float] = 0


class ParamsMicro2(BaseModel):
    input_file: Optional[str]
    output_folder: str = "examples/output"
    main_output_file: str = "anonymized_Microaggregation2_CLI.csv"
    save_preprocessed_dataset: bool = True
    preprocessed_file: str = "preprocessed_dataset_CLI.csv"
    k: int = 3
    interval: int = 900
    landa: Optional[float] = 0


class ParamsSwaplocations(BaseModel):
    input_file: Optional[str]
    output_folder: str = "examples/output"
    main_output_file: str = "anonymized_Microaggregation2_CLI.csv"
    save_preprocessed_dataset: bool = True
    preprocessed_file: str = "preprocessed_dataset_CLI.csv"
    k: int = 3
    max_r_s: int = 500
    min_r_s: int = 100
    max_r_t: int = 120
    min_r_t: int = 60


class ParamsSwapmob(BaseModel):
    input_file: Optional[str]
    output_folder: str = "examples/output"
    main_output_file: str = "anonymized_Microaggregation2_CLI.csv"
    save_preprocessed_dataset: bool = True
    preprocessed_file: str = "preprocessed_dataset_CLI.csv"
    spatial_thold: float = 0.1
    temporal_thold: float = 60


class ParamsSimpleGeneralization(BaseModel):
    input_file: Optional[str]
    output_folder: str = "examples/output"
    main_output_file: str = "anonymized_Microaggregation2_CLI.csv"
    save_preprocessed_dataset: bool = True
    preprocessed_file: str = "preprocessed_dataset_CLI.csv"
    gen_tile_size: int = 500
    tile_shape: str = "squared"
    traj_anon_tile_size: int = 1000
    overlapping_strategy: str = "all"


class ParamsMeasures(BaseModel):
    original_file: Optional[str]
    anonymized_file: Optional[str]
    output_folder: str = "examples/output"
    main_output_file: str = "measures.json"


class Measures(BaseModel):
    propensity: float
    rsme: float
    rsme_normalized: float
    percen_record_linkage: float
    percen_traj_removed: float
    percen_loc_removed: float


class ParamsAnalyze(BaseModel):
    method: str = "QuadTreeHeatMap"
    input_file: Optional[str]
    output_folder: str = "examples/output"
    main_output_file: str = "anonymous_QuadTreeHeatMap_CLI.json"
    save_preprocessed_dataset: bool = True
    preprocessed_file: str = "preprocessed_dataset_CLI.csv"
    min_k: int = 5
    max_locations: int = 1000
    min_sector_length: int = 50
    merge_sectors: bool = True


class ParamsFilter(BaseModel):
    input_file: Optional[str]
    main_output_file: str = "filtered_dataset.json"
    min_locations: int = 10
    max_speed: int = 300


# class Params(BaseModel):
#     method: str


app = FastAPI()


# @app.get("/anonymize/")
# def get(params: Params):
#     return {f"message: from anom get {params}"}


# @app.get("/")
# def get_root():
#     return {f"message: from root get"}


# @app.get("/task/")
# def get(task_id: str):
#     response_file_path = tasks_manager.return_task(task_id)
#     return FileResponse(response_file_path)


@app.get("/task/")
def get(task_id: str):
    response_file_path = tasks_manager.return_task(task_id)
    if response_file_path is None:
        task_message = f"task {task_id} not available or still processing"
        print(task_message)
        return {"message": task_message}
    else:
        response = FileResponse(response_file_path, filename=response_file_path)
        return response


# @app.post("/anonymize/Microaggregation/")
# def post(params: ParamsMicro = Depends(), files: List[UploadFile] = File(...)):
#     method = "Microaggregation"
#     response_file_path = anonymize(method, params, files[0].file)
#     return FileResponse(response_file_path)


# @app.post("/anonymize/Microaggregation/")
# def post(params: ParamsMicro = Depends(), files: List[UploadFile] = File(...),
#          background_tasks: BackgroundTasks = None):
#     method = "Microaggregation"
#     task_id = str(uuid.uuid4().hex)
#     background_tasks.add_task(anonymize_factory, method, params, files[0].file, files[0].filename, task_id)
#     task_message = f"task {task_id} requested"
#     return {"message": task_message}


# @app.post("/anonymize/Microaggregation2/")
# def post(params: ParamsMicro2 = Depends(), files: List[UploadFile] = File(...)):
#     method = "Microaggregation2"
#     response_file_path = anonymize(method, params, files[0].file)
#     return FileResponse(response_file_path)


# @app.post("/anonymize/TimePartMicroaggregation/")
# def post(params: ParamsMicro2 = Depends(), files: List[UploadFile] = File(...),
#          background_tasks: BackgroundTasks = None):
#     method = "TimePartMicroaggregation"
#     task_id = str(uuid.uuid4().hex)
#     background_tasks.add_task(anonymize_factory, method, params, files[0].file, files[0].filename, task_id)
#     task_message = f"task {task_id} requested"
#     return {"message": task_message}


@app.post("/anonymize/{method}")
def post(method: str, data_file: UploadFile = File(...),
         config_file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    if method not in config['anonymization_methods']:
        task_message = f"Anonymization method not valid: {method}"
        return {"message": task_message}
    task_id = str(uuid.uuid4().hex)
    background_tasks.add_task(anonymize_factory, data_file.file, data_file.filename,
                              config_file.file, task_id)
    task_message = f"task {task_id} requested"
    return {"message": task_message}


# @app.post("/anonymize/{method}")
# def post(method: str, files: List[UploadFile] = File(...), background_tasks: BackgroundTasks = None):
#     with open(CONFIG_FILE, 'r') as f:
#         config = json.load(f)
#     if method not in config['anonymization_methods']:
#         task_message = f"Anonymization method not valid: {method}"
#         return {"message": task_message}
#     task_id = str(uuid.uuid4().hex)
#     background_tasks.add_task(anonymize_factory, files[0].file, files[0].filename, files[1].file, task_id)
#     task_message = f"task {task_id} requested"
#     return {"message": task_message}


# @app.post("/anonymize/SwapLocations/")
# def post(params: ParamsSwaplocations = Depends(), files: List[UploadFile] = File(...)):
#     method = "SwapLocations"
#     response_file_path = anonymize(method, params, files[0].file)
#     return FileResponse(response_file_path)


# @app.post("/anonymize/SwapLocations/")
# def post(params: ParamsSwaplocations = Depends(), files: List[UploadFile] = File(...),
#          background_tasks: BackgroundTasks = None):
#     method = "SwapLocations"
#     task_id = str(uuid.uuid4().hex)
#     background_tasks.add_task(anonymize_factory, method, params, files[0].file, files[0].filename, task_id)
#     task_message = f"task {task_id} requested"
#     return {"message": task_message}


# @app.post("/anonymize/SwapMob/")
# def post(params: ParamsSwapmob = Depends(), files: List[UploadFile] = File(...)):
#     method = "SwapMob"
#     response_file_path = anonymize(method, params, files[0].file)
#     return FileResponse(response_file_path)


# @app.post("/anonymize/SwapMob/")
# def post(params: ParamsSwapmob = Depends(), files: List[UploadFile] = File(...),
#          background_tasks: BackgroundTasks = None):
#     method = "SwapMob"
#     task_id = str(uuid.uuid4().hex)
#     background_tasks.add_task(anonymize_factory, method, params, files[0].file, files[0].filename, task_id)
#     task_message = f"task {task_id} requested"
#     return {"message": task_message}


# @app.post("/anonymize/SimpleGeneralization/")
# def post(params: ParamsSimpleGeneralization = Depends(), files: List[UploadFile] = File(...),
#          background_tasks: BackgroundTasks = None):
#     method = "SimpleGeneralization"
#     task_id = str(uuid.uuid4().hex)
#     background_tasks.add_task(anonymize_factory, method, params, files[0].file, files[0].filename, task_id)
#     task_message = f"task {task_id} requested"
#     return {"message": task_message}


# @app.post("/analyze/")
# def post(params: ParamsAnalyze = Depends(), files: List[UploadFile] = File(...)):
#     response_file_path = analyze(params, files[0].file)
#     return FileResponse(response_file_path)


@app.post("/analyze/{method}")
def post(method:str, data_file: UploadFile = File(...),
         config_file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    if method not in config['analysis_methods']:
        task_message = f"Analysis method not valid: {method}"
        return {"message": task_message}
    task_id = str(uuid.uuid4().hex)
    print(task_id)
    background_tasks.add_task(analyze_factory, data_file.file, data_file.filename, config_file.file, task_id)
    task_message = f"task {task_id} requested"
    return {"message": task_message}


# @app.post("/analyze/")
# def post(params: ParamsAnalyze = Depends(), files: List[UploadFile] = File(...),
#          background_tasks: BackgroundTasks = None):
#     task_id = str(uuid.uuid4().hex)
#     print(task_id)
#     background_tasks.add_task(analyze_back, params, files[0].file, files[0].filename, task_id)
#     task_message = f"task {task_id} requested"
#     return {"message": task_message}


# @app.post("/measures/")
# def post(params: ParamsMeasures = Depends(), files: List[UploadFile] = File(...)) -> Measures:
#     response_measures = measures(params, files[0].file, files[1].file)
#     return Measures(propensity=response_measures["propensity"],
#                     rsme=response_measures["rsme"],
#                     rsme_normalized=response_measures["rsme_normalized"],
#                     percen_record_linkage=response_measures["percen_record_linkage"],
#                     percen_traj_removed=response_measures["percen_traj_removed"],
#                     percen_loc_removed=response_measures["percen_loc_removed"])


@app.post("/compute_measures/")
def post(params: ParamsMeasures = Depends(), files: List[UploadFile] = File(...),
         background_tasks: BackgroundTasks = None):
    task_id = str(uuid.uuid4().hex)
    background_tasks.add_task(measures_back, params, files[0].file, files[1].file,
                              files[0].filename, files[1].filename, task_id)
    task_message = f"task {task_id} requested"
    return {"message": task_message}


@app.post("/filter/")
def post(params: ParamsFilter = Depends(), files: List[UploadFile] = File(...),
         background_tasks: BackgroundTasks = None):
    task_id = str(uuid.uuid4().hex)
    print(task_id)
    background_tasks.add_task(filter_back, params, files[0].file, files[0].filename, task_id)
    task_message = f"task {task_id} requested"
    return {"message": task_message}
