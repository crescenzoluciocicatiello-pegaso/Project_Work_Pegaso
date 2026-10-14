from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
from app.db import get_db

router = APIRouter(prefix="/medici", tags=["Medici"])


@router.get("/", response_model=List[schemas.MedicoResponse])
def get_medici(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_medici(db, skip=skip, limit=limit)


@router.get("/{medico_id}", response_model=schemas.MedicoResponse)
def get_medico(medico_id: int, db: Session = Depends(get_db)):
    medico = crud.get_medico(db, medico_id)
    if not medico:
        raise HTTPException(status_code=404, detail="Medico non trovato")
    return medico


@router.get("/by-cf/{codice_fiscale}", response_model=schemas.MedicoResponse)
def get_medico_by_cf(codice_fiscale: str, db: Session = Depends(get_db)):
    medico = crud.get_medico_by_cf(db, codice_fiscale)
    if not medico:
        raise HTTPException(status_code=404, detail="Medico non trovato")
    return medico


@router.post(
    "/", response_model=schemas.MedicoResponse, status_code=status.HTTP_201_CREATED
)
def create_medico(medico: schemas.MedicoCreate, db: Session = Depends(get_db)):
    if crud.get_medico_by_cf(db, medico.codice_fiscale):
        raise HTTPException(status_code=400, detail="Codice fiscale già registrato")
    return crud.create_medico(db, medico)
