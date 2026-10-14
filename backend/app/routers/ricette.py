from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
from app.db import get_db

router = APIRouter(prefix="/ricette", tags=["Ricette"])


@router.get("/", response_model=List[schemas.RicettaResponse])
def get_ricette(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_ricette(db, skip=skip, limit=limit)


@router.get("/{ricetta_id}", response_model=schemas.RicettaResponse)
def get_ricetta(ricetta_id: int, db: Session = Depends(get_db)):
    ricetta = crud.get_ricetta(db, ricetta_id)
    if not ricetta:
        raise HTTPException(status_code=404, detail="Ricetta non trovata")
    return ricetta


@router.get(
    "/paziente/{paziente_id}", response_model=List[schemas.RicettaResponsePaziente]
)
def get_ricette_by_paziente(paziente_id: int, db: Session = Depends(get_db)):
    ricette = crud.get_ricette_by_paziente(db, paziente_id)
    if not ricette:
        raise HTTPException(
            status_code=404,
            detail="Nessuna ricetta trovata per il paziente specificato",
        )
    return ricette


@router.post(
    "/", response_model=schemas.RicettaResponse, status_code=status.HTTP_201_CREATED
)
def create_ricetta(ricetta: schemas.RicettaCreate, db: Session = Depends(get_db)):
    return crud.create_ricetta(db, ricetta)
