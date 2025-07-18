from typing import Dict, Tuple, List
import requests
import pandas as pd
from pandas import DataFrame
from agent import build_graph
from pathlib import Path
import tempfile
import re


# Constants

DEFAULT_API_URL = "https://agents-course-unit4-scoring.hf.space"
QUESTIONS_URL = f"{DEFAULT_API_URL}/questions"
SUBMIT_URL = f"{DEFAULT_API_URL}/submit"
FILE_PATH = f"{DEFAULT_API_URL}/files/"


# --- Functions ---

def get_questions() -> Dict:
    """Fetch questions from the API
    Returns:
        Dict: A dictionary containing the questions
    """

    response = requests.get(QUESTIONS_URL)
    return response.json()

def submit_answer(submission_data: Dict, results_log: list) -> tuple[str, Dataframe]:
    """Submits answers to the scoring API and returns the submission status and results
    
    Args:
        submission_data (Dict): A dictionary containing the submission data
        results_log (list): A list of dictionaries containing results log. This log is converted to a pandas dataframe.

    Returns:
        tuple[str, DataFrame]: A tuple containing the submission status and a pandas dataframe containing the results log.
    """

    response = requests.post(SUBMIT_URL, json=submission_data)
    result_data = response.json()
    final_status = (
            f"Submission Successful!\n"
            f"User: {result_data.get('username')}\n"
            f"Overall Score: {result_data.get('score', 'N/A')}% "
            f"({result_data.get('correct_count', '?')}/"
            f"{result_data.get('total_attempted', '?')} correct)\n"
            f"Message: {result_data.get('message', 'No message received.')}"
        )
    print("Submission successful.")
    results_df = pd.DataFrame(results_log)
    return final_status, results_df

def run_agent( gaia_agent: build_graph, questions: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    results_log = []
    answers_payload = []

    print(f"🚀 Running agent on {len(questions_data)} questions...")
    for item in questions:
        task_id = item.get("task_id")
        question_text = item.get("question")
        question_text = process_file(task_id, question_text)
        if not task_id or question_text is None:
            print(f"⚠️ Skipping invalid item (missing task_id or question): {item}")
            continue
        try:
            submitted_answer = gaia_agent(task_id, question_text)
            answers_payload.append(
                {"task_id": task_id, "submitted_answer": submitted_answer}
            )
        except Exception as e:
            print(f"❌ Error running agent on task {task_id}: {e}")
            submitted_answer = f"AGENT ERROR: {e}"

        results_log.append(
            {
                "Task ID": task_id,
                "Question": question_text,
                "Submitted Answer": submitted_answer,
            }
        )
    return results_log, answers_payload




def process_file(task_id: str, question_text: str) -> str:
    """
    Attempt to download a file associated with a task from the API.
    - If the file exists (HTTP 200), it is saved to a temp directory and the local file path is returned.
    - If no file is found (HTTP 404), returns None.
    - For all other HTTP errors, the exception is propagated to the caller.
    """
    file_url = f"{FILE_PATH}{task_id}"

    try:
        response = requests.get(file_url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(f"Exception in download_file>> {str(exc)}")
        return question_text # Unable to get the file

    # Determine filename from 'Content-Disposition' header, fallback to task_id
    content_disposition = response.headers.get("content-disposition", "")
    filename = task_id
    match = re.search(r'filename="([^"]+)"', content_disposition)
    if match:
        filename = match.group(1)

    # Save file in a temp directory
    temp_storage_dir = Path(tempfile.gettempdir()) / "gaia_cached_files"
    temp_storage_dir.mkdir(parents=True, exist_ok=True)

    file_path = temp_storage_dir / filename
    file_path.write_bytes(response.content)
    return (
                f"{question_text}\n\n"
                f"---\n"
                f"A file was downloaded for this task and saved locally at:\n"
                f"{str(file_path)}\n"
                f"---\n\n"
            )

