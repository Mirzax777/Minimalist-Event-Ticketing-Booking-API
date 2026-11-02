from fastapi import FastAPI

app = FastAPI(title="Ticket API")


@app.get("/")
def root():
    return {"message": "Ticket API is Running"}
