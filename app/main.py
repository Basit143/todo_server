from fastapi import FastAPI,Depends
from typing import Annotated
from sqlmodel import SQLModel, Field,create_engine, Session ,select
from contextlib import asynccontextmanager
from app import setting

#Step:1 Database Table Schema
class  Todo(SQLModel, table=True):
    id:int | None = Field(default=None, primary_key=True)
    title:str


#Connection to the Database 
connection_string: str = str(setting.DATABASE_URL).replace(
    "postgresql","postgresql+psycopg"
)

engine = create_engine(connection_string, echo=True)


def create_db_tables():
    print("create_db_tables")
    SQLModel.metadata.create_all(engine)
    print("Done")

@asynccontextmanager
async def lifespan(todo_server: FastAPI):
    print("server startup")
    create_db_tables()
    yield

#Table Data Save and Get

todo_server: FastAPI = FastAPI(lifespan=lifespan)

# @todo_server.get("/")
# def hello():
#     return {"Hello": "World"}


@todo_server.get("/db")
def db ():
    return {"DB": setting.DATABASE_URL , "Connection": connection_string}
    
def get_session():
    with Session(engine) as session:
        yield session

@todo_server.get("/")
def hello_world():
     return {"Greet": "Hello World!"}

@todo_server.post("/todo")
def create_todo(todo_data: Todo, session: Annotated[Session,Depends(get_session)]):
    # with Session(engine) as session: 
        session.add(todo_data)
        session.commit()
        session.refresh(todo_data)
        return todo_data


# Get All Todos Data 

@todo_server.get("/todo")
def get_all_todos(new_concept: Annotated[Session,Depends(get_session)]):
    # with Session(engine) as session:
    # session = Session(engine)
      query = select(Todo)
      all_todos = new_concept.exec(query).all()
      return all_todos

# Put method  for updating the data in database using id of the

@todo_server.put("/todo/{todo_id}")
def update_todo(todo_id: int, todo_data: Todo, session: Annotated[Session, Depends(get_session)]):
    existing_todo = session.get(Todo, todo_id)
    if existing_todo:
        existing_todo.title = todo_data.title
        session.add(existing_todo)
        session.commit()
        session.refresh(existing_todo)
        return existing_todo
    else:
        return {"error": "Todo item not found"}

# delete method 

@todo_server.delete("/todo/{todo_id}")
def delete_todo(todo_id: int, session: Annotated[Session, Depends(get_session)]):
    todo = session.get(Todo, todo_id)
    if todo:
        session.delete(todo)
        session.commit()
        return {"message": f"Todo item with id {todo_id} deleted successfully"}
    else:
        return {"error": "Todo item not found"}




