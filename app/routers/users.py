from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from ..database import get_db
from ..models import Users

SECRET_KEY: str = "2e9130e14cfb4b057709970f09765e432dff09d8b667b2e31f9cc35aa3c7dda8"
ALGORITHM = "HS256"

router: APIRouter = APIRouter(prefix="/user", tags=["user"])
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


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


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.put("/password/", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency, db: db_dependency, user_verification: UserVerification
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not Authorized")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if isinstance(user_model, Users):
        if not bcrypt_context.verify(
            user_verification.password, user_model.hashed_password
        ):
            raise HTTPException(status_code=401, detail="Error on password change")

        user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
        db.add(user_model)
        db.commit()
    else:
        raise HTTPException(status_code=401, detail="Not Authorized")


@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(
    user: user_dependency, db: db_dependency, phone_number: str
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not Authorized")

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if isinstance(user_model, Users):
        user_model.phone_number = phone_number
        db.add(user_model)
        db.commit()
    else:
        raise HTTPException(status_code=401, detail="Not Authorized")
