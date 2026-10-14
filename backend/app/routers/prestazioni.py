from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
from app.db import get_db

router = APIRouter(prefix="/prestazioni", tags=["Prestazioni"])


@router.get("/", response_model=List[schemas.PrestazioneResponse])
def get_prestazioni(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_prestazioni(db, skip=skip, limit=limit)


@router.get("/{prestazione_id}", response_model=schemas.PrestazioneResponse)
def get_prestazione(prestazione_id: int, db: Session = Depends(get_db)):
    prestazione = crud.get_prestazione(db, prestazione_id)
    if not prestazione:
        raise HTTPException(status_code=404, detail="Prestazione non trovata")
    return prestazione


@router.post(
    "/",
    response_model=schemas.PrestazioneResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_prestazione(
    prestazione: schemas.PrestazioneCreate, db: Session = Depends(get_db)
):
    return crud.create_prestazione(db, prestazione)
