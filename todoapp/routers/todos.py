from fastapi import APIRouter, Depends, HTTPException, Path, status, Request
from ..models import Todos
from ..database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="todoapp/templates")

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
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

class TodoRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=300)
    priority: int = Field(ge=1, le=5)
    complete: bool = Field(default=False)

def redirect_to_login():
    response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    return response



## Pages ###
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if user is None:
            return redirect_to_login()
        
        todos = db.query(Todos).filter(Todos.owner_id == user["id"]).all()
        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})
    except:
        return redirect_to_login()
    
@router.get("/add-todo-page")
async def render_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if user is None:
            return redirect_to_login()
        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})
    except:
        return redirect_to_login()
    
@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if user is None:
            return redirect_to_login()
        
        todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()

        if todo_model is None:
            return redirect_to_login()
        
        return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo_model, "user": user})
    except:
        return redirect_to_login()

### Endpoints ###
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency,db: db_dependency):
    """
    Read all todo records from the database.
    Parameters:
    * db: The database session.
    * Depends is dependency injection system of FastAPI.
    Here we are injecting the database session into the path operation function.
    This function will read all todo records from the database and return them.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed.")
    return db.query(Todos).filter(Todos.owner_id == user["id"]).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    """
    This function will read a specific todo record by its ID from the database and return it.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed.")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()

    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail=f"Todo with the id {todo_id} not found")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    """
        This function will create a new todo record in the database.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed.")

    todo_model = Todos(**todo_request.model_dump(), owner_id=user["id"])  # unpacking the fields from the Pydantic model to the SQLAlchemy model
    db.add(todo_model)
    db.commit()

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
        user: user_dependency,
        db: db_dependency,
        todo_request: TodoRequest,
        todo_id: int = Path(gt=0)):
    """
    This function will update an existing todo record in the database.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed.")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail=f"Todo with the id {todo_id} not found")
    
    # use setattr to update attributes
    setattr(todo_model, 'title', todo_request.title)
    setattr(todo_model, 'description', todo_request.description)
    setattr(todo_model, 'priority', todo_request.priority)
    setattr(todo_model, 'complete', todo_request.complete)

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,db: db_dependency, todo_id: int = Path(gt=0)):
    """
    This function will delete a todo record from the database.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed.")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail=f"Todo with the id {todo_id} not found")

    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).delete()
    db.commit()