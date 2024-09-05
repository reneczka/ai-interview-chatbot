from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models
from openai import OpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel
import ai

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
last_question = ""


@app.post("/message/")
def send_message(
    req_message: ReqMessage, db: Session = Depends(get_db)) -> ResMessage:
    global message_count, last_question

    job = db.query(
        models.Job).filter(models.Job.id == req_message.jobId).first()
    if not job:
        raise HTTPException(status_code=400, detail="No job found")

    if not req_message.userMessage:
        message_count = 1
        welcome_message = f"Welcome to the interview for the position of {job.job_name}. I'll be asking you some questions related to the job. Let's begin!"
        last_question = ai.generate_question()

        print("# # # # # # # # # # # #", f"Message Count = {message_count}")

        return ResMessage(aiMessage=[welcome_message, last_question])

    message_count += 1

    evaluation = ai.generate_answer_evaluation()

    if 1 < message_count < 10:
        next_question = ai.generate_question()
        last_question = next_question

        print("# # # # # # # # # # # #", f"Message Count = {message_count}")
        return ResMessage(aiMessage=[evaluation, next_question])

    if message_count == 10:
        final_evaluation = ai.generate_final_evaluation()
        bye_bye_message = "Thank you for participating in this interview. Best of luck in your job search!"

        print("# # # # # ## # # # #", f"Message Count = {message_count}")
        message_count = 0
        last_question = ""
        return ResMessage(
            aiMessage=[evaluation, final_evaluation, bye_bye_message])

    print("# # # # # # # # # # # #", f"Message Count = {message_count}")
    return ResMessage(aiMessage=[("this is a mock ai message")])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)


    # uvicorn main:app --reload
