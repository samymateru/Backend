from fastapi import FastAPI, Depends, Form
from AuditNew.Internal.annual_plans.routes import router as annual_plans_router
from Management.companies.routes import router as companies_router
from AuditNew.Internal.engagements.routes import router as engagements_router
from Management.roles.routes import router as roles_router
from Management.settings.business_process.routes import router as business_process_router
from Management.settings.risk_rating.routes import router as risk_rating_router
from Management.settings.engagement_types.routes import router as engagement_types_router
from AuditNew.Internal.engagements.administration.routes import router as administration_router
from Management.users.routes import router as users_router
from contextlib import asynccontextmanager
from utils import verify_password, get_db_connection, create_jwt_token
from Management.users.databases import get_user
from fastapi.middleware.cors import CORSMiddleware
from Management.companies.databases import  get_companies

from Management.templates.databases import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    from utils import connection_pool
    if connection_pool:
        print("Database connection pool initialized.")
    yield
    from utils import connection_pool
    connection_pool.closeall()
    print("Database connection pool closed")

app = FastAPI(lifespan=lifespan)
from seedings import *
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login", tags=["Authentication"])
def users(
          email: str = Form(...),
          password: str = Form(...),
          db: Connection = Depends(get_db_connection)):
    user_data: List[Dict] = get_user(db, column="email", value=email)
    if len(user_data) == 0:
        return HTTPException(status_code=405, detail="User doesn't exists")
    password_hash: bytes = user_data[0]["password_hash"].encode()
    if verify_password(password_hash, password):
        user: dict = {
            "user_id": user_data[0].get("id"),
            "company_id": user_data[0].get("company"),
            "type": user_data[0].get("type"),
            "status": user_data[0].get("status")
        }
        company = get_companies(db, column="id", value=user_data[0].get("company_id"))[0]
        token: str = create_jwt_token(user)
        user: dict = {
            "id": user_data[0].get("id"),
            "name": user_data[0].get("name"),
            "email": user_data[0].get("email"),
            "company_name": company.get("name"),
            "account_status": company.get("status")
        }
        return {"token": token, "token_type": "bearer", "status_code": 203, "detail": "login success", "content": user}
    else:
        return {"detail":"Invalid password", "status_code": 204}

app.include_router(companies_router, tags=["Company"])
app.include_router(users_router,tags=["User"])
app.include_router(annual_plans_router, tags=["Annual Audit Plans"])

# app.include_router(modules_router, tags=["Modules"])
app.include_router(roles_router, tags=["Roles"])
app.include_router(engagements_router, tags=["Engagements"])
app.include_router(business_process_router, tags=["Business Process"])
app.include_router(risk_rating_router, tags=["Risk Rating"])
app.include_router(engagement_types_router, tags=["Engagement Types"])
app.include_router(administration_router, tags=["Engagement Profile"])
# app.include_router(templates_router, tags=["Templates"])
# app.include_router(company_modules_router)
# app.include_router(audit_logs_router)
# app.include_router(engagement_profile_router)
# app.include_router(permission_router)
# app.include_router(features_router)
# app.include_router(feature_record_router)
# app.include_router(staff_assignment_router)
# app.include_router(planning_details_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
