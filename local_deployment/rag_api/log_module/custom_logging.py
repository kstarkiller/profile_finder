import logging
import os

# Logs path
base_path = os.path.dirname(__file__)
logs_path = os.path.join(base_path, "logs", "local_api_access.log")


# Logging module configuration
logging.basicConfig(
    filename=logs_path,  # Log file name
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)


# Log access
def log_access(username, success):
    """
    Logs a login attempt.

    Args:
        username (str): The username attempting to log in.
        success (bool): Indicates whether the login was successful or failed.
    """
    if success:
        logging.info(f"Successful login for user: {username}")
    else:
        logging.warning(f"Login failed for user: {username}")


# Log the asked question and the generated response
def log_response(question, response):
    """
    Logs the asked question and the generated response.

    Args:
        question (str): The question asked.
        response (str): The generated response.
    """
    logging.info("")
    logging.info(f"Question asked: {question}")
    logging.info("")
    logging.info(f"Generated response: {response}")
    logging.info("")


# Monitoring logs for failed login attempts
def monitor_logs(log_file="logs/local_api_access.log"):
    """
    Monitors the log file for login failures.

    Args:
        log_file (str): The path to the log file.
    """
    with open(log_file, "r") as file:
        logs = file.readlines()

    failed_attempts = [log for log in logs if "Login failed" in log]

    if failed_attempts:
        print(f"{len(failed_attempts)} login failures detected:")
        for attempt in failed_attempts:
            print(attempt.strip())
    else:
        print("No login failures detected.")
