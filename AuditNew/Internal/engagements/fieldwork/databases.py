from typing import Dict, List
from fastapi import HTTPException
from psycopg2.extensions import connection as Connection
from psycopg2.extensions import cursor as Cursor
from AuditNew.Internal.engagements.schemas import UpdateEngagement, NewEngagement
import json

def get_summary_procedures(connection: Connection, engagement_id: int):
    query: str = f""" 
                    SELECT
                    main_program.name as program, 
                    sub_program.reference,
                    sub_program.title,
                    sub_program.prepared_by,
                    sub_program.reviewed_by,
                    sub_program.effectiveness,
                    COUNT(issue.id) AS issue_count 
                    FROM main_program 
                    LEFT JOIN sub_program ON main_program.id = sub_program.program
                    LEFT JOIN issue ON sub_program.id = issue.sub_program
                    WHERE main_program.engagement = %s
                    GROUP BY sub_program.reference, sub_program.title, sub_program.prepared_by, 
                    sub_program.reviewed_by, sub_program.effectiveness, main_program.name;                
                 """
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (engagement_id,))
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row_)) for row_ in rows]
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error fetching summary of procedures {e}")

def get_summary_review_notes(connection: Connection, engagement_id: int):
    query: str = f"""
                    SELECT 
                    review_comment.reference,
                    review_comment.title,
                    review_comment.description,
                    review_comment.raised_by,
                    review_comment.action_owner,
                    review_comment.resolution_summary,
                    review_comment.resolution_details,
                    review_comment.resolved_by,
                    review_comment.decision
                    FROM review_comment 
                    WHERE engagement = %s;
                 """
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (engagement_id,))
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row_)) for row_ in rows]
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error fetching summary of review notes {e}")

def get_summary_task(connection: Connection, engagement_id: int):
    query: str = f"""
                    SELECT 
                    task.reference,
                    task.title,
                    task.description,
                    task.raised_by,
                    task.action_owner,
                    task.resolution_summary,
                    task.resolution_details,
                    task.resolved_by,
                    task.decision
                    FROM task 
                    WHERE engagement = %s;
                 """
    try:
        with connection.cursor() as cursor:
            cursor: Cursor
            cursor.execute(query, (engagement_id,))
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row_)) for row_ in rows]
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error fetching summary of task {e}")
