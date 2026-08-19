from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from collections import Counter

from app.core.database import get_db, SessionLocal
from app.models.analysis_run import AnalysisRun
from app.models.import_ticket_id import ImportTicketID
from app.models.ticket import Ticket
from app.models.ticket_classification import TicketClassification
from app.models.category import Category
from app.models.client import Client  # ✅ FIX
from app.services.platforms.factory import get_platform_service  # ✅ FIX

from app.services.ai.ai_service import classify_ticket_batch

router = APIRouter(prefix="/analysis", tags=["Analysis"])


# ------------------------
# TOP DRIVERS
# ------------------------
def calculate_top_drivers(classifications):
    counter = Counter()

    for c in classifications:
        if c.ai_main_category:
            counter[(c.ai_main_category, c.ai_subcategory)] += 1

    return [
        {
            "main_category": k[0],
            "subcategory": k[1],
            "count": v,
        }
        for k, v in counter.most_common(5)
    ]


# ------------------------
# START ANALYSIS (ASYNC)
# ------------------------
@router.post("/run")
def run_analysis(
    client_id: int,
    import_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):

    run = AnalysisRun(
        client_id=client_id,
        import_id=import_id,
        started_by=1,
        status="running",
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    # 🚀 ASYNC START
    background_tasks.add_task(process_analysis, run.id, client_id, import_id)

    return {
        "message": "Analysis started",
        "run_id": run.id,
    }


# ------------------------
# BACKGROUND PROCESS
# ------------------------
def process_analysis(run_id: int, client_id: int, import_id: int):

    db = SessionLocal()

    try:
        run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()

        client = db.query(Client).filter(Client.id == client_id).first()

        platform_service = get_platform_service(client, db)

        ticket_ids = (
            db.query(ImportTicketID)
            .filter(ImportTicketID.import_id == import_id)
            .limit(250)
            .all()
        )

        run.total_ticket_ids = len(ticket_ids)
        db.commit()

        categories = (
            db.query(Category)
            .filter(Category.client_id == client_id, Category.is_active == True)
            .all()
        )

        categories_list = [
            {
                "main_category": c.main_category,
                "subcategory": c.subcategory,
                "description": c.description,
            }
            for c in categories
        ]

        tickets_for_ai = []
        ticket_db_map = []

        # FETCH TICKETS
        for imported_ticket in ticket_ids:

            customer_message, agent_response, raw_ticket = (
                platform_service.extract_first_customer_and_agent(
                    imported_ticket.external_ticket_id
                )
            )

            ticket = Ticket(
                client_id=client_id,
                import_id=import_id,
                external_ticket_id=imported_ticket.external_ticket_id,
                subject=raw_ticket.get("subject"),
                customer_message=customer_message,
                agent_response=agent_response,
                status=raw_ticket.get("status"),
                channel=raw_ticket.get("channel"),
                raw_ticket_json=raw_ticket,
                is_valid_closed_ticket=True if customer_message else False,
            )

            db.add(ticket)
            db.commit()
            db.refresh(ticket)

            tickets_for_ai.append(
                {
                    "customer_message": customer_message,
                    "agent_response": agent_response,
                }
            )

            ticket_db_map.append(ticket)

        # AI BATCH PROCESS
        BATCH_SIZE = 25
        results = []

        for i in range(0, len(tickets_for_ai), BATCH_SIZE):

            batch = tickets_for_ai[i : i + BATCH_SIZE]

            batch_results = classify_ticket_batch(batch, categories_list)

            results.extend(batch_results)

            # 🔥 PROGRESS
            run.analyzed_tickets_count = len(results)
            db.commit()

        # SAVE RESULTS
        support_count = 0
        non_support_count = 0

        for i, result in enumerate(results):

            ticket = ticket_db_map[i]

            if result["is_support_ticket"]:
                support_count += 1
            else:
                non_support_count += 1

            classification = TicketClassification(
                analysis_run_id=run.id,
                ticket_id=ticket.id,
                ai_main_category=result["main_category"],
                ai_subcategory=result["subcategory"],
                ai_confidence=result["confidence"],
                ai_reason=result["reason"],
                is_support_ticket=result["is_support_ticket"],
                suggested_new_main_category=result["suggested_new_main_category"],
                suggested_new_subcategory=result["suggested_new_subcategory"],
            )

            db.add(classification)

        db.commit()

        # TOP DRIVERS
        classifications = db.query(TicketClassification).filter(
            TicketClassification.analysis_run_id == run.id
        ).all()

        run.summary_json = {
            "top_5_drivers": calculate_top_drivers(classifications)
        }

        run.support_count = support_count
        run.non_support_count = non_support_count
        run.status = "completed"

        db.commit()

    except Exception as e:
        run.status = "failed"
        run.error_message = str(e)
        db.commit()

    finally:
        db.close()


# ------------------------
# FILTER ENDPOINT
# ------------------------
@router.get("/runs/{run_id}/tickets")
def get_analysis_run_tickets(
    run_id: int,
    is_support_ticket: bool | None = None,
    main_category: str | None = None,
    subcategory: str | None = None,
    db: Session = Depends(get_db),
):

    query = (
        db.query(TicketClassification, Ticket)
        .join(Ticket, Ticket.id == TicketClassification.ticket_id)
        .filter(TicketClassification.analysis_run_id == run_id)
    )

    if is_support_ticket is not None:
        query = query.filter(TicketClassification.is_support_ticket == is_support_ticket)

    if main_category:
        query = query.filter(TicketClassification.ai_main_category == main_category)

    if subcategory:
        query = query.filter(TicketClassification.ai_subcategory == subcategory)

    rows = query.all()

    return [
        {
            "ticket_id": ticket.id,
            "main_category": classification.ai_main_category,
            "subcategory": classification.ai_subcategory,
            "confidence": classification.ai_confidence,
        }
        for classification, ticket in rows
    ]

@router.get("/runs/{run_id}")
def get_analysis_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return {
        "id": run.id,
        "status": run.status,
        "total_ticket_ids": run.total_ticket_ids,
        "analyzed_tickets_count": run.analyzed_tickets_count,
        "support_count": run.support_count,
        "non_support_count": run.non_support_count,
        "error_message": run.error_message,
        "summary": run.summary_json,
    }