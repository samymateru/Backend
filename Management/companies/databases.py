from psycopg.errors import ForeignKeyViolation, UniqueViolation
from Management.companies.schemas import *
from fastapi import HTTPException
from datetime import datetime
from psycopg import AsyncConnection, sql
from utils import get_unique_key

async def create_new_company(connection: AsyncConnection, company: NewCompany):
    query = sql.SQL(
        """
        INSERT INTO public.companies (id, name, owner, email, telephone, website, entity_type, status, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """)
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(query, (
                get_unique_key(),
                company.name,
                company.owner,
                company.email,
                company.telephone,
                company.website,
                company.entity_type,
                company.status,
                datetime.now()
            ))
            company_id = await cursor.fetchone()
        await connection.commit()
        return company_id[0]
    except UniqueViolation as e:
        await connection.rollback()
        raise HTTPException(status_code=409, detail="Company already already exist")
    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating new company {e}")

async def get_companies(connection: AsyncConnection, company_id: str):
    query = sql.SQL("""SELECT * FROM public.companies WHERE id = %s""")

    try:
        async with connection.cursor() as cursor:
            await cursor.execute(query, (company_id,))
            rows = await cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            data = [dict(zip(column_names, row_)) for row_ in rows]
            return data
    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail="Error querying companies")




# def get_companies_(connection: Connection, company_id: int) -> List[Dict]:
#     query = """SELECT * FROM public.companies WHERE id = %s"""
#
#
#     try:
#         with connection.cursor() as cursor:
#             cursor: Cursor
#             cursor.execute(query, (company_id,))
#             rows = cursor.fetchall()
#             column_names = [desc[0] for desc in cursor.description]
#             data = [dict(zip(column_names, row_)) for row_ in rows]
#             return data
#     except Exception as e:
#         connection.rollback()
#         print(f"Error querying companies {e}")
#         raise HTTPException(status_code=400, detail="Error querying companies")