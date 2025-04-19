import json
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from AuditNew.Internal.engagements.issue.schemas import *
from datetime import datetime
from psycopg import AsyncConnection, AsyncCursor, sql
from psycopg.errors import ForeignKeyViolation, UniqueViolation
from utils import get_unique_key

def safe_json_dump(obj):
    return obj.model_dump_json() if obj is not None else '{}'

async def edit_issue(connection: AsyncConnection, issue: Issue, issue_id: str):
    query = sql.SQL(
    """
    UPDATE public.issue
    SET 
        title = %s,
        criteria = %s,
        finding = %s,
        risk_rating = %s,
        process = %s,
        sub_process = %s,
        root_cause_description = %s,
        root_cause = %s,
        sub_root_cause = %s,
        risk_category = %s,
        sub_risk_category = %s,
        impact_description = %s,
        impact_category = %s,
        impact_sub_category = %s,
        recurring_status = %s,
        recommendation = %s,
        management_action_plan = %s,
        estimated_implementation_date = %s
    WHERE id = %s;
    """)
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(query, (
                            issue.title,
                            issue.criteria,
                            issue.finding,
                            issue.risk_rating,
                            issue.process,
                            issue.sub_process,
                            issue.root_cause_description,
                            issue.root_cause,
                            issue.sub_root_cause,
                            issue.risk_category,
                            issue.sub_risk_category,
                            issue.impact_description,
                            issue.impact_category,
                            issue.impact_sub_category,
                            issue.recurring_status,
                            issue.recommendation,
                            issue.management_action_plan,
                            issue.estimated_implementation_date,
                            issue_id
                    ))
        await connection.commit()
    except UniqueViolation:
        await connection.rollback()
        raise HTTPException(status_code=409, detail="Issue already exist")
    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating issue {e}")

async def add_new_issue(connection: AsyncConnection, issue: Issue, sub_program_id: str, engagement_id: str):
    query = sql.SQL(
        """
        INSERT INTO public.issue (
                id,
                sub_program,
                engagement,
                title,
                criteria,
                finding,
                risk_rating,
                source,
                sdi_name,
                process,
                sub_process,
                root_cause_description,
                root_cause,
                sub_root_cause,
                risk_category,
                sub_risk_category,
                impact_description,
                impact_category,
                impact_sub_category,
                recurring_status,
                recommendation,
                management_action_plan,
                estimated_implementation_date,
                regulatory,
                status,
                LOD1_implementer,
                LOD1_owner,
                LOD2_risk_manager,
                LOD2_compliance_officer,
                LOD3_audit_manager
                )
        VALUES (
         %s, %s, %s, %s, %s, %s, %s,
         %s, %s, %s, %s, %s, %s, %s, %s,
         %s, %s, %s, %s, %s, %s, %s,
         %s, %s, %s, %s, %s, %s, %s
        );
        """)
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(query,(
                get_unique_key(),
                sub_program_id,
                engagement_id,
                issue.title,
                issue.criteria,
                issue.finding,
                issue.risk_rating,
                issue.source,
                issue.sdi_name,
                issue.process,
                issue.sub_process,
                issue.root_cause_description,
                issue.root_cause,
                issue.sub_root_cause,
                issue.risk_category,
                issue.sub_risk_category,
                issue.impact_description,
                issue.impact_category,
                issue.impact_sub_category,
                issue.recurring_status,
                issue.recommendation,
                issue.management_action_plan,
                issue.estimated_implementation_date,
                issue.regulatory,
                issue.status,
                json.dumps(jsonable_encoder(issue.model_dump().get(IssueActors.IMPLEMENTER.value))),
                json.dumps(jsonable_encoder(issue.model_dump().get(IssueActors.OWNER.value))),
                json.dumps(jsonable_encoder(issue.model_dump().get(IssueActors.RISK_MANAGER.value))),
                json.dumps(jsonable_encoder(issue.model_dump().get(IssueActors.COMPLIANCE_OFFICER.value))),
                json.dumps(jsonable_encoder(issue.model_dump().get(IssueActors.AUDIT_MANAGER.value)))
            ))
        await connection.commit()
    except ForeignKeyViolation:
        await connection.rollback()
        raise HTTPException(status_code=40, detail="Sub program id is invalid")
    except UniqueViolation:
        await connection.rollback()
        raise HTTPException(status_code=409, detail="Issue already exist")
    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating issue {e}")

async def remove_issue(connection: AsyncConnection, issue_id: str):
    query = sql.SQL("DELETE FROM public.issue WHERE id = %s")
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(query, (issue_id,))
        await connection.commit()
    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting issue {e}")

async def send_issues_to_implementor(connection: AsyncConnection, issue_ids: IssueSendImplementation, user_email: str):
    try:
        issue_details = IssueImplementationDetails(
            notes="Issue sent to implementer",
            issued_by=User(
                name="",
                email=user_email,
                date_issued=datetime.now()
            ),
            type="send"
        )
        async with connection.cursor() as cursor:
            placeholders = ','.join(['%s'] * len(issue_ids.model_dump().get("id")))
            query_issue = sql.SQL("SELECT engagement FROM public.issue WHERE id IN ({})").format(placeholders)
            await cursor.execute(query_issue, issue_ids.id)
            rows = await cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            issue_data = [dict(zip(column_names, row_)) for row_ in rows]
            for issue in issue_data:
                allowed_to_send_list = []
                await cursor.execute("SELECT leads FROM public.engagements WHERE id = %s;", (issue.get("engagement"),))
                rows = await cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                leads = [dict(zip(column_names, row_)) for row_ in rows]
                for lead in leads[0].get("leads"):
                    allowed_to_send_list.append(lead.get("email"))
                if user_email in allowed_to_send_list:
                    data = await get_issue_and_issue_actors(
                        connection=connection,
                        cursor=cursor,
                        issue_ids=issue_ids,
                        issue_actors=IssueActors.IMPLEMENTER,
                        status={IssueStatus.NOT_STARTED},
                        next_status=IssueStatus.OPEN,
                        issue_details=issue_details
                    )
                else:
                    raise HTTPException(status_code=403, detail="Your not team lead")
    except HTTPException as h:
        raise HTTPException(status_code=h.status_code, detail=h.detail)

    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error send issues to implementor {e}")

async def save_issue_implementation_(connection: AsyncConnection, issue_details: IssueImplementationDetails, issue_id: str, user_email: str):
    query_issue = sql.SQL("SELECT * FROM public.issue WHERE id = %s;")
    query_update = sql.SQL(
        """
         UPDATE public.issue
         SET
         status = %s
         WHERE id = %s;
        """)
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(query_issue, (issue_id,))
            rows = await cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            issue_data = [dict(zip(column_names, row_)) for row_ in rows]
            allowed_to_save_list = []
            for implementer in issue_data[0].get(IssueActors.IMPLEMENTER.value):
                allowed_to_save_list.append(implementer.get("email"))
            if user_email in allowed_to_save_list:
                if issue_data[0].get("status") == IssueStatus.OPEN:
                    await update_issue_details(
                        connection=connection,
                        cursor=cursor,
                        issue_details=issue_details,
                        issue_id=issue_id
                    )
                    await cursor.execute(query_update, (IssueStatus.IN_PROGRESS_IMPLEMENTER, issue_id))
                    await connection.commit()
                if issue_data[0].get("status") == IssueStatus.IN_PROGRESS_IMPLEMENTER:
                    await update_issue_details(
                        connection=connection,
                        cursor=cursor,
                        issue_details=issue_details,
                        issue_id=issue_id
                    )
            else:
                raise HTTPException(status_code=403, detail="Your not issue implementer")
    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error saving issue implementation {e}")

async def send_issues_to_owner(connection: AsyncConnection, issue_id: str, user_email: str):
    query_issue = sql.SQL("SELECT * FROM public.issue WHERE id = %s;")
    try:
        issue_details = IssueImplementationDetails(
            notes="Issue sent to the owner",
            issued_by=User(
                name="",
                email=user_email,
                date_issued=datetime.now()
            ),
            type="send"
        )
        async with connection.cursor() as cursor:
            await cursor.execute(query_issue, (issue_id,))
            rows = await cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            issue_data = [dict(zip(column_names, row_)) for row_ in rows]
            allowed_to_save_list = []
            for implementer in issue_data[0].get(IssueActors.IMPLEMENTER.value):
                allowed_to_save_list.append(implementer.get("email"))
            if user_email in allowed_to_save_list:
                issue_ids = IssueSendImplementation(
                    id = [issue_id]
                )
                data = await get_issue_and_issue_actors(
                    connection=connection,
                    cursor=cursor,
                    issue_ids=issue_ids,
                    issue_actors=IssueActors.OWNER,
                    status={IssueStatus.IN_PROGRESS_IMPLEMENTER},
                    next_status=IssueStatus.IN_PROGRESS_OWNER,
                    issue_details=issue_details
                )
            else:
                raise HTTPException(status_code=403, detail="Your not issue implementer")
    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error sending issue to owner {e}")

async def send_accept_response(connection: AsyncConnection, issue: IssueAcceptResponse, issue_id: str, user_email: str):
    query = sql.SQL("SELECT * FROM public.issue WHERE id = %s")
    issue_details = IssueImplementationDetails(
        notes=issue.accept_notes,
        attachment=issue.accept_attachment,
        issued_by=User(
            name="",
            email=user_email,
            date_issued=datetime.now()
        ),
        type="accept"
    )
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(query, (issue_id,))
            rows = await cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            issue_data = [dict(zip(column_names, row_)) for row_ in rows]
            allowed_actors_list = []
            for actor in issue_data[0].get(issue.actor.value):
                allowed_actors_list.append(actor.get("email"))
            if user_email in allowed_actors_list:
                issue_ids = IssueSendImplementation(
                    id=[issue_id]
                )
                match issue.actor:
                    case issue.actor.OWNER:
                        issue_actor = IssueActors.COMPLIANCE_OFFICER if issue_data[0].get("regulatory") else IssueActors.RISK_MANAGER
                        data = await get_issue_and_issue_actors(
                            connection=connection,
                            cursor=cursor,
                            issue_ids=issue_ids,
                            issue_actors=issue_actor,
                            status={IssueStatus.IN_PROGRESS_OWNER},
                            next_status=IssueStatus.CLOSED_NOT_VERIFIED,
                            issue_details=issue_details
                        )
                    case issue.actor.RISK_MANAGER:
                        data = await get_issue_and_issue_actors(
                            connection=connection,
                            cursor=cursor,
                            issue_ids=issue_ids,
                            issue_actors=IssueActors.AUDIT_MANAGER,
                            status={IssueStatus.CLOSED_NOT_VERIFIED},
                            next_status=str(issue.lod2_feedback.value),
                            issue_details=issue_details
                        )
                    case issue.actor.COMPLIANCE_OFFICER:
                        data = await get_issue_and_issue_actors(
                            connection=connection,
                            cursor=cursor,
                            issue_ids=issue_ids,
                            issue_actors=IssueActors.AUDIT_MANAGER,
                            status={IssueStatus.CLOSED_NOT_VERIFIED},
                            next_status=str(issue.lod2_feedback.value),
                            issue_details=issue_details
                        )
                    case issue.actor.AUDIT_MANAGER:
                        data = []
                        await update_issue_status(
                            connection=connection,
                            cursor=cursor,
                            issue_ids=issue_ids,
                            status=issue_data[0].get("status"),
                            next_status=IssueStatus.CLOSED_VERIFIED_BY_AUDIT
                        )
                    case _:
                        pass
            else:
                raise HTTPException(status_code=403, detail=f"Your not issue {issue.actor.value}")

    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error sending accept response {e}")

async def send_decline_response(connection: AsyncConnection, issue: IssueDeclineResponse, issue_id: str, user_email: str):
    query = sql.SQL("SELECT * FROM public.issue WHERE id = %s")
    try:
        issue_details = IssueImplementationDetails(
            notes=issue.decline_notes,
            issued_by=User(
                name="",
                email=user_email,
                date_issued=datetime.now()
            ),
            type="decline"
        )
        async with connection.cursor() as cursor:
            await cursor.execute(query, (issue_id,))
            rows = await cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            issue_data = [dict(zip(column_names, row_)) for row_ in rows]
            allowed_actors_list = []
            for actor in issue_data[0].get(issue.actor.value):
                allowed_actors_list.append(actor.get("email"))
            if user_email in allowed_actors_list:
                issue_ids = IssueSendImplementation(
                    id=[issue_id]
                )
                match issue.actor:
                    case issue.actor.AUDIT_MANAGER:
                        issue_actor = IssueActors.COMPLIANCE_OFFICER if issue_data[0].get("regulatory") else IssueActors.RISK_MANAGER
                        data = await get_issue_and_issue_actors(
                            connection=connection,
                            cursor=cursor,
                            issue_ids=issue_ids,
                            issue_actors=issue_actor,
                            status={
                                IssueStatus.CLOSED_RISK_NA,
                                IssueStatus.CLOSED_RISK_ACCEPTED,
                                IssueStatus.CLOSED_VERIFIED_BY_RISK
                            },
                            next_status=IssueStatus.CLOSED_NOT_VERIFIED,
                            issue_details=issue_details
                        )

                    case issue.actor.RISK_MANAGER:
                        data = await get_issue_and_issue_actors(
                            connection=connection,
                            cursor=cursor,
                            issue_ids=issue_ids,
                            issue_actors=IssueActors.OWNER,
                            status={IssueStatus.CLOSED_NOT_VERIFIED},
                            next_status=IssueStatus.IN_PROGRESS_OWNER,
                            issue_details=issue_details
                        )
                    case issue.actor.COMPLIANCE_OFFICER:
                        data = await get_issue_and_issue_actors(
                            connection=connection,
                            cursor=cursor,
                            issue_ids=issue_ids,
                            issue_actors=IssueActors.OWNER,
                            status={IssueStatus.CLOSED_NOT_VERIFIED},
                            next_status=IssueStatus.IN_PROGRESS_OWNER,
                            issue_details=issue_details
                        )
                    case issue.actor.OWNER:
                        data = await get_issue_and_issue_actors(
                            connection=connection,
                            cursor=cursor,
                            issue_ids=issue_ids,
                            issue_actors=IssueActors.IMPLEMENTER,
                            status={IssueStatus.IN_PROGRESS_OWNER},
                            next_status=IssueStatus.IN_PROGRESS_IMPLEMENTER,
                            issue_details=issue_details
                        )
                    case _:
                        pass
            else:
                raise HTTPException(status_code=403, detail=f"Your not issue {issue.actor.value}")

    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error sending decline response {e}")

async def get_issue_and_issue_actors(
        connection: AsyncConnection,
        cursor: AsyncCursor,
        issue_ids: IssueSendImplementation,
        issue_actors: str,
        status: set[IssueStatus],
        next_status: str,
        issue_details: IssueImplementationDetails
):
    placeholders = ','.join(['%s'] * len(issue_ids.model_dump().get("id")))
    query_implementers = sql.SQL("SELECT * FROM public.issue WHERE id IN ({})").format(placeholders)
    query_update = sql.SQL(
        """
        UPDATE public.issue
        SET status = %s
        WHERE id = %s;
        """)
    await cursor.execute(query_implementers, issue_ids.id)
    rows = await cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    data = [dict(zip(column_names, row_)) for row_ in rows]
    issue_list = []
    for issue in data:
        implementors = []
        if issue.get("status") in status:
            for implementor in issue.get(issue_actors) or []:
                email = implementor.get("email")
                if email:
                    implementors.append(email)
            mailed_issue = MailedIssue(
                id=issue.get("id"),
                title=issue.get("title"),
                criteria=issue.get("criteria"),
                finding=issue.get("finding"),
                risk_rating=issue.get("risk_rating"),
                regulatory=issue.get("regulatory"),
                engagement=issue.get("engagement"),
                status=issue.get("status"),
                lod1_implementer=issue.get(IssueActors.IMPLEMENTER.value),
                lod1_owner=issue.get(IssueActors.OWNER.value),
                lod2_risk_manager=issue.get(IssueActors.RISK_MANAGER.value),
                lod2_compliance_officer=issue.get(IssueActors.COMPLIANCE_OFFICER.value),
                lod3_audit_manager=issue.get(IssueActors.AUDIT_MANAGER.value),
                implementors=implementors
            )
            await update_issue_details(
                connection=connection,
                cursor=cursor,
                issue_id=issue_ids.id[0],
                issue_details=issue_details
            )
            issue_list.append(mailed_issue)
            await cursor.execute(query_update, (next_status, issue.get("id")))
            await connection.commit()
        else:
            raise HTTPException(status_code=403, detail="Issue cant be updated right now")
    return issue_list

async def update_issue_status(cursor: AsyncCursor, connection: AsyncConnection, issue_ids: IssueSendImplementation, status: str, next_status: str):
    status_ = {
        IssueStatus.CLOSED_RISK_NA,
        IssueStatus.CLOSED_RISK_ACCEPTED,
        IssueStatus.CLOSED_VERIFIED_BY_RISK
    }
    placeholders = ','.join(['%s'] * len(issue_ids.model_dump().get("id")))
    query = sql.SQL(
        """
        UPDATE public.issue
        SET status = %s
        WHERE id IN ({})
        """).format(placeholders)
    if status in status_:
        params = [next_status] + issue_ids.id
        await cursor.execute(query, params)
        await connection.commit()
    else:
        raise HTTPException(status_code=403, detail="Issue cant be updated right now")

async def get_issue_from_actor(connection: AsyncConnection, user_email: str):
    conditions = []
    params = []
    jsonb_columns = [
        IssueActors.IMPLEMENTER.value,
        IssueActors.OWNER.value,
        IssueActors.RISK_MANAGER.value,
        IssueActors.COMPLIANCE_OFFICER.value,
        IssueActors.AUDIT_MANAGER.value
    ]
    for col in jsonb_columns:
        conditions.append(f"""
            (
                status != 'Not started' AND EXISTS (
                    SELECT 1
                    FROM jsonb_array_elements(
                        CASE
                            WHEN {col} IS NOT NULL AND jsonb_typeof({col}) = 'array' THEN {col}
                            ELSE '[]'::jsonb
                        END
                    ) AS elem
                    WHERE elem->>%s = %s
                )
            )
        """)
        params.extend(["email", user_email])  # add key and value for each condition

    # Join all conditions with OR
    where_clause = " OR ".join(conditions)

    query = sql.SQL("SELECT * FROM public.issue WHERE  {};").format(where_clause)

    try:
        async with connection.cursor() as cursor:
            await cursor.execute(query, params)
            rows = await cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row_)) for row_ in rows]
    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error fetching issue by actors {e}")

async def update_issue_details(connection: AsyncConnection, cursor: AsyncCursor, issue_id: str, issue_details: IssueImplementationDetails):
    query = sql.SQL(
        """
          INSERT INTO public.implementation_details (id, issue, notes, attachments, issued_by, type)
          VALUES (%s, %s, %s, %s, %s, %s);
        """)
    await cursor.execute(query, (
        get_unique_key(),
        issue_id,
        issue_details.notes,
        json.dumps(issue_details.model_dump().get("attachment")),
        issue_details.issued_by.model_dump_json(),
        issue_details.type
    ))
    await connection.commit()

async def get_issue_updates(connection: AsyncConnection, issue_id: str):
    query = sql.SQL("SELECT * FROM public.implementation_details WHERE issue = %s;")
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(query, (issue_id,))
            rows = await cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row_)) for row_ in rows]
    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error fetching issue details {e}")

async def mark_issue_prepared(connection: AsyncConnection, prepare: User, issue_id: str):
    query = sql.SQL(
        """
          UPDATE public.issue
          SET 
          prepared_by = %s::jsonb
          WHERE id = %s;
        """)
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(query, (prepare.model_dump_json(), issue_id))
        await connection.commit()
    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error mark issue prepared {e}")

async def mark_issue_reviewed(connection: AsyncConnection, review: User, issue_id: str):
    query = sql.SQL(
        """
          UPDATE public.issue
          SET 
          reviewed_by = %s::jsonb
          WHERE id = %s;
        """)
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(query, (review.model_dump_json(), issue_id))
        await connection.commit()
    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error mark issue reviewed {e}")

async def mark_issue_reportable(connection: AsyncConnection, reportable: bool, issue_id: str):
    query = sql.SQL(
        """
          UPDATE public.issue
          SET 
          reportable = %s
          WHERE id = %s;
        """)
    try:
        async with connection.cursor() as cursor:
            await cursor.execute(query, (reportable, issue_id))
        await connection.commit()
    except Exception as e:
        await connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error mark issue reportable {e}")


