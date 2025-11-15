from fastapi import FastAPI, HTTPException, status
from .models import Base
from .database import engine 
from .routers import auth, todos, admin, users


app = FastAPI()

Base.metadata.create_all(bind=engine) #this will create everything from database.py and models.py in the database

@app.get("/healthy")
def health_check():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)