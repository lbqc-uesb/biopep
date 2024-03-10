from datetime import datetime
import os
import pandas as pd


# Start a task, generating an output folder with current datetime and task name
def generate(
    option: str,
    query: str,
    cutoff: int,
    taskname: str,
    input_type: str,
    receptor: str,
    site: str,
) -> dict:
    dt = datetime.today()
    directory = f'{dt.strftime("%Y_%m_%d_%H%M%S")}_{taskname}'

    # generate output folder
    output_path = f"{os.getcwd()}/output/{directory}"
    print(f"Generated output in: output/{directory}")
    os.mkdir(output_path)

    # add task to tasks file
    tasks_file = f"{os.getcwd()}/app/data/tasks.csv"

    data = {
        "id": [format_id(taskname, dt.strftime("%Y/%m/%d %H:%M:%S"))],
        "option": [option],
        "query": [query],
        "cutoff": [cutoff],
        "taskname": [taskname],
        "input_type": [input_type],
        "receptor": [receptor],
        "site": [site],
        "created_at": [dt.strftime("%Y/%m/%d %H:%M:%S")],
        "finished_at": [None],
    }

    if os.path.isfile(tasks_file):
        df_tasks = pd.read_csv(tasks_file)
        df_tasks = pd.concat([df_tasks, pd.DataFrame(data)], ignore_index=True)
    else:
        df_tasks = pd.DataFrame(data)

    df_tasks.to_csv(tasks_file, index=False)

    return pd.DataFrame(data).iloc[0].to_dict()


def format_id(taskname: str, created_at: str):
    dt = datetime.strptime(created_at, "%Y/%m/%d %H:%M:%S")

    return f'{dt.strftime("%Y_%m_%d_%H%M%S")}_{taskname}'


def finish(task_id: str):
    dt = datetime.today()

    df = pd.read_csv(f"{os.getcwd()}/app/data/tasks.csv")
    df.loc[df["id"] == task_id, ["finished_at"]] = dt.strftime("%Y/%m/%d %H:%M:%S")

    df.to_csv(f"{os.getcwd()}/app/data/tasks.csv", index=False)
