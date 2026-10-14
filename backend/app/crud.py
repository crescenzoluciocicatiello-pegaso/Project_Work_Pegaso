from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Query, Session, joinedload

import app.models as models
import app.schemas as schemas

STATO_SLOT_LIBERO = "0"
STATO_SLOT_OCCUPATO = "1"


def _salva(db: Session, oggetto):
    db.add(oggetto)
    db.commit()
    db.refresh(oggetto)
    return oggetto


def _filtra_per_date(
    query: Query,
    data_inizio: Optional[datetime],
    data_fine: Optional[datetime],
) -> Query:
    if data_inizio:
        query = query.filter(models.Slot.data_inizio_slot >= data_inizio)
    if data_fine:
        query = query.filter(models.Slot.data_fine_slot <= data_fine)
    return query


# pazienti

def get_utenti_pazienti(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UtentePaziente).offset(skip).limit(limit).all()


def get_utente_paziente(db: Session, utente_id: int):
    return (
        db.query(models.UtentePaziente)
        .filter(models.UtentePaziente.id == utente_id)
        .first()
    )


def get_utente_paziente_by_cf(db: Session, codice_fiscale: str):
    return (
        db.query(models.UtentePaziente)
        .filter(models.UtentePaziente.codice_fiscale == codice_fiscale)
        .first()
    )


def get_utente_paziente_by_username(db: Session, username: str):
    return (
        db.query(models.UtentePaziente)
        .filter(models.UtentePaziente.username == username)
        .first()
    )


def create_utente_paziente(db: Session, utente: schemas.UtentePazienteCreate):
    return _salva(db, models.UtentePaziente(**utente.model_dump()))


def update_utente_paziente(
    db: Session, utente_id: int, utente: schemas.UtentePazienteCreate
):
    db_utente = get_utente_paziente(db, utente_id)
    if not db_utente:
        return None

    for key, value in utente.model_dump(exclude_unset=True).items():
        setattr(db_utente, key, value)

    db.commit()
    db.refresh(db_utente)
    return db_utente


def delete_utente_paziente(db: Session, utente_id: int) -> bool:
    db_utente = get_utente_paziente(db, utente_id)
    if not db_utente:
        return False

    db.delete(db_utente)
    db.commit()
    return True


# medici

def get_medici(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Medico).offset(skip).limit(limit).all()


def get_medico(db: Session, medico_id: int):
    return db.query(models.Medico).filter(models.Medico.id == medico_id).first()


def get_medico_by_cf(db: Session, codice_fiscale: str):
    return (
        db.query(models.Medico)
        .filter(models.Medico.codice_fiscale == codice_fiscale)
        .first()
    )


def create_medico(db: Session, medico: schemas.MedicoCreate):
    return _salva(db, models.Medico(**medico.model_dump()))


# prestazioni

def get_prestazioni(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Prestazione).offset(skip).limit(limit).all()


def get_prestazione(db: Session, prestazione_id: int):
    return (
        db.query(models.Prestazione)
        .filter(models.Prestazione.id == prestazione_id)
        .first()
    )


def create_prestazione(db: Session, prestazione: schemas.PrestazioneCreate):
    return _salva(db, models.Prestazione(**prestazione.model_dump()))


# slot

def get_slot(db: Session, slot_id: int):
    return db.query(models.Slot).filter(models.Slot.id == slot_id).first()


def get_slots_disponibili(
    db: Session,
    data_inizio: Optional[datetime] = None,
    data_fine: Optional[datetime] = None,
):
    query = db.query(models.Slot).filter(models.Slot.stato_slot == STATO_SLOT_LIBERO)
    return _filtra_per_date(query, data_inizio, data_fine).all()


def get_slots_disponibili_by_codice_prestazione(
    db: Session,
    id_prestazione: int,
    data_inizio: Optional[datetime] = None,
    data_fine: Optional[datetime] = None,
):
    query = db.query(models.Slot).filter(
        models.Slot.stato_slot == STATO_SLOT_LIBERO,
        models.Slot.id_prestazione == id_prestazione,
    )
    return _filtra_per_date(query, data_inizio, data_fine).all()


def create_slot(db: Session, slot: schemas.SlotCreate):
    return _salva(db, models.Slot(**slot.model_dump()))


def update_slot_status(db: Session, slot_id: int, status: str):
    db_slot = get_slot(db, slot_id)
    if db_slot:
        db_slot.stato_slot = status
        db.commit()
        db.refresh(db_slot)
    return db_slot


# ricette

def _aggiungi_nome_medico(ricetta) -> None:
    if ricetta.medico:
        ricetta.nome_medico = f"{ricetta.medico.nome} {ricetta.medico.cognome}"


def get_ricette(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Ricetta).offset(skip).limit(limit).all()


def get_ricetta(db: Session, ricetta_id: int):
    ricetta = (
        db.query(models.Ricetta)
        .options(joinedload(models.Ricetta.medico))
        .filter(models.Ricetta.id == ricetta_id)
        .first()
    )
    if ricetta:
        _aggiungi_nome_medico(ricetta)
    return ricetta


def get_ricette_by_paziente(db: Session, paziente_id: int):
    ricette = (
        db.query(models.Ricetta)
        .options(joinedload(models.Ricetta.medico))
        .filter(models.Ricetta.id_paziente == paziente_id)
        .all()
    )
    for ricetta in ricette:
        _aggiungi_nome_medico(ricetta)
    return ricette


def create_ricetta(db: Session, ricetta: schemas.RicettaCreate):
    return _salva(db, models.Ricetta(**ricetta.model_dump()))


# ricetta - prestazione

def get_ricetta_prestazione(db: Session, id_assoc: int):
    return (
        db.query(models.RicettaPrestazione)
        .filter(models.RicettaPrestazione.id == id_assoc)
        .first()
    )


def get_ricette_prestazioni_by_ricetta(db: Session, id_ricetta: int):
    assocs = (
        db.query(models.RicettaPrestazione)
        .options(joinedload(models.RicettaPrestazione.prestazione))
        .filter(models.RicettaPrestazione.id_ricetta == id_ricetta)
        .all()
    )
    for assoc in assocs:
        assoc.codice_prestazione = assoc.prestazione.codice_prestazione
        assoc.descrizione = assoc.prestazione.descrizione
    return assocs


def create_ricetta_prestazione(db: Session, assoc: schemas.RicettaPrestazioneCreate):
    return _salva(db, models.RicettaPrestazione(**assoc.model_dump()))


def set_ricetta_prestazione_prenotata(db: Session, id_assoc: int):
    db_assoc = get_ricetta_prestazione(db, id_assoc)
    if db_assoc:
        db_assoc.prenotata = True
        db.commit()
    return db_assoc


def delete_ricetta_prestazione(db: Session, id_assoc: int) -> bool:
    db_assoc = get_ricetta_prestazione(db, id_assoc)
    if not db_assoc:
        return False

    db.delete(db_assoc)
    db.commit()
    return True


# prenotazioni

def get_prenotazioni_dettagliate(
    db: Session,
    paziente_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
):
    query = (
        db.query(
            models.Prenotazione,
            models.UtentePaziente.codice_fiscale,
            models.UtentePaziente.nome,
            models.UtentePaziente.cognome,
            models.UtentePaziente.data_nascita,
            models.UtentePaziente.comune_nascita,
            models.Prestazione.codice_prestazione,
            models.Prestazione.descrizione,
            models.Slot.data_inizio_slot,
            models.Slot.data_fine_slot,
        )
        .join(
            models.UtentePaziente,
            models.Prenotazione.id_paziente == models.UtentePaziente.id,
        )
        .join(models.Slot, models.Prenotazione.id_slot == models.Slot.id)
        .join(
            models.Prestazione,
            models.Slot.id_prestazione == models.Prestazione.id,
        )
    )
    if paziente_id is not None:
        query = query.filter(models.Prenotazione.id_paziente == paziente_id)

    # copio i dati delle altre tabelle sulla prenotazione per PrenotazioneResponse
    prenotazioni = []
    for riga in query.offset(skip).limit(limit).all():
        p = riga[0]
        p.codice_fiscale = riga.codice_fiscale
        p.nome = riga.nome
        p.cognome = riga.cognome
        p.data_nascita = riga.data_nascita
        p.comune_nascita = riga.comune_nascita
        p.codice_prestazione = riga.codice_prestazione
        p.descrizione = riga.descrizione
        p.data_inizio_slot = riga.data_inizio_slot
        p.data_fine_slot = riga.data_fine_slot
        prenotazioni.append(p)
    return prenotazioni


def create_prenotazione(db: Session, prenotazione: schemas.PrenotazioneCreate):
    db_prenotazione = models.Prenotazione(**prenotazione.model_dump())
    db.add(db_prenotazione)

    db_slot = get_slot(db, prenotazione.id_slot)
    if db_slot:
        db_slot.stato_slot = STATO_SLOT_OCCUPATO

    db.commit()
    db.refresh(db_prenotazione)
    return db_prenotazione


def delete_prenotazione_by_ricetta_prestazione(db: Session, id_assoc: int) -> bool:
    db_assoc = get_ricetta_prestazione(db, id_assoc)
    if not db_assoc or not db_assoc.prenotata:
        return False

    # prendo l'ultima prenotazione fatta per questa prestazione
    prenotazione = (
        db.query(models.Prenotazione)
        .filter(models.Prenotazione.id_ricetta_prestazione == id_assoc)
        .order_by(models.Prenotazione.id.desc())
        .first()
    )
    db_assoc.prenotata = False
    if prenotazione:
        if prenotazione.slot:
            prenotazione.slot.stato_slot = STATO_SLOT_LIBERO
        db.delete(prenotazione)

    db.commit()
    return True
