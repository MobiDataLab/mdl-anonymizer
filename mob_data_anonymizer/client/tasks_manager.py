from mob_data_anonymizer.client.make_api_call import MakeApiCall
import json
import re
import ntpath


def request_return_task(task_id):
    api = MakeApiCall()

    param = {"task_id": str(task_id)}

    response = api.get_user_data(param)
    try:
        d = response.headers['content-disposition']
    except KeyError:
        print(f"Received: {response.json()['message']}")
        return

    filename = re.findall("filename=\"(.+)\"", d)[0]
    filename = path_leaf(filename)

    if filename.endswith('.json'):
        with open(filename, 'w') as f:
            json.dump(response.json(), f, indent=4)
    else:
        with open(filename, 'wb') as f:
            f.write(response.content)

    print(f"Received: {filename}")


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
