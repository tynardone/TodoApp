from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .database import engine
from .models import Base
from .routers import admin, auth, todos, users

app = FastAPI()

# Runs only if database does not exist
Base.metadata.create_all(bind=engine)

# Frontend
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def test(request: Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)


@app.get("/healthy")
async def health_check():
    return {"status": "healthy"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
