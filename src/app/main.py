from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health_controller():
    return {"status": "Healthy"}
