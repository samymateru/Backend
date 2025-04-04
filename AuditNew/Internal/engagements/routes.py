from fastapi import APIRouter, Depends, HTTPException

from AuditNew.Internal.engagements.administration.databases import add_new_business_contact
from utils import  get_db_connection
from AuditNew.Internal.engagements import databases
from AuditNew.Internal.engagements.schemas import *
from typing import Dict, List
from utils import get_current_user
from schema import CurrentUser
from seedings import planning_procedures, finalization_procedures, reporting_procedures, add_engagement_profile


router = APIRouter(prefix="/engagements")

@router.get("/{annual_id}")
def get_engagements(
        annual_id: str,
        db = Depends(get_db_connection),
        user: CurrentUser  = Depends(get_current_user)
):
    if user.status_code != 200:
        return HTTPException(status_code=user.status_code, detail=user.description)
    try:
        engagement_data: List[Dict] = databases.get_engagements(db, column="plan_id", value=annual_id)
        if engagement_data.__len__() == 0:
            return {"payload": [], "status_code": 200}
        return {"payload": engagement_data, "status_code":200}
    except HTTPException as e:
        return HTTPException(status_code=e.status_code, detail=e.detail)

@router.post("/new_engagement/{annual_id}")
def create_new_engagement(
        annual_id: int,
        engagement: NewEngagement,
        db = Depends(get_db_connection),
        user: CurrentUser  = Depends(get_current_user)
    ):
    eng: str | int = databases.get_engagement_code(db, str(annual_id))
    if user.status_code != 200:
        return HTTPException(status_code=user.status_code, detail=user.description)
    max_ = 0
    try:
        for data in eng:
            if engagement.department.code == data[0].split("-")[0]:
                if int(data[0].split("-")[1]) >= max_:
                    max_ = int(data[0].split("-")[1])
        code: str = engagement.department.code + "-" + str(max_ + 1).zfill(3) + "-" + str(datetime.now().year)
        id = databases.create_new_engagement(db, engagement, str(annual_id), code=code)
        planning_procedures(connection=db, engagement=id)
        finalization_procedures(connection=db, engagement=id)
        reporting_procedures(connection=db, engagement=id)
        add_engagement_profile(connection=db, engagement=id)
        add_new_business_contact(connection=db, engagement_id=id)
        return {"detail": "engagement successfully created", "status_code": 501}
    except HTTPException as e:
        return HTTPException(status_code=e.status_code, detail=e.detail)

@router.put("/update_engagement")
def update_engagement(
        user_update: UpdateEngagement,
        db = Depends(get_db_connection),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    if current_user.status_code != 200:
        return HTTPException(status_code=current_user.status_code, detail=current_user.description)
    try:
        databases.update_engagement(db, user_update)
        return {"message": "engagement successfully updated", "code": 502}
    except HTTPException as e:
        return HTTPException(status_code=e.status_code, detail=e.detail)

@router.delete("/{engagement_id}")
def delete_engagement(
        engagement_id: int,
        db = Depends(get_db_connection),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    if current_user.status_code != 200:
        return HTTPException(status_code=current_user.status_code, detail=current_user.description)
    try:
        databases.delete_engagements(db, engagement_id=engagement_id)
        return {"message": "successfully delete the engagement", "code": 503}
    except HTTPException as e:
        return HTTPException(status_code=e.status_code, detail=e.detail)
