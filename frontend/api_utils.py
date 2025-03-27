import requests
import logging
import streamlit as st

# Configure logger for terminal output
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Add console handler to ensure logs are printed to terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def fetch_jobs_data(jobs_url):
    try:
        response = requests.get(jobs_url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch jobs: {e}")
        return None

def send_message(message_url, job_id, message):
    try:
        response = requests.post(
            message_url,
            json={"job_id": job_id, "user_message": message}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to send message: {e}")
        return None