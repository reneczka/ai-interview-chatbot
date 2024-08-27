from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models
from openai import OpenAI
from dotenv import load_dotenv
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_question(job_title):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant conducting a job interview."},
            {"role": "user", "content": f"Generate an interview question for a {job_title} position."}
        ]
    )
    return response.choices[0].message.content

@app.get("/")
def read_root():
    return {"Hey": "Renia"}


@app.get("/jobs/")
def read_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.Job).all()
    return jobs


@app.get("/jobs/{job_id}")
def read_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/jobs/{job_id}/technologies/")
def read_technologies(job_id: int, db: Session = Depends(get_db)):
    technologies = db.query(models.Technology).filter(models.Technology.job_id == job_id).all()
    if not technologies:
        raise HTTPException(status_code=404, detail="No technologies found for this job")
    return technologies
    # # only the names of the technologies
    # technology_names = [tech.tech for tech in technologies]
    # return technology_names


@app.get("/jobs/{job_id}/interview-start")
async def start_interview(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    welcome_message = f"Welcome to the mock interview for {job.job_name} at {job.company_name}!"
    first_question = generate_question(job.job_name)
    
    return {"welcome_message": welcome_message, "first_question": first_question}


@app.get("/jobs/{job_id}/interview-finish")
async def finish_interview(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    bye_message = f"Thank you for participating in the mock interview for {job.job_name} at {job.company_name}. Hope you enjoyed it, see you soon!"

    return {"bye_message": bye_message}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)


# def evaluate_answer(job_title, question, answer):
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are an AI assistant evaluating job interview answers."},
#             {"role": "user", "content": f"Evaluate this answer for a {job_title} position. Question: {question}, Answer: {answer}"}
#         ]
#     )
#     return response.choices[0].message['content']


# uvicorn main:app --reload