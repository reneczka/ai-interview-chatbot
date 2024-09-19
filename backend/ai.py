from openai import OpenAI
import os
from typing import List, Dict
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def request_AI(job_id: int, interview_history: List[Dict[str, str]], model: str = "gpt-4o-mini", max_tokens: int = 500) -> str:
    payload = {
        "messages": interview_history,
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0.3,
        "top_p": 0.9,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.1
    }

    print("Messages sent to OpenAI:", json.dumps(interview_history, indent=2))

    try:
        response = client.chat.completions.create(**payload)
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in AI request: {str(e)}")
        return "I apologize, but I'm having trouble generating a response at the moment. Let's move on to the next question."

def generate_first_question(job, job_id: int, interview_history: List[Dict[str, str]]) -> str:
    return request_AI(job_id, interview_history)

def generate_evaluation_and_next_question(job, job_id: int, interview_history: List[Dict[str, str]]) -> str:
    return request_AI(job_id, interview_history)

def generate_final_evaluation(job, job_id: int, interview_history: List[Dict[str, str]]) -> str:
    prompt = "Please provide a final evaluation of the candidate's performance throughout the interview. Summarize their strengths and areas for improvement based on their responses to all questions."
    interview_history.append({"role": "user", "content": prompt})
    return request_AI(job_id, interview_history)



