from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import os
from uuid import uuid4

from app.core.database import get_db
from app.models.import_file import ImportFile
from app.models.import_ticket_id import ImportTicketID
from app.models.client import Client
from app.models.user import User

router = APIRouter(prefix="/imports", tags=["Imports"])

@router.post("/tickets")
def upload_ticket_ids(
    client_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # 1. Validate client
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # 2. Save file locally
    folder = "uploads"
    os.makedirs(folder, exist_ok=True)

    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid4()}.{file_ext}"
    filepath = os.path.join(folder, filename)

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    # 3. Create ImportFile record
    import_file = ImportFile(
        client_id=client_id,
        uploaded_by=1,  # TEMP (later replace with current user)
        file_name=file.filename,
        file_path=filepath,
        status="processing",
    )
    db.add(import_file)
    db.commit()
    db.refresh(import_file)

    try:
        # 4. Read Excel
        df = pd.read_excel(filepath)

        # IMPORTANT: adjust column name if needed
        possible_columns = [
            "Ticket id",
            "Ticket ID",
            "ticket_id",
            "ticket id"
        ]

        ticket_id_column = next((col for col in possible_columns if col in df.columns), None)

        if not ticket_id_column:
            raise Exception("Excel must contain a ticket ID column")

        ticket_ids = df[ticket_id_column].dropna().astype(str).tolist()

        records = [
            ImportTicketID(
                import_id=import_file.id,
                external_ticket_id=tid,
            )
            for tid in ticket_ids
        ]

        db.bulk_save_objects(records)

        # 6. Update status
        import_file.status = "processed"
        db.commit()

        return {
            "message": "Upload successful",
            "total_ids": len(ticket_ids),
            "import_id": import_file.id,
        }

    except Exception as e:
        import_file.status = "failed"
        import_file.error_message = str(e)
        db.commit()

        raise HTTPException(status_code=400, detail=str(e))