from fastapi import Depends
from configparser import ConfigParser
from getpass import getpass
from os import path
from routers.data import minio_bucket_download
from dependencies.dependencies import token_validity
import re
import os
import glob
import pandas as pd
import json
CONF_FILE = "./pit.ini"


def clear_console():
    print("\n" * 150)


def get_variable(message, hide=False, cls=False, default=None):
    """Get variable from  terminal.

    Args:
        message (str): message you want to print in the terminal.
        hide (bool, optional): Hides the entered value. Defaults to False.
        cls (bool, optional): Clean the terminal. Defaults to False.
        default (str, optional): If there is a default value for your variable. Defaults to None.

    Returns:
        str: The entered value.
    """
    if cls:
        clear_console()

    if hide is True:
        result = ""
        while result == "":
            result = getpass(message)
    else:
        result = input(f"{message} (default: {default})")

    if result is None or result == "":
        result = default

    return str(result)


def process_conf_file(conf_file=CONF_FILE):
    """
    Process configuration file for retrieving data.

        Parameters:
            conf_file (ini): The configuration file in ini file format

        Returns:
            credentials (str): the username and/or password for connecting to the PIT Server
            base_url (str): The url of PIT Server
    """
    config_object = ConfigParser()
    credentials = {}
    base_url = None
    if path.isfile(conf_file):
        config_object.read(conf_file)
        if "email" in config_object["AUTH"] and "url" in config_object["BASEURL"]:
            credentials["username"] = config_object["AUTH"]["email"]
            base_url = config_object["BASEURL"]["url"]
            if "password" in config_object["AUTH"]:
                credentials["password"] = config_object["AUTH"]["password"]
            else:
                message = f'Enter the paswword ({credentials["username"]}): '
                credentials["password"] = get_variable(message, True)
    return credentials, base_url


def request_connection(client, url, user, password):
    """
    Request connection to OKA Server.

        Parameters:
            url (str): The url of OKA server login
            user (str): The username (Email) of registered and active user
            password (str): The password of user

        Returns:
            csrf_token (str): The csrf_token or error of connection to PIT Server
    """
    login_url = url + "/login/"
    client.get(login_url)  # sets cookie
    csrf_token = client.cookies["csrftoken"]
    login_data = {
        "email": user,
        "password": password,
        "csrfmiddlewaretoken": csrf_token,
    }
    r = client.post(login_url, data=login_data)
    if r.status_code == 200:
        return {"csrf_token": csrf_token}
    else:
        return {"Error": r.reason}


def get_data(client, url_data, csrf_token, jobs={}):
    """
    Get data from OKA Server.

        Parameters:
            client (Request): Request session for connecting to OKA server
            url_data (str): OKA server API url
            csrf_token (str): Connection csrfmiddlewaretoken from OKA server

        Returns:
            data_json (json): requested data or error from OKA server
    """
    data = {"data": jobs, "csrfmiddlewaretoken": csrf_token}

    r = client.post(
        url_data,
        json=data,
        cookies={"csrftoken": csrf_token},
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token,
        },
    )
    print(r.content)
    r.raise_for_status()
    if r.status_code == 200 and r.headers["content-type"].strip().startswith("application/json"):
        data_json = r.json()
        return data_json
    else:
        return {"Error": r.reason}

def get_simple_data(client, url_data, csrf_token):
    """
    Get data from OKA Server.

        Parameters:
            client (Request): Request session for connecting to OKA server
            url_data (str): OKA server API url
            csrf_token (str): Connection csrfmiddlewaretoken from OKA server

        Returns:
            data_json (json): requested data or error from OKA server
    """

    r = client.get(
        url_data,
        cookies={"csrftoken": csrf_token},
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token,
        },
    )
    r.raise_for_status()
    if r.status_code == 200 and r.headers["content-type"].strip().startswith("application/json"):
        data_json = r.json()
        return data_json
    else:
        return {"Error": r.reason}

def send_data(client, url_data, csrf_token, application, loops, job_features):
    """
    Get data from OKA Server.

        Parameters:
            client (Request): Request session for connecting to OKA server
            url_data (str): OKA server API url
            csrf_token (str): Connection csrfmiddlewaretoken from OKA server
            application (file): ear application file
            loops (file): ear loops file
            job_features (dict): input size and application
        Returns:
            data_json (json): requested data or error from OKA server
    """
    data = {
        "job_features": [job_features],
        "csrfmiddlewaretoken": csrf_token,
    }
    files = {
        "application": open(application, "rb"),
        "loops": open(loops, "rb"),
    }

    r = client.post(
        url_data,
        data=data,
        files=files,
        cookies={"csrftoken": csrf_token},
        headers={"X-CSRFToken": csrf_token},
    )
    if r.status_code == 200:
        if os.path.exists(application) and os.path.exists(loops):
            os.remove(application)
            os.remove(loops)
        else:
            print("The files does not exist")
        data_json = r.json()

        return data_json
    else:
        return {"Error": r.reason}


async def parse_workflow(
    script_path: str,
    token: str = Depends(token_validity)
):
    """HEROES Workflow Script parser function.

    This function allows the authenticated user to parse a workflow script.
    Return a list of workflow tasks
    """
    try:
        # decoded_token = await decode_token(token)

        tasks = {}
        script_bucket = f"{script_path.split('/')[1]}"
        script_file = script_path.split('/')[-1]
        script_path_on_bucket = f"/{'/'.join(script_path.split('/')[2:])}"
        print("PARSE WORKFLOW")
        print(script_file)
        await minio_bucket_download(
            script_bucket,
            script_path_on_bucket,
            token
        )
        print("Workflow parser")

        with open(script_file, 'r') as file_downloaded:
            script_file_lines = file_downloaded.readlines()
        for current_line in script_file_lines:
            # print("Line{}: {}".format(head,20 line.strip()))  # Debug
            if re.match('^(process ).+( {)$', current_line.strip()):
              print("process: {}".format(current_line.strip().split(' ')[1]))
              current_process = current_line.strip().split(' ')[1]
              tasks[current_process] = {}
            elif re.match('^(cpus = \'HEROES_CPUS\')', current_line.strip()):
              tasks[current_process]["cpus"] = "HEROES_CPUS"
              print(current_line.strip())
            elif re.match('^(memory = \'HEROES_MEMORY\')', current_line.strip()):
              tasks[current_process]['memory'] = "HEROES_MEMORY"
              print(current_line.strip())
            elif re.match('^(time = \'HEROES_TIME\')', current_line.strip()):
              tasks[current_process]['time'] = "HEROES_TIME"
              print(current_line.strip())
        return tasks
    except Exception as e:
        raise e


def get_ear_data(ear_application_path, ear_loops_path):

    # Applications files
    csv_files = glob.glob(ear_application_path + "/*.heroes*.csv")
    df_list = [pd.read_csv(file, sep=";") for file in csv_files]

    big_df = pd.concat(df_list, ignore_index=True, sort=False)
    big_df.to_csv(ear_loops_path + "/ear_heroes.app.csv", sep=";", index=False)

    # Loops files
    csv_files = glob.glob(ear_loops_path + "/*.heroes.loops.csv")
    df_list = [pd.read_csv(file, sep=";") for file in csv_files]

    big_df = pd.concat(df_list, ignore_index=True, sort=False)
    big_df.to_csv(ear_loops_path + "/ear_heroes.loops.csv", sep=";", index=False)

    return {"apps": ear_loops_path + "/ear_heroes.app.csv" , "loops": ear_loops_path + "/ear_heroes.loops.csv"}


def slice_to_string_key(data):
    new_data = {}
    for elt in data:
        new_data[elt[0]] = data[elt]
    return new_data

def add_unit(unit, value):
    result = 0
    # GB to Bytes
    if unit == "memory" :
        result = str(value) + " B"
    elif unit == "time":
        result = str(value) + "s"
    return result
