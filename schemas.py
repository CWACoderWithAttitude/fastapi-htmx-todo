# schemas.py
from pydantic import BaseModel
class TodoSchema(BaseModel):
    id: int
    todo: str
    done: bool

    class Config:
        #orm_mode = True
        from_attributes = True