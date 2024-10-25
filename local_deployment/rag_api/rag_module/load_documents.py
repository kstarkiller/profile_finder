import os
import sys
import requests
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from docker_check import is_running_in_docker

db_host, api_host = is_running_in_docker()

def load_profile():
    """
    Loads profiles from database api.

    Args:
        None

    Returns:
        List: A list where each line is a line of the document(s).
    """
    # Load the profiles from the database
    response = requests.get(f"http://{db_host}:5050/get_profiles")
    response.raise_for_status()

    # Convert the response to a Dataframe
    profiles = response.json().get("profiles")
    documents = pd.DataFrame(profiles)

    documents = documents["combined"].tolist()

    return documents

load_profile()
