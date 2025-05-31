from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Todo API")

class TodoItem(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    completed: bool = False

todos = {}
counter = 0

@app.post("/todos/", response_model=TodoItem)
def create_todo(todo: TodoItem):
    global counter
    counter += 1
    todo.id = counter
    todos[counter] = todo
    return todo

@app.get("/todos/", response_model=List[TodoItem])
def read_todos(skip: int = 0, limit: int = 10):
    return list(todos.values())[skip: skip + limit]

@app.get("/todos/{todo_id}", response_model=TodoItem)
def read_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todos[todo_id]

@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, todo: TodoItem):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.id = todo_id
    todos[todo_id] = todo
    return todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    del todos[todo_id]
    return {"message": "Todo deleted successfully"}