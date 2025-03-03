from fastapi import HTTPException
from psycopg2.extensions import connection as Connection
from AuditNew.Internal.engagements.reporting.schemas import *
from AuditNew.Internal.engagements.planning.schemas import StandardTemplate
from psycopg2.extensions import cursor as Cursor

def safe_json_dump(obj):
    return obj.model_dump_json() if obj is not None else '{}'

def add_reporting_procedure(connection: Connection, report: StandardTemplate, engagement_id: int):

    query: str = """
                   INSERT INTO public.reporting_procedure (
                        engagement,
                        title,
                        tests,
                        results,
                        observation,
                        attachments,
                        conclusion,
                        type,
                        prepared_by,
                        reviewed_by
                   ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                 """
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (
                engagement_id,
                report.title,
                safe_json_dump(report.tests),
                safe_json_dump(report.results),
                safe_json_dump(report.observation),
                report.attachments,
                safe_json_dump(report.conclusion),
                report.type,
                safe_json_dump(report.prepared_by),
                safe_json_dump(report.reviewed_by)
            ))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error adding reporting procedures {e}")

def get_reporting_procedures(connection: Connection, column: str = None, value: int | str = None):
    query: str = """
                   SELECT * from public.reporting_procedure
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
        raise HTTPException(status_code=400, detail=f"Error fetching reporting procedures {e}")

def edit_reporting_procedure(connection: Connection, report: StandardTemplate, procedure_id: int):
    query: str = """
                    UPDATE public.reporting_procedure
                    SET 
                    title = %s,
                    tests = %s::jsonb,
                    results = %s::jsonb,
                    observation = %s::jsonb,
                    attachments = %s,
                    conclusion = %s::jsonb,
                    prepared_by = %s::jsonb,
                    reviewed_by = %s::jsonb  WHERE id = %s; 
                   """
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (
                report.title,
                safe_json_dump(report.tests),
                safe_json_dump(report.results),
                safe_json_dump(report.observation),
                report.attachments,
                safe_json_dump(report.conclusion),
                safe_json_dump(report.prepared_by),
                safe_json_dump(report.reviewed_by),
                procedure_id
            ))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating reporting procedure {e}")