import json
from fastapi import HTTPException
from psycopg2.extensions import connection as Connection
from psycopg2.extensions import cursor as Cursor
from AuditNew.Internal.engagements.review_comment.schemas import *
from utils import get_reference, get_unique_key
from psycopg import AsyncConnection, sql
from psycopg.errors import ForeignKeyViolation, UniqueViolation


async def remove_review_comment(connection: AsyncConnection, review_comment_id: str):
    query = sql.SQL("DELETE FROM public.review_comment WHERE id = %s")
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(query,(review_comment_id,))
        await connection.commit()
    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting review comment {e}")

async def raise_review_comment_(connection: AsyncConnection, review_comment: NewReviewComment, engagement_id: str):
    query = sql.SQL(
        """
        INSERT INTO public.review_comment (
            id,
            engagement,
            reference,
            title,
            description,
            raised_by,
            action_owner
            ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """)
    try:
        reference: str = get_reference(connection=connection, resource="review_comment", id=engagement_id)
        async with connection.cursor() as cursor:
            await cursor.execute(query, (
                get_unique_key(),
                engagement_id,
                reference,
                review_comment.title,
                review_comment.description,
                review_comment.raised_by.model_dump_json(),
                json.dumps(review_comment.model_dump().get("action_owner"))
            ))
        await connection.commit()
    except ForeignKeyViolation:
        await connection.rollback()
        raise HTTPException(status_code=409, detail="Engagement id is invalid")
    except UniqueViolation:
        await connection.rollback()
        raise HTTPException(status_code=409, detail="Review comment already exits")
    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error raising review comment {e}")

async def resolve_review_comment_(connection: AsyncConnection, review_comment: ResolveReviewComment, review_comment_id: str):
    query = sql.SQL(
        """
           UPDATE public.review_comment
           SET 
           resolution_summary = %s,
           resolution_details = %s,
           resolved_by = %s::jsonb,
           decision = %s
           WHERE id = %s;
        """)
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(query, (
                review_comment.resolution_summary,
                review_comment.resolution_details,
                review_comment.resolved_by.model_dump_json(),
                review_comment.decision,
                review_comment_id
            ))
        await connection.commit()
    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error resolving review comment {e}")

