from utils import get_current_user
from schema import CurrentUser
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from utils import  get_db_connection
from AuditNew.Internal.engagements.administration.schemas import *
from AuditNew.Internal.engagements.administration.databases import *
from schema import ResponseMessage

router = APIRouter(prefix="/engagements")

@router.get("/profile/{engagement_id}", response_model=List[EngagementProfile])
def fetch_engagement_profile(
        engagement_id: int,
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        data = get_engagement_profile(db, column="engagement", value=engagement_id)
        return data
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/context/policies/{engagement_id}", response_model=List[Policy])
def fetch_engagement_policies(
        engagement_id: int,
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        data = get_engagement_policies(db, column="engagement", value=engagement_id)
        return data
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/context/engagement_process/{engagement_id}", response_model=List[EngagementProcess])
def fetch_engagement_process(
        engagement_id: int,
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        data = get_engagement_process(db, column="engagement", value=engagement_id)
        return data
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/context/regulations/{engagement_id}", response_model=List[Regulations])
def fetch_regulations(
        engagement_id: int,
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        data = get_engagement_regulations(db, column="engagement", value=engagement_id)
        return data
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/staff/{engagement_id}", response_model=List[Staff])
def fetch_staff(
        engagement_id: int,
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        data = get_engagement_staff(db, column="engagement", value=engagement_id)
        return data
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.post("/profile/{engagement_id}", response_model=ResponseMessage)
def create_engagement_profile(
        engagement_id: int,
        profile: EngagementProfile,
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        delete_profile(db, engagement_id)
        add_engagement_profile(db, profile=profile, engagement_id=engagement_id)
        return {"detail": "Profile added successfully"}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.post("/context/policies/{engagement_id}", response_model=ResponseMessage)
def create_engagement_policy(
        engagement_id: int,
        name: str = Form(...),
        version: str = Form(...),
        key_areas: str = Form(...),
        attachment: UploadFile = File(...),
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    policy = Policy(
        name=name,
        version=version,
        key_areas=key_areas,
        attachment=attachment.filename
    )
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        add_engagement_policies(db, policy=policy, engagement_id=engagement_id)
        return {"detail": "Policy added successfully"}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.post("/context/engagement_process/{engagement_id}", response_model=ResponseMessage)
def create_engagement_process(
        engagement_id: int,
        process: EngagementProcess,
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        add_engagement_process(db, process=process, engagement_id=engagement_id)
        return {"detail": "Engagement process added successfully"}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.post("/context/regulations/{engagement_id}", response_model=ResponseMessage)
def create_engagement_regulations(
        engagement_id: int,
        name: str = Form(...),
        issue_date: datetime = Form(...),
        key_areas = Form(...),
        attachment: UploadFile = File(...),
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    regulation = Regulations(
        name = name,
        issue_date= issue_date,
        key_areas = key_areas,
        attachment = attachment.filename
    )
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        add_engagement_regulations(db, regulation=regulation, engagement_id=engagement_id)
        return {"detail": "Regulation added successfully"}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.post("/staff/{engagement_id}", response_model=ResponseMessage)
def create_engagement_staff(
        engagement_id: int,
        staff: Staff,
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        add_engagement_staff(db, staff=staff, engagement_id=engagement_id)
        return {"detail": "Staff added successfully"}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

