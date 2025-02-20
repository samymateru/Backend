from fastapi import APIRouter, Depends, HTTPException, Query
from utils import get_db_connection
from Management.companies.schemas import *
from typing import Tuple, List, Dict
from Management.companies import databases as company_database
from Management.users import databases as user_database
from schema import CurrentUser
from utils import generate_hash_password, get_current_user
from Management.companies import databases
from Management.users.schemas import *

router = APIRouter(prefix="/companies")

@router.post("/new_company")
def new_company(
        new_company_data: NewCompany,
        db = Depends(get_db_connection)
    ):
    try:
        company_id: int = company_database.create_new_company(db, new_company_data)
        user_data = NewUser(
            name = new_company_data.owner,
            telephone = new_company_data.telephone,
            email = new_company_data.email,
            type = "owner",
            password = new_company_data.password,
            module_id=new_company_data.module_id,
            status = True,
        )
        user_database.create_new_user(db, user_data, company_id)
        return {"detail": "company successfully created", "status_code":201}
    except HTTPException as e:
        return HTTPException(status_code=e.status_code, detail=e.detail)


@router.put("/update_company")
def update_company(
        update_company_data: UpdateCompany,
        db = Depends(get_db_connection)
):
    pass


@router.get("/")
def get_company(
        db = Depends(get_db_connection),
        current_user: CurrentUser  = Depends(get_current_user)
    ):
    if current_user.status_code != 200:
        return HTTPException(status_code=current_user.status_code, detail=current_user.description)
    try:
        company_data: List[Dict] = databases.get_companies(db, column="id", value=current_user.company_id)
        if company_data.__len__() == 0:
            return {"payload": [], "status_code": 200}
        return {"payload": company_data[0], "status_code": 200}
    except HTTPException as e:
        return HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/resource")
def get_resource(
        db = Depends(get_db_connection),
        current_user: CurrentUser  = Depends(get_current_user),
        resource: ResourceTypes = Query()
    ):
    if current_user.status_code != 200:
        return HTTPException(status_code=current_user.status_code, detail=current_user.description)
    try:
        resource_data = databases.get_resource(db, resource.value, column="company", value=current_user.company_id)
        if resource_data.__len__() == 0:
            return {"payload": [], "status_code": 200}
        return {"payload": resource_data, "status_code": 200}
    except HTTPException as e:
        return HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/sub_resource")
def get_sub_resource(
        db = Depends(get_db_connection),
        #current_user: CurrentUser  = Depends(get_current_user),
        resource: SubResourceTypes = Query()
    ):
    # if current_user.status_code != 200:
    #     return HTTPException(status_code=current_user.status_code, detail=current_user.description)
    try:
        resource_data = databases.get_resource(db, resource.value, column="company", value="3")
        if resource_data.__len__() == 0:
            return {"payload": [], "status_code": 200}
        return {"payload": resource_data, "status_code": 200}
    except HTTPException as e:
        return HTTPException(status_code=e.status_code, detail=e.detail)

@router.post("/business_process")
def add_business_process(
        business_process: BusinessProcess,
        db = Depends(get_db_connection),
        current_user: CurrentUser  = Depends(get_current_user),
    ):
    if current_user.status_code != 200:
        return HTTPException(status_code=current_user.status_code, detail=current_user.description)
    try:
        databases.add_business_process(db, business_process, str(current_user.company_id))
        return {"detail": "Business process added successfully", "status_code": 501}
    except HTTPException as e:
        return HTTPException(status_code=e.status_code, detail=e.detail)

@router.post("/business_sub_process/{business_process_id}")
def add_business_sub_process(
        business_process_id: str,
        business_sub_process: BusinessSubProcess,
        db = Depends(get_db_connection),
        current_user: CurrentUser  = Depends(get_current_user),

    ):
    if current_user.status_code != 200:
        return HTTPException(status_code=current_user.status_code, detail=current_user.description)
    try:
        databases.add_business_sub_process(db, business_sub_process, business_process_id)
        return {"detail": "Business sub process added successfully", "status_code": 501}
    except HTTPException as e:
        return HTTPException(status_code=e.status_code, detail=e.detail)
