from fastapi import FastAPI

app = FastAPI(title="Study Group Finder")


@app.get("/health")
def health():
    return {"status": "ok"}
