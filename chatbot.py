from fastapi import FastAPI

app = FastAPI()

@app.get("/renia")
async def get_renia():
    return {"message": "renia"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)