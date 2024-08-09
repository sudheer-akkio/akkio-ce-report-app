import json
import os
import time

import pandas as pd

from src import utils

# Setup
API_KEY = "463c3703-cb1d-434b-a540-bbcb4b5db0d7"  # INSERT API KEY HERE

utils.API_KEY = API_KEY

# Directory to save responses
resp_directory = "artifacts"
os.makedirs(resp_directory, exist_ok=True)  # Ensure directory exists

# Get project ID from UI
project_id = "jF4vcd53hUYWLkFYzlqj"  # INSERT PROJECT ID HERE

# Load prompts from Excel file
df = pd.read_excel("prompt_list.xlsx")

prompts = df.iloc[:, 0].tolist()

for i, content in enumerate(prompts):

    print("Processing prompt: ", i + 1)
    creation_resp = utils.create_chat_request(project_id, content)
    print(creation_resp)

    task_id = creation_resp["task_id"]

    # Set a timeout for 5 minutes (300 seconds)
    timeout = 300
    format_type = "plotly_json"
    start_time = time.time()  # Get the current time to measure against the timeout

    # Loop until the task status is "SUCCEEDED"
    while True:
        status = utils.check_task_status(task_id)
        print(status)
        if status["status"] == "SUCCEEDED":
            chat_id = status["metadata"]["location"].split("/chats/")[1]
            chat_response = utils.get_chat_results(chat_id, format_type)

            # File path with project_id and task_id
            file_name = f"project_{project_id}_taskid_{task_id}"
            file_path = os.path.join(resp_directory, file_name)

            # Save the response to a text file
            # with open(file_path, "w") as file:
            #     json.dump(chat_response, file, indent=4)
            # print(f"Response saved to {file_path}")

            utils.process_chat_output(chat_response, file_path)

            break
        elif status["status"] == "FAILED":
            print("Task failed.")
            break

        elif time.time() - start_time > timeout:
            print("Task timed out.")
            break

        # Wait for some time before checking again to avoid overwhelming the server
        time.sleep(5)  # Sleep for 5 seconds
    print("Done processing prompt: ", i + 1)
