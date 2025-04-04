from fastapi import APIRouter, Depends, HTTPException
from AuditNew.Internal.engagements.databases import update_engagement
from utils import  get_db_connection
from Management.users.databases import *
from Management.users.schemas import *
from utils import get_current_user
from schema import CurrentUser, ResponseMessage
from Management.roles.databases import *


router = APIRouter(prefix="/users")

@router.get("/", response_model=List[User])
def fetch_users(
        db = Depends(get_db_connection),
        user: CurrentUser  = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        data = get_user(db, column="company", value=user.company_id)
        return data
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/profile", response_model=User)
def fetch_user(
        db = Depends(get_db_connection),
        user: CurrentUser  = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        data = get_user(db, column="id", value=user.user_id)[0]
        return data
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.post("/", response_model=ResponseMessage)
def create_new_user(
        user_data: NewUser,
        db = Depends(get_db_connection),
        user: CurrentUser  = Depends(get_current_user)
    ):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        new_user(connection=db, user_data=user_data,  company_id=user.company_id)
        return {"detail": "User successfully created"}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put("/")
def update_user(
        user_update: UpdateUser,
        db = Depends(get_db_connection),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    if current_user.status_code != 200:
        return HTTPException(status_code=current_user.status_code, detail=current_user.description)
    if current_user.type != "admin":
        return HTTPException(status_code=101, detail="your not admin")
    try:
        update_user(db, user_update)
        return {"detail": "user successfully updated", "status_code": 502}
    except HTTPException as e:
        return HTTPException(status_code=e.status_code, detail=e.detail)

@router.delete("/{user_id}")
def delete_user(
        user_id: int,
        db = Depends(get_db_connection),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    if current_user.status_code != 200:
        return HTTPException(status_code=current_user.status_code, detail=current_user.description)
    if current_user.type != "admin":
        return HTTPException(status_code=101, detail="your not admin")
    try:
        pass
    except HTTPException as e:
        return HTTPException(status_code=e.status_code, detail=e.detail)



