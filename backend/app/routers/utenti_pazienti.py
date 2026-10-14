from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
from app.db import get_db

router = APIRouter(prefix="/utenti_pazienti", tags=["Utenti Pazienti"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

UTENTE_NON_TROVATO = "Utente Paziente non trovato"


@router.post("/login", response_model=schemas.UtentePazienteResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_utente_paziente_by_username(db, request.username)
    if not user or not pwd_context.verify(request.password, user.password):
        raise HTTPException(status_code=401, detail="Username o password errati")
    return user


@router.get("/", response_model=List[schemas.UtentePazienteResponse])
def get_utenti_pazienti(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_utenti_pazienti(db, skip=skip, limit=limit)


@router.get("/{utente_id}", response_model=schemas.UtentePazienteResponse)
def get_utente_paziente(utente_id: int, db: Session = Depends(get_db)):
    utente = crud.get_utente_paziente(db, utente_id)
    if not utente:
        raise HTTPException(status_code=404, detail=UTENTE_NON_TROVATO)
    return utente


@router.get("/by-cf/{codice_fiscale}", response_model=schemas.UtentePazienteResponse)
def get_utente_paziente_by_cf(codice_fiscale: str, db: Session = Depends(get_db)):
    utente = crud.get_utente_paziente_by_cf(db, codice_fiscale)
    if not utente:
        raise HTTPException(status_code=404, detail=UTENTE_NON_TROVATO)
    return utente


@router.get("/by-username/{username}", response_model=schemas.UtentePazienteResponse)
def get_utente_paziente_by_username(username: str, db: Session = Depends(get_db)):
    utente = crud.get_utente_paziente_by_username(db, username)
    if not utente:
        raise HTTPException(status_code=404, detail=UTENTE_NON_TROVATO)
    return utente


@router.post(
    "/",
    response_model=schemas.UtentePazienteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_utente_paziente(
    utente: schemas.UtentePazienteCreate, db: Session = Depends(get_db)
):
    if crud.get_utente_paziente_by_cf(db, utente.codice_fiscale):
        raise HTTPException(status_code=400, detail="Codice fiscale già registrato")
    utente.password = pwd_context.hash(utente.password)
    return crud.create_utente_paziente(db, utente)


@router.put("/{utente_id}", response_model=schemas.UtentePazienteResponse)
def update_utente_paziente(
    utente_id: int,
    utente: schemas.UtentePazienteCreate,
    db: Session = Depends(get_db),
):
    if not crud.get_utente_paziente(db, utente_id):
        raise HTTPException(status_code=404, detail=UTENTE_NON_TROVATO)
    utente.password = pwd_context.hash(utente.password)
    return crud.update_utente_paziente(db, utente_id, utente)


@router.delete("/{utente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_utente_paziente(utente_id: int, db: Session = Depends(get_db)):
    if not crud.delete_utente_paziente(db, utente_id):
        raise HTTPException(status_code=404, detail=UTENTE_NON_TROVATO)
