from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
from app.db import get_db

router = APIRouter(prefix="/ricetta-prestazione", tags=["ricetta_prestazione"])


@router.get("/{id_ricetta}", response_model=List[schemas.RicettaPrestazioneResponse])
def get_ricette_prestazioni_by_ricetta(id_ricetta: int, db: Session = Depends(get_db)):
    assocs = crud.get_ricette_prestazioni_by_ricetta(db, id_ricetta)
    if not assocs:
        raise HTTPException(status_code=404, detail="Prestazioni non trovate")
    return assocs


@router.post("/", response_model=schemas.RicettaPrestazioneBase)
def create_ricetta_prestazione(
    assoc: schemas.RicettaPrestazioneCreate, db: Session = Depends(get_db)
):
    return crud.create_ricetta_prestazione(db, assoc)


@router.delete("/{assoc_id}")
def delete_ricetta_prestazione(assoc_id: int, db: Session = Depends(get_db)):
    if not crud.delete_ricetta_prestazione(db, assoc_id):
        raise HTTPException(status_code=404, detail="Associazione non trovata")
    return {"message": "Associazione eliminata con successo"}
