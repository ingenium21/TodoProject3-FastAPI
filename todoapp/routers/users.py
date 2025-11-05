from fastapi import APIRouter, Depends, HTTPException, Path, status
from models import Todos, Users
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import get_current_user, authenticate_user, bcrypt_context

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


def get_db():
    """Dependency to get DB session, opens and closes it properly."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def read_user(user: user_dependency, db: db_dependency):
    """
    Read the current logged-in user details from the database.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed or not authorized.")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return user_model

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(user: user_dependency, db: db_dependency, new_password: str, current_password: str):
    """
    Change your password.
    """
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found.")
    #check the old password
    authenticated_user = authenticate_user(user_model.username, current_password, db)
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Current password is incorrect.")
    else:
        hashed_new_password = bcrypt_context.hash(new_password)
        user_model.hashed_password = hashed_new_password
        db.add(user_model)
        db.commit()
    return {"detail": "Password updated successfully."}
