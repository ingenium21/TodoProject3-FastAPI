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

class UserVerification(BaseModel):
    password: str
    new_password: str


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

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    """
    Change your password.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed or not authorized.")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found.")
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=403, detail="Current password is incorrect.")
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
    
@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def update_phone_number(
    user: user_dependency,
    db: db_dependency,
    phone_number: str
):
    """updates the phone number"""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed or not authorized.")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()
    