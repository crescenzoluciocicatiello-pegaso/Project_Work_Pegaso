from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
from app.db import get_db

router = APIRouter(prefix="/prenotazioni", tags=["Prenotazioni"])


@router.get("/", response_model=List[schemas.PrenotazioneResponse])
def get_prenotazioni(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_prenotazioni_dettagliate(db, skip=skip, limit=limit)


@router.get(
    "/paziente/{paziente_id}", response_model=List[schemas.PrenotazioneResponse]
)
def get_prenotazioni_by_paziente(paziente_id: int, db: Session = Depends(get_db)):
    return crud.get_prenotazioni_dettagliate(db, paziente_id=paziente_id)


@router.post(
    "/",
    response_model=schemas.PrenotazioneCreate,
    status_code=status.HTTP_201_CREATED,
)
def create_prenotazione(
    prenotazione: schemas.PrenotazioneCreate, db: Session = Depends(get_db)
):
    slot = crud.get_slot(db, prenotazione.id_slot)
    if not slot or slot.stato_slot != crud.STATO_SLOT_LIBERO:
        raise HTTPException(
            status_code=400, detail="Slot non disponibile o inesistente"
        )

    db_prenotazione = crud.create_prenotazione(db, prenotazione)
    crud.set_ricetta_prestazione_prenotata(db, prenotazione.id_ricetta_prestazione)
    return db_prenotazione


@router.delete(
    "/ricetta-prestazione/{id_ricetta_prestazione}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_prenotazione(id_ricetta_prestazione: int, db: Session = Depends(get_db)):
    if not crud.delete_prenotazione_by_ricetta_prestazione(db, id_ricetta_prestazione):
        raise HTTPException(
            status_code=404,
            detail="Nessuna prenotazione attiva per questa prestazione",
        )
