import json
import os
import time

import pandas as pd
import streamlit as st

from src import utils  # Assuming the utils module is available
from src.utils import PPTXExporter

# Streamlit App
st.title("Chat Explore Prompt Report Generator")

# Input fields for API Key and Project ID
API_KEY = st.text_input("Enter API Key", type="password")

utils.API_KEY = API_KEY

project_id = st.text_input("Enter Project ID")

# Browse for directory to save responses
resp_directory = st.text_input(
    "Enter directory to save artifacts",
    value="/Users/snuggeha/Documents/Internal-Utilities/ce-pptx-utilies/artifacts",
)

# Ensure directory exists
if resp_directory and not os.path.exists(resp_directory):
    st.write("Directory does not exist. Creating directory...")
    os.makedirs(resp_directory)

# Upload prompts Excel file
uploaded_file = st.file_uploader("Upload Excel file with prompts", type="xlsx")

if uploaded_file is not None and resp_directory:
    try:
        df = pd.read_excel(uploaded_file)
        prompts = df.iloc[:, 0].tolist()
    except Exception as e:
        st.error(f"Error occurred while importing prompts: {str(e)}")
        prompts = []

if st.button("Create Report Artifacts"):

    # Add validation handling so that the user cannot proceed without entering the required fields
    if not API_KEY or not project_id or not resp_directory or not prompts:
        st.error("Please fill in all the required fields and upload the prompts file.")
        st.stop()

    # Set up a progress bar
    progress_bar = st.progress(0)

    # Set up a placeholder for status messages
    status_text = st.empty()

    # Set up a placeholder for error messages
    error_placeholder = st.empty()

    # Example loop to demonstrate the progress
    total_iterations = len(prompts)
    for i, content in enumerate(prompts):

        # Update the progress bar with each iteration
        progress = int((i + 1) / total_iterations * 100)
        progress_bar.progress(progress)

        status_text.text(f"Processing prompt {i + 1} of {total_iterations}")

        creation_resp = utils.create_chat_request(project_id, content)

        task_id = creation_resp["task_id"]

        # Set a timeout for 5 minutes (300 seconds)
        timeout = 300
        format_type = "plotly_json"
        start_time = time.time()

        # Loop until the task status is "SUCCEEDED"
        while True:
            status = utils.check_task_status(task_id)
            if status["status"] == "SUCCEEDED":
                chat_id = status["metadata"]["location"].split("/chats/")[1]
                chat_response = utils.get_chat_results(chat_id, format_type)

                # File path with project_id and task_id
                file_name = f"project_{project_id}_taskid_{task_id}"
                file_path = os.path.join(resp_directory, file_name)

                utils.process_chat_output(chat_response, file_path)
                break

            elif status["status"] == "FAILED":
                error_placeholder.error("Task failed.")
                break

            elif time.time() - start_time > timeout:
                error_placeholder.error("Task timed out.")
                break

            # Wait for some time before checking again to avoid overwhelming the server
            time.sleep(5)

    # Display a message when done
    st.success("Processing complete!")

# Text box to name presentation
output_filename = st.text_input("Enter PPTX filename", value="output_deck.pptx")

if st.button("Export to PPTX"):

    # Add validation handling so that the user cannot proceed without entering the required fields
    if not API_KEY or not project_id or not resp_directory or not prompts:
        st.error("Please fill in all the required fields and upload the prompts file.")
        st.stop()

    # Setup
    pptx_filepath = os.path.join(resp_directory, output_filename)

    # Initialize object
    obj = PPTXExporter(resp_directory)

    # Create slides
    obj.create()

    obj.save(pptx_filepath)

    # Display a message when done
    st.success("PPTX export complete!")
