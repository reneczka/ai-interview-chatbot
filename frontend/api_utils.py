import requests


def fetch_jobs_data(jobs_url):
    try:
        response = requests.get(jobs_url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to fetch jobs: {e}")
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
        print(f"Failed to send message: {e}")
        return None