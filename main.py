from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hey": "Renia"}

@app.get("/jobs/")
def read_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.Job).all()
    return jobs


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)

# uvicorn main:app --reload
