from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import case
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

@app.post("/message/")
def send_message(req_message: ReqMessage, db: Session = Depends(get_db)) -> ResMessage:
    job = db.query(models.Job).filter(models.Job.id == req_message.jobId).first()
    if not job:
        raise HTTPException(status_code=400, detail = "No job found")
    print(req_message)

    return ResMessage(aiMessage=["dupa"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)

# uvicorn main:app --reload
