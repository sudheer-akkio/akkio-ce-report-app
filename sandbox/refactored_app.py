import os
import time
from typing import List, Dict, Any, Tuple, Optional

import akkio
import pandas as pd
import streamlit as st

from src.utils import (
    API_KEY,
    create_chat_request,
    check_task_status,
    get_chat_results,
    process_chat_output,
    transform_data,
    df_to_dict,
    create_dataset,
    PPTXExporter,
)

class AkkioApp:
    def __init__(self) -> None:
        self._api_key: str = ""
        self._project_id: str = ""
        self._resp_directory: str = ""
        self._prompts: List[str] = []
        self._df: Optional[pd.DataFrame] = None

    def run(self) -> None:
        st.title("Akkio Automation Utilities")
        tab1, tab2 = st.tabs(["Prompt Report Generation", "Transform Your Data"])

        with tab1:
            self._prompt_report_generation()

        with tab2:
            self._transform_data()

    def _prompt_report_generation(self) -> None:
        self._api_key = st.text_input("Enter API Key", type="password", key="api_key_tab1")
        API_KEY = self._api_key
        self._project_id = st.text_input("Enter Project ID", key="project_key_tab1")
        self._resp_directory = st.text_input(
            "Enter directory to save artifacts",
            value="/Users/snuggeha/Documents/Internal-Utilities/akkio-ce-report-app/artifacts",
        )

        self._ensure_directory_exists()
        self._upload_prompts_file()

        if st.button("Create Report Artifacts"):
            self._create_report_artifacts()

        output_filename = st.text_input("Enter PPTX filename", value="output_deck.pptx")
        if st.button("Export to PPTX"):
            self._export_to_pptx(output_filename)

    def _transform_data(self) -> None:
        self._api_key = st.text_input("Enter API Key", type="password", key="api_key_tab2")
        API_KEY = self._api_key
        akkio.api_key = self._api_key
        self._project_id = st.text_input("Enter Deployed Transform Project ID", key="project_key_tab2")
        project_name = st.text_input("Enter New Project Name", key="project_name_tab2")

        self._upload_data_file()

        predict_field = st.text_input("Enter Predict Field")

        if st.button("Transform Data"):
            self._transform_data_process(project_name, predict_field)

    def _ensure_directory_exists(self) -> None:
        if self._resp_directory and not os.path.exists(self._resp_directory):
            st.write("Directory does not exist. Creating directory...")
            os.makedirs(self._resp_directory)

    def _upload_prompts_file(self) -> None:
        uploaded_file = st.file_uploader(
            "Upload Excel file with prompts", type="xlsx", key="uploader_key_tab1"
        )
        if uploaded_file is not None and self._resp_directory:
            try:
                self._df = pd.read_excel(uploaded_file)
                self._prompts = self._df.iloc[:, 0].tolist()
            except Exception as e:
                st.error(f"Error occurred while importing prompts: {str(e)}")
                self._prompts = []

    def _upload_data_file(self) -> None:
        uploaded_file = st.file_uploader(
            "Upload Data", type=["xlsx", "csv"], key="uploader_key_tab2"
        )
        if uploaded_file is not None and self._resp_directory:
            try:
                file_extension = os.path.splitext(uploaded_file.name)[1]
                if file_extension == ".xlsx":
                    self._df = pd.read_excel(uploaded_file)
                elif file_extension == ".csv":
                    self._df = pd.read_csv(uploaded_file)
                else:
                    st.error(
                        "Invalid file format. Please upload either an Excel file (.xlsx) or a CSV file (.csv)."
                    )
                    self._df = None
            except Exception as e:
                st.error(f"Error occurred while importing data: {str(e)}")
                self._df = None

    def _create_report_artifacts(self) -> None:
        if not self._validate_inputs():
            return

        progress_bar, status_text, error_placeholder = self._setup_progress_indicators()

        total_iterations = len(self._prompts)
        for i, content in enumerate(self._prompts):
            self._process_prompt(i, content, total_iterations, progress_bar, status_text, error_placeholder)

        st.success("Processing complete!")

    def _validate_inputs(self) -> bool:
        if not self._api_key or not self._project_id or not self._resp_directory or not self._prompts:
            st.error("Please fill in all the required fields and upload the prompts file.")
            return False
        return True

    def _setup_progress_indicators(self) -> Tuple[st.progress, st.empty, st.empty]:
        progress_bar = st.progress(0)
        status_text = st.empty()
        error_placeholder = st.empty()
        return progress_bar, status_text, error_placeholder

    def _process_prompt(self, i: int, content: str, total_iterations: int,
                        progress_bar: st.progress, status_text: st.empty, error_placeholder: st.empty) -> None:
        progress = int((i + 1) / total_iterations * 100)
        progress_bar.progress(progress)
        status_text.text(f"Processing prompt {i + 1} of {total_iterations}")

        creation_resp = create_chat_request(self._project_id, content)
        task_id = creation_resp["task_id"]

        self._wait_for_task_completion(task_id, error_placeholder)

    def _wait_for_task_completion(self, task_id: str, error_placeholder: st.empty) -> None:
        timeout = 300
        format_type = "plotly_json"
        start_time = time.time()

        while True:
            status = check_task_status(task_id)
            if status["status"] == "SUCCEEDED":
                chat_id = status["metadata"]["location"].split("/chats/")[1]
                chat_response = get_chat_results(chat_id, format_type)
                file_name = f"project_{self._project_id}_taskid_{task_id}"
                file_path = os.path.join(self._resp_directory, file_name)
                process_chat_output(chat_response, file_path)
                break
            elif status["status"] == "FAILED":
                error_placeholder.error("Task failed.")
                break
            elif time.time() - start_time > timeout:
                error_placeholder.error("Task timed out.")
                break
            time.sleep(5)

    def _export_to_pptx(self, output_filename: str) -> None:
        if not self._validate_inputs():
            return

        pptx_filepath = os.path.join(self._resp_directory, output_filename)
        exporter = PPTXExporter(self._resp_directory)
        exporter.create()
        exporter.save(pptx_filepath)
        st.success("PPTX export complete!")

    def _transform_data_process(self, project_name: str, predict_field: str) -> None:
        if not self._validate_transform_inputs(project_name):
            return

        progress_bar, status_text, error_placeholder = self._setup_progress_indicators()

        status_text.text("Transforming data...")
        transformed_df = transform_data(self._project_id, df_to_dict(self._df), save=False)
        progress_bar.progress(50)

        status_text.text(f"Creating project with project name: {project_name}...")
        transformed_dataset_id = create_dataset(project_name, transformed_df)

        new_model = self._train_model(transformed_dataset_id, predict_field)
        if new_model["status"] != "success":
            raise ValueError(
                f"Project creation failed due to model training error. Model training details: {new_model}"
            )

        progress_bar.progress(100)
        st.success("Processing complete!")

        transformed_project_id = new_model["model_id"]
        st.write(f"New Project ID: {transformed_project_id}")

    def _validate_transform_inputs(self, project_name: str) -> bool:
        if not self._api_key or not self._project_id or not project_name or self._df is None:
            st.error("Please fill in all the required fields and upload data to be transformed.")
            return False
        return True

    def _train_model(self, dataset_id: str, predict_field: str) -> Dict[str, Any]:
        training_mode = 1
        predict_fields = [predict_field]
        ignore_fields: List[str] = []
        return akkio.create_model(
            dataset_id,
            predict_fields,
            ignore_fields,
            {"duration": training_mode, "extra_attention": False},
        )

if __name__ == "__main__":
    app = AkkioApp()
    app.run()
