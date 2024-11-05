import requests
import pandas as pd

from docker_check import is_running_in_docker

(
    db_host,
    db_port,
    db_user,
    db_pwd,
    db_name,
    mongo_host,
    mongo_port,
    mongo_user,
    mongo_pwd,
    mongo_db,
) = is_running_in_docker()


def load_profile():
    """
    Loads profiles from database api.

    Args:
        None

    Returns:
        List: A list where each line is a line of the document(s).
    """
    try:
        # Load the profiles from the database
        response = requests.get(f"http://{db_host}:{db_port}/get_profiles")
        response.raise_for_status()

        # Convert the response to a Dataframe
        profiles = response.json().get("profiles")
        documents = pd.DataFrame(profiles)

        if documents.empty:
            return []
        else:
            documents = documents["combined"].tolist()

        return documents
    except Exception as e:
        raise ValueError(f"Error loading profiles: {e}")
