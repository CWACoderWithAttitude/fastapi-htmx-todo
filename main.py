from typing import Annotated, Union
import logging

from fastapi import Depends, FastAPI, Request, Form, Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uuid import uuid4
from models import Todo
from schemas import TodoSchema
from database import engine, SessionLocal, Base
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
logger.info("FastAPI application initialized")

todos = []


def get_db():
    """
    Create and manage database session lifecycle.

    Yields:
        Session: SQLAlchemy database session.
    """
    try:
        db = SessionLocal()
        logger.debug("Database session created")
        yield db
    finally:
        db.close()
        logger.debug("Database session closed")


def create_todo_in_db(db: Session, todo_text: str) -> Todo:
    """
    Create a new todo item in the database.

    Args:
        db (Session): The database session to use.
        todo_text (str): The text content of the todo item.

    Returns:
        Todo: The newly created todo object with assigned ID.
    """
    new_todo = Todo(todo=todo_text)
    logger.debug(f"Creating todo object with text: '{todo_text}'")

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    logger.info(f"New todo created with ID: {new_todo.id}")
    return new_todo


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    logger.info("Index page requested")
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/todos", response_class=HTMLResponse)
async def list_todos(request: Request, db: Session = Depends(get_db), hx_request: Annotated[Union[str, None], Header()] = None):
    logger.info(f"&&& List todos requested (HTMX: {bool(hx_request)})")
    todos = db.query(Todo).all()
    if hx_request:
        logger.debug(f"Returning {len(todos)} todos via HTMX")
        return templates.TemplateResponse(
            request=request, name="todos.html", context={"todos": todos}
        )

    logger.debug(f"Returning {len(todos)} todos as JSON")
    return JSONResponse(content=jsonable_encoder(todos))


@app.post("/todos", response_class=HTMLResponse)
async def create_todo(request: Request, todo: Annotated[str, Form()], db: Session = Depends(get_db)):
    """
    Handle POST request to create a new todo item.

    Args:
        request (Request): The incoming HTTP request.
        todo (str): The todo text from the form submission.
        db (Session): Database session dependency.

    Returns:
        HTMLResponse: Rendered template with updated todos list.
    """
    logger.info(f"Received request to create todo: '{todo}'")

    # Create the todo in the database using dedicated method
    new_todo = create_todo_in_db(db, todo)

    # Debug: Print all properties of the newly created todo
    print(
        f"new_todo properties: id={new_todo.id}, todo={new_todo.todo}, done={new_todo.done}")

    return templates.TemplateResponse(
        request=request, name="todos.html", context={"todos": todos}
    )


@app.put("/todos/{todo_id}", response_class=HTMLResponse)
async def update_todo(request: Request, todo_id: str, text: Annotated[str, Form()]):
    logger.info(f"Updating todo {todo_id} with text: '{text}'")
    found = False
    for index, todo in enumerate(todos):
        if str(todo.id) == todo_id:
            old_text = todo.text
            todo.text = text
            logger.info(f"Todo {todo_id} updated: '{old_text}' -> '{text}'")
            found = True
            break

    if not found:
        logger.warning(f"Todo {todo_id} not found for update")

    return templates.TemplateResponse(
        request=request, name="todos.html", context={"todos": todos}
    )


@app.post("/todos/{todo_id}/toggle", response_class=HTMLResponse)
async def toggle_todo(request: Request, todo_id: str):
    logger.info(f"Toggling todo {todo_id}")
    found = False
    for index, todo in enumerate(todos):
        if str(todo.id) == todo_id:
            todos[index].done = not todos[index].done
            logger.info(
                f"Todo {todo_id} toggled to {'done' if todos[index].done else 'not done'}")
            found = True
            break

    if not found:
        logger.warning(f"Todo {todo_id} not found for toggle")

    return templates.TemplateResponse(
        request=request, name="todos.html", context={"todos": todos}
    )


@app.post("/todos/{todo_id}/delete", response_class=HTMLResponse)
async def delete_todo(request: Request, todo_id: str):
    logger.info(f"Deleting todo {todo_id}")
    found = False
    for index, todo in enumerate(todos):
        if str(todo.id) == todo_id:
            deleted_text = todo.text
            del todos[index]
            logger.info(
                f"Todo {todo_id} deleted: '{deleted_text}'. Remaining todos: {len(todos)}")
            found = True
            break

    if not found:
        logger.warning(f"Todo {todo_id} not found for deletion")

    return templates.TemplateResponse(
        request=request, name="todos.html", context={"todos": todos}
    )
