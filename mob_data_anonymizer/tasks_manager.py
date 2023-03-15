from mob_data_anonymizer import CONFIG_DB_FILE
from mob_data_anonymizer.make_api_call import MakeApiCall
import json
import re
import ntpath
from pathlib import Path


def request_return_task(task_id):
    api = MakeApiCall()

    filename = task_id + ".json"
    param = {"task_id": str(task_id)}

    response = api.get_user_data(param)
    try:
        d = response.headers['content-disposition']
    except KeyError:
        # print(f"Received: {response.content}")
        print(f"Received: {response.json()['message']}")
        return

    # filename = response.headers["content-disposition"].split(";")[1].split("=")[1]

    filename = re.findall("filename=\"(.+)\"", d)[0]
    filename = path_leaf(filename)

    if filename.endswith('.json'):
        with open(filename, 'w') as f:
            json.dump(response.json(), f, indent=4)
    else:
        with open(filename, 'wb') as f:
            f.write(response.content)

    print(f"Received: {filename}")


def return_task(task_id):
    # filename = CONFIG_DB_FILE + "mob_data_anonymizer/db/" + task_id + ".json"
    with open(CONFIG_DB_FILE) as param_file:
        data = json.load(param_file)
    filename = data['db_folder'] + task_id + ".json"
    path = Path(filename)
    if path.is_file():
        return filename
    filename = data['db_folder'] + task_id + ".csv"
    path = Path(filename)
    if path.is_file():
        return filename

    return None


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
