from fastapi import FastAPI

app = FastAPI(
    title="High-Concurrency Inventory System",
    description="FastAPI backend using Redis atomic inventory reservation and PostgreSQL persistence.",
    version="1.0.0",
)

@app.get("/")
def root():
    return {"message": "High-Concurrency Inventory System API is running"}