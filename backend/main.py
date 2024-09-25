from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models as models
from dotenv import load_dotenv
from pydantic import BaseModel
import ai as ai
from typing import Optional, List, Dict


Base.metadata.create_all(bind=engine)

app = FastAPI()

load_dotenv()

welcome_message = 'Welcome to the interview for the {job_name}.'
farewell_message = 'Thank you for participating in the interview. We wish you the best of luck!'
max_questions = 3


class InterviewRequest(BaseModel):
    job_id: int
    user_message: Optional[str] = None

class InterviewResponse(BaseModel):
    ai_messages: List[str]
    interview_ended: bool = False

class InterviewState:
    def __init__(self, job: models.Job):
        self.job = job
        self.messages = []
        self.question_count = 0
        self.interview_ended = False

    def get_interview_history(self) -> List[Dict[str, str]]:
        system_prompt = f"""
        You are an AI assistant conducting a job interview for the position of {self.job.job_name}.
        Job Description:
        {self.job.job_description}

        Your tasks:
        1. Generate relevant technical questions based on the job description.
        2. Evaluate the candidate's answers to the questions.
        3. If the candidate's answer is unclear or lacking detail, provide feedback and hints to help them elaborate.
        4. After evaluating the answer, generate the next question in the interview.

        Guidelines:
        - Keep questions technical and relevant to the role.
        - Provide constructive feedback for each answer before asking the next question.
        - If the candidate doesn't know the answer, offer a brief explanation and move to a related but different question.
        - Maintain a professional and encouraging tone throughout the interview.

        In your first response, generate the first technical question for the interview.
        In subsequent responses, evaluate the previous answer, provide feedback, and ask the next question.
        After the final question, provide an overall evaluation of the candidate's performance.

        Remember, you are evaluating the candidate's technical skills and problem-solving abilities relevant to the {self.job.job_name} position.
        """
        history = [{"role": "system", "content": system_prompt}] + self.messages
        return history

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

interview_states = {}

### 
class TechnologyResponse(BaseModel):
    tech: str
    level: str

class JobResponse(BaseModel):
    id: int
    job_name: str
    company_name: str
    job_location: str
    salary: Optional[str]
    job_url: str
    type_of_work: str
    experience: str
    employment_type: str
    operating_mode: str
    job_description: Optional[str]
    technologies: List[TechnologyResponse]

@app.get("/jobs/", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.Job).all()
    
    job_responses = []
    for job in jobs:
        technologies = [TechnologyResponse(tech=tech.tech, level=tech.level) for tech in job.technologies]
        job_response = JobResponse(
            id=job.id,
            job_name=job.job_name,
            company_name=job.company_name,
            job_location=job.job_location,
            salary=job.salary,
            job_url=job.job_url,
            type_of_work=job.type_of_work,
            experience=job.experience,
            employment_type=job.employment_type,
            operating_mode=job.operating_mode,
            job_description=job.job_description,
            technologies=technologies
        )
        job_responses.append(job_response)
    
    return job_responses

###

def get_job_details(job_id: int, db: Session) -> models.Job:
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.post("/message/")
def process_message(message: InterviewRequest, db: Session = Depends(get_db)) -> InterviewResponse:
    state = interview_states.get(message.job_id)

    if not message.user_message:
        if state and state.interview_ended:
            return InterviewResponse(ai_messages=[farewell_message], interview_ended=True)

        job = get_job_details(message.job_id, db)
        state = InterviewState(job)
        interview_states[message.job_id] = state

        first_question = ai.generate_first_question(state.get_interview_history())
        state.add_message("assistant", first_question)
        state.question_count += 1

        formatted_welcome = welcome_message.format(job_name=job.job_name)

        return InterviewResponse(ai_messages=[formatted_welcome, first_question])

    if state.interview_ended:
        raise HTTPException(status_code=400, detail="Invalid interview state")

    state.add_message("user", message.user_message)
    interview_history = state.get_interview_history()

    if state.question_count < max_questions:
        ai_response = ai.generate_evaluation_and_next_question(interview_history)
        state.add_message("assistant", ai_response)
        state.question_count += 1
        return InterviewResponse(ai_messages=[ai_response])
    else:
        final_evaluation = ai.generate_final_evaluation(interview_history)
        state.add_message("assistant", final_evaluation)
        state.interview_ended = True
        return InterviewResponse(ai_messages=[final_evaluation, farewell_message], interview_ended=True)

if __name__ == "__main__":
    import uvicorn
    print("# # # # # # # # # # # # Starting the BACKEND server")
    uvicorn.run(app, host="localhost", port=8000)

# uvicorn main:app --reload