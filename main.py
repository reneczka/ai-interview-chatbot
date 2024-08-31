from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models
from openai import OpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel

Base.metadata.create_all(bind=engine)
app = FastAPI()
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ReqMessage(BaseModel):
    jobId: int
    userMessage: str | None = None

class ResMessage(BaseModel):
    aiMessage: list[str]

message_count = 0

@app.post("/message/")
def send_message(
    req_message: ReqMessage, db: Session = Depends(get_db)) -> ResMessage:
    global message_count

    if not req_message.userMessage:
        message_count = 1
        job = db.query(
            models.Job).filter(models.Job.id == req_message.jobId).first()
        if not job:
            raise HTTPException(status_code=400, detail="No job found")

        welcome_message = f"Welcome to the interview for the position of {job.job_name}. I'll be asking you some questions related to the job. Let's begin!"

        # prompt = f"Create a job interview question for the following job description: {job.job_description}. Do not ask about user's past projects, ask technical questions."
        # response = client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages=[{
        #         "role":
        #         "system",
        #         "content":
        #         "You are an AI assistant that generates job interview questions."
        #     }, {
        #         "role": "user",
        #         "content": prompt
        #     }])

        # interview_question = response.choices[0].message.content.strip()

        #TODO! delete mock ansert
        ai_mock = "This is mock ai answer"

        print("# # # # # # # # # # # #", f"Message Count = {message_count}")

        return ResMessage(aiMessage=[welcome_message, ai_mock])

    message_count += 1

    if message_count == 10:
        final_evaluation = "Based on your answers, you have demonstrated a strong understanding of the required skills. Good luck with your job search!"
        bye_bye_message = "Thank you for participating in this interview. Bye bye!"
        print("# # # # # # # # # # # #", f"Message Count = {message_count}")
        message_count = 0
        return ResMessage(aiMessage=[final_evaluation, bye_bye_message])

    # Otherwise, continue the interview with the next question
    job = db.query(
        models.Job).filter(models.Job.id == req_message.jobId).first()
    if not job:
        raise HTTPException(status_code=400, detail="No job found")

    # prompt = f"Create a job interview question for the following job description: {job.job_description}. Do not ask about user's past projects, ask technical questions."
    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[{
    #         "role":
    #         "system",
    #         "content":
    #         "You are an AI assistant that generates job interview questions."
    #     }, {
    #         "role": "user",
    #         "content": prompt
    #     }])

    # interview_question = response.choices[0].message.content.strip()

    #TODO! delete mock answer
    ai_mock = "This is mock ai answer"

    print("# # # # # # # # # # # #", f"Message Count = {message_count}")
    return ResMessage(aiMessage=[ai_mock])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)


    # uvicorn main:app --reload
