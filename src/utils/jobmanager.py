import json
import os
from src.Config import JOB_DATA_FILE


def _job_entries(job_data: dict):
    """
    Yield job_id/user_id pairs, and skip over the jobs
    """
    for job_id, user_id in job_data.items():
        if job_id == "jobs":
            continue
        yield job_id, user_id

def verify_job_data_file():
    """
    Ensures the job data file is present
    """

    # create the file if it doesn't exist
    # with a dictionary
    if not os.path.isfile(JOB_DATA_FILE):
        with open(JOB_DATA_FILE, 'w') as f:
            json.dump(obj={"jobs": 0}, fp=f, indent=4)


def get_all_jobs() -> dict:
    """
    Get all jobs
    """
    verify_job_data_file()

    # get all jobs
    all_jobs = None
    with open(JOB_DATA_FILE, 'r') as f:
        all_jobs = json.load(f)

    return all_jobs


def save_jobs(jobs: dict):
    """
    Save all jobs ig
    """
    verify_job_data_file()

    with open(JOB_DATA_FILE, 'w') as f:
        json.dump(obj=jobs, fp=f, indent=4)


def add_job(user_id: int) -> int:
    """
    Add a new job for the given user ID and return its job ID
    """

    all_jobs: dict = get_all_jobs()
    user_id_str = str(user_id)

    # prevent duplicate jobs per user
    for _, existing_user_id in _job_entries(all_jobs):
        if existing_user_id == user_id_str:
            return -1

    all_jobs["jobs"] += 1
    job_id = all_jobs["jobs"]
    all_jobs[str(job_id)] = user_id_str

    save_jobs(all_jobs)
    return job_id

def remove_job(job_id: int):
    """
    Remove a job based on job ID
    """

    all_jobs: dict = get_all_jobs()
    job_key = str(job_id)

    if job_key in all_jobs:
        del all_jobs[job_key]
        save_jobs(all_jobs)


def get_user_id(job_id: int) -> int:
    """
    Return the user ID for a given job ID, or -1 if missing
    """

    all_jobs: dict = get_all_jobs()
    user_id_str = all_jobs.get(str(job_id))

    if user_id_str is None:
        return -1

    try:
        return int(user_id_str)
    except ValueError:
        return user_id_str

def get_job_id(user_id: int) -> int:
    """
    Return the job ID for a given user ID, or -1 if missing
    """

    all_jobs: dict = get_all_jobs()
    user_id_str = str(user_id)

    for job_id, existing_user_id in _job_entries(all_jobs):
        if existing_user_id == user_id_str:
            return int(job_id)

    return -1