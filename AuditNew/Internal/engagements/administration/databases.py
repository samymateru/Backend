import json
from fastapi import HTTPException
from psycopg2.extensions import connection as Connection
from AuditNew.Internal.engagements.administration.schemas import *
from psycopg2.extensions import cursor as Cursor


def edit_engagement_profile(connection: Connection, profile: EngagementProfile, engagement_id: int):
    query: str = """
                   UPDATE public.profile
                    SET 
                        audit_background = %s::jsonb,
                        audit_objectives = %s::jsonb,
                        key_legislations = %s::jsonb ,
                        relevant_systems = %s::jsonb,
                        key_changes = %s::jsonb,
                        reliance = %s::jsonb,
                        scope_exclusion = %s::jsonb,
                        core_risk = %s,
                        estimated_dates = %s::jsonb
                        WHERE engagement = %s;
                 """
    try:
        values = (
            profile.audit_background.model_dump_json(),
            profile.audit_objectives.model_dump_json(),
            profile.key_legislations.model_dump_json(),
            profile.relevant_systems.model_dump_json(),
            profile.key_changes.model_dump_json(),
            profile.reliance.model_dump_json(),
            profile.scope_exclusion.model_dump_json(),
            profile.core_risk,
            profile.estimated_dates.model_dump_json(),
            engagement_id
        )
        with connection.cursor() as cursor:
            cursor.execute(query, values)
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating engagement profile {e}")

def add_engagement_policies(connection: Connection, policy: Policy, engagement_id: int):
    query: str = """
                   INSERT INTO public.policies (
                        engagement,
                        name,
                        version,
                        key_areas,
                        attachment
                   ) VALUES(%s, %s, %s, %s, %s)
                 """
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (
                engagement_id,
                policy.name,
                policy.version,
                policy.key_areas,
                policy.attachment
            ))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error adding engagement policy {e}")

def add_new_business_contact(connection: Connection, engagement_id: int):
    query: str = """
                   INSERT INTO public.business_contact (
                        engagement,
                        "user",
                        type
                   ) VALUES(%s, %s::jsonb, %s)
                 """
    try:

        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (
                engagement_id,
                json.dumps([]),
                "action"
            ))
            cursor.execute(query, (
                engagement_id,
                json.dumps([]),
                "info"
            ))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error adding business contact {e}")

def add_engagement_process(connection: Connection, process: EngagementProcess, engagement_id: int):
    query: str = """
                   INSERT INTO public.engagement_process (
                        engagement,
                        process,
                        sub_process,
                        description,
                        business_unit
                   ) VALUES(%s, %s, %s, %s, %s)
                 """
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (
                engagement_id,
                process.process,
                process.sub_process,
                process.description,
                process.business_unit
            ))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error adding engagement process {e}")

def add_engagement_regulations(connection: Connection, regulation: Regulations, engagement_id: int):
    query: str = """
                   INSERT INTO public.regulations (
                        engagement,
                        name,
                        issue_date,
                        key_areas,
                        attachment
                   ) VALUES(%s, %s, %s, %s, %s)
                 """
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (
                engagement_id,
                regulation.name,
                regulation.issue_date,
                regulation.key_areas,
                regulation.attachment
            ))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error adding engagement regulation {e}")

def add_engagement_staff(connection: Connection, staff: Staff, engagement_id: int):
    query: str = """
                   INSERT INTO public.staff (
                        engagement,
                        name,
                        role,
                        start_date,
                        end_date,
                        tasks
                   ) VALUES(%s, %s, %s, %s, %s, %s)
                 """
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (
                engagement_id,
                staff.name,
                staff.role.model_dump_json(),
                staff.start_date,
                staff.end_date,
                staff.tasks
            ))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error adding engagement staff {e}")

def get_engagement_profile(connection: Connection, column: str = None, value: int | str = None):
    query: str = """
                    SELECT * from public.profile 
                 """
    if column and value:
        query += f"WHERE  {column} = %s"
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (value,))
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row_)) for row_ in rows]
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error fetching engagement profile {e}")


def get_business_contacts(connection: Connection, column: str = None, value: int | str = None):
    query: str = """
                    SELECT * from public.business_contact 
                 """
    if column and value:
        query += f"WHERE  {column} = %s"
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (value,))
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row_)) for row_ in rows]
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error fetching business contacts {e}")

def get_engagement_policies(connection: Connection, column: str = None, value: int | str = None):
    query: str = """
                    SELECT * from public.policies
                 """
    if column and value:
        query += f"WHERE  {column} = %s"
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (value,))
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row_)) for row_ in rows]
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error fetching engagement policies {e}")

def get_engagement_process(connection: Connection, column: str = None, value: int | str = None):
    query: str = """
                    SELECT * from public.engagement_process
                 """
    if column and value:
        query += f"WHERE  {column} = %s"
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (value,))
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row_)) for row_ in rows]
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error fetching engagement processes {e}")

def get_engagement_regulations(connection: Connection, column: str = None, value: int | str = None):
    query: str = """
                    SELECT * from public.regulations
                 """
    if column and value:
        query += f"WHERE  {column} = %s"
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (value,))
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row_)) for row_ in rows]
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error fetching engagement regulations {e}")


def get_engagement_staff(connection: Connection, column: str = None, value: int | str = None):
    query: str = """
                    SELECT * from public.staff
                 """
    if column and value:
        query += f"WHERE  {column} = %s"
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (value,))
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row_)) for row_ in rows]
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error fetching engagement staffing {e}")


def remove_profile(connection: Connection, profile_id: int):
    query: str = """
                    DELETE FROM public.profile WHERE id = %s
                 """
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (profile_id,))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting engagement profile {e}")


def remove_policy(connection: Connection, policy_id: int):
    query: str = "DELETE FROM public.policies WHERE id = %s"
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (policy_id,))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error removing policy {e}")

def remove_engagement_process(connection: Connection, engagement_process_id: int):
    query: str = "DELETE FROM public.engagement_process WHERE id = %s"
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (engagement_process_id,))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error removing engagement process {e}")


def remove_staff(connection: Connection, staff_id: int):
    query: str = "DELETE FROM public.staff WHERE id = %s"
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (staff_id,))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error removing staff {e}")

def remove_regulation(connection: Connection, regulation_id: int):
    query: str = "DELETE FROM public.regulations WHERE id = %s"
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (regulation_id,))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error removing regulation {e}")

def edit_business_contact(connection: Connection, business_contacts: List[BusinessContact], engagement_id: int):
    query: str = """
                  UPDATE public.business_contact
                  SET 
                  "user" = %s::jsonb
                  WHERE engagement = %s AND type = %s
                 """
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            for business_contact in business_contacts:
                cursor.execute(query, (
                    json.dumps(business_contact.model_dump().get("user")),
                    engagement_id,
                    business_contact.type
                    ))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating business contact {e}")

def edit_engagement_process(connection: Connection, engagement_process: EngagementProcess, engagement_process_id: int):
    query: str = """
                  UPDATE public.engagement_process
                  SET 
                  process = %s,
                  sub_process = %s,
                  description = %s,
                  business_unit = %s
                  WHERE id = %s
                 """
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (
                engagement_process.process,
                engagement_process.sub_process,
                engagement_process.description,
                engagement_process.business_unit,
                engagement_process_id
                ))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating engagement process {e}")

def edit_regulations(connection: Connection, regulation: Regulations, regulation_id: int):
    query: str = """
                  UPDATE public.regulations
                  SET 
                  name = %s,
                  issue_date = %s,
                  key_areas = %s,
                  attachment = %s
                  WHERE id = %s
                 """
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (
                regulation.name,
                regulation.issue_date,
                regulation.key_areas,
                regulation.attachment,
                regulation_id
                ))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating regulation {e}")

def edit_policies(connection: Connection, policy: Policy, policy_id: int):
    query: str = """
                  UPDATE public.policies
                  SET 
                  name = %s,
                  version = %s,
                  key_areas = %s,
                  attachment = %s
                  WHERE id = %s
                 """
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (
                policy.name,
                policy.version,
                policy.key_areas,
                policy.attachment,
                policy_id
                ))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating policy {e}")

def edit_staff(connection: Connection, staff: Staff, staff_id: int):
    query: str = """
                  UPDATE public.staff
                  SET 
                  name = %s,
                  role = %s::jsonb,
                  start_date = %s,
                  end_date = %s,
                  tasks = %s
                  WHERE id = %s
                 """
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (
                staff.name,
                staff.role,
                staff.start_date,
                staff.end_date,
                staff.tasks,
                staff_id
                ))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating staffing {e}")