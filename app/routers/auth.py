from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from ..database import SessionLocal
from ..models import Users

# These work together to add a signature to the JWT
SECRET_KEY: str = "2e9130e14cfb4b057709970f09765e432dff09d8b667b2e31f9cc35aa3c7dda8"
ALGORITHM = "HS256"

router: APIRouter = APIRouter(prefix="/auth", tags=["auth"])
bcrypt_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    phone_number: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        user_id: int | None = payload.get("id")
        user_role: str | None = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user.",
            )
        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate user.")


db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="app/templates")


### Pages ###
@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", context={"request": request})


@router.get("/register-page")
def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", context={"request": request})


### Endpoints ###
def authenticate_user(username: str, password: str, db: Session):
    user: Users | None = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
) -> str:
    encode: dict = {"sub": username, "id": user_id, "role": role}
    expires: datetime = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        phone_number=create_user_request.phone_number,
        is_active=True,
    )

    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
):
    """Authenticate user with OAuth2 form. If successfuly authenticated return a JWT."""
    user = authenticate_user(form_data.username, form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user.",
        )
    token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=20),
    )
    return Token(access_token=token, token_type="bearer")
