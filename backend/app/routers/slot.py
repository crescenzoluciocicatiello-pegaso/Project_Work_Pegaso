from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
from app.db import get_db

router = APIRouter(prefix="/slot", tags=["Slot"])

STATI_SLOT_VALIDI = (crud.STATO_SLOT_LIBERO, crud.STATO_SLOT_OCCUPATO)


@router.get("/disponibili", response_model=List[schemas.SlotResponse])
def get_slots_disponibili(
    data_inizio: Optional[datetime] = Query(None),
    data_fine: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    return crud.get_slots_disponibili(db, data_inizio, data_fine)


@router.get(
    "/disponibili-by-codice-prestazione", response_model=List[schemas.SlotResponse]
)
def get_slots_disponibili_by_codice_prestazione(
    id_prestazione: int = Query(..., description="ID della prestazione"),
    data_inizio: Optional[datetime] = Query(None),
    data_fine: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    return crud.get_slots_disponibili_by_codice_prestazione(
        db, id_prestazione, data_inizio, data_fine
    )


@router.post(
    "/", response_model=schemas.SlotResponse, status_code=status.HTTP_201_CREATED
)
def create_slot(slot: schemas.SlotCreate, db: Session = Depends(get_db)):
    return crud.create_slot(db, slot)


@router.put("/{slot_id}/status", response_model=schemas.SlotResponse)
def update_slot_status(slot_id: int, status: str, db: Session = Depends(get_db)):
    if status not in STATI_SLOT_VALIDI:
        raise HTTPException(
            status_code=400,
            detail="Stato non valido, usa '0' (libero) o '1' (occupato)",
        )
    return crud.update_slot_status(db, slot_id, status)
