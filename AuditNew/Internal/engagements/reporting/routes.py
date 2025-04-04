from utils import get_current_user
from schema import CurrentUser
from fastapi import APIRouter, Depends, Query, Path
from utils import  get_db_connection
from AuditNew.Internal.engagements.reporting.databases import *
from typing import List, Optional

router = APIRouter(prefix="/engagements")

@router.post("/reporting_procedures/{engagement_id}")
def create_new_reporting_procedure(
        engagement_id: int,
        report: NewReportingProcedure,
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        add_reporting_procedure(db, report=report, engagement_id=engagement_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/reporting_procedures/{engagement_id}", response_model=List[StandardTemplate])
def fetch_reporting_procedures(
        engagement_id: int,
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        data = get_reporting_procedures(db, column="engagement", value=engagement_id)
        return data
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.put("/reporting_procedures/{procedure_id}")
def update_reporting_procedure(
        procedure_id: int,
        report: StandardTemplate,
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        edit_reporting_procedure(db, report=report, procedure_id=procedure_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/summary_findings")
def fetch_company_summary_of_findings(
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        data = get_company_issues(connection=db, company_id=user.company_id)
        return data
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/summary_findings/engagement/{engagement_id}")
def fetch_engagement_summary_of_findings(
        engagement_id: int,
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        data = get_engagement_issues(connection=db, engagement_id=engagement_id)
        return data
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/summary_findings/audit_plan/{audit_plan_id}")
def fetch_audit_plan_summary_of_findings(
        audit_plan_id: int,
        db=Depends(get_db_connection),
        user: CurrentUser = Depends(get_current_user)
):
    if user.status_code != 200:
        raise HTTPException(status_code=user.status_code, detail=user.description)
    try:
        data = get_audit_plan_issues(connection=db, audit_plan_id=audit_plan_id)
        return data
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)



@router.get("/summary_audit_process/{engagement_id}")
def fetch_summary_of_audit_process():
    pass