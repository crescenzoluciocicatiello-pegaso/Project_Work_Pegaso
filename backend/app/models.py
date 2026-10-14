from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UtentePaziente(Base):
    __tablename__ = "utente_paziente"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(255))  # hash bcrypt
    email: Mapped[str] = mapped_column(String(255), unique=True)
    nome: Mapped[str] = mapped_column(String(50))
    cognome: Mapped[str] = mapped_column(String(50))
    sesso: Mapped[Optional[str]] = mapped_column(String(1))
    telefono: Mapped[Optional[str]] = mapped_column(String(20))
    data_nascita: Mapped[date] = mapped_column(Date)
    comune_nascita: Mapped[Optional[str]] = mapped_column(String(50))
    codice_fiscale: Mapped[str] = mapped_column(String(16), unique=True)

    ricette: Mapped[List["Ricetta"]] = relationship(
        back_populates="paziente", cascade="all, delete-orphan"
    )
    prenotazioni: Mapped[List["Prenotazione"]] = relationship(
        back_populates="paziente", cascade="all, delete-orphan"
    )


class Medico(Base):
    __tablename__ = "medico"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(50))
    cognome: Mapped[str] = mapped_column(String(50))
    specializzazione: Mapped[Optional[str]] = mapped_column(String(100))
    codice_fiscale: Mapped[str] = mapped_column(String(16), unique=True)

    ricette: Mapped[List["Ricetta"]] = relationship(back_populates="medico")


class Prestazione(Base):
    __tablename__ = "prestazione"

    id: Mapped[int] = mapped_column(primary_key=True)
    codice_prestazione: Mapped[str] = mapped_column(String(20), unique=True)
    descrizione: Mapped[str] = mapped_column(String(255))

    ricette_collegate: Mapped[List["RicettaPrestazione"]] = relationship(
        back_populates="prestazione"
    )
    slots: Mapped[List["Slot"]] = relationship(back_populates="prestazione")


class Slot(Base):
    __tablename__ = "slot"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_inizio_slot: Mapped[datetime] = mapped_column(DateTime)
    data_fine_slot: Mapped[datetime] = mapped_column(DateTime)
    stato_slot: Mapped[str] = mapped_column(String(1), server_default="0")  # 0 libero, 1 occupato
    id_prestazione: Mapped[int] = mapped_column(
        ForeignKey("prestazione.id", ondelete="RESTRICT")
    )

    prestazione: Mapped["Prestazione"] = relationship(back_populates="slots")
    prenotazioni: Mapped[List["Prenotazione"]] = relationship(back_populates="slot")


class Ricetta(Base):
    __tablename__ = "ricetta"

    id: Mapped[int] = mapped_column(primary_key=True)
    nre: Mapped[str] = mapped_column(String(15), unique=True)
    data_emissione: Mapped[date] = mapped_column(Date)
    data_scadenza: Mapped[Optional[date]] = mapped_column(Date)

    id_paziente: Mapped[int] = mapped_column(
        ForeignKey("utente_paziente.id", ondelete="CASCADE")
    )
    id_medico: Mapped[int] = mapped_column(ForeignKey("medico.id", ondelete="RESTRICT"))

    paziente: Mapped["UtentePaziente"] = relationship(back_populates="ricette")
    medico: Mapped["Medico"] = relationship(back_populates="ricette")
    prestazioni: Mapped[List["RicettaPrestazione"]] = relationship(
        back_populates="ricetta", cascade="all, delete-orphan"
    )


class RicettaPrestazione(Base):
    __tablename__ = "ricetta_prestazione"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_ricetta: Mapped[int] = mapped_column(
        ForeignKey("ricetta.id", ondelete="CASCADE")
    )
    id_prestazione: Mapped[int] = mapped_column(
        ForeignKey("prestazione.id", ondelete="CASCADE")
    )
    prenotata: Mapped[bool] = mapped_column(default=False)

    ricetta: Mapped["Ricetta"] = relationship(back_populates="prestazioni")
    prestazione: Mapped["Prestazione"] = relationship(
        back_populates="ricette_collegate"
    )
    prenotazione: Mapped[Optional["Prenotazione"]] = relationship(
        back_populates="ricetta_prestazione"
    )


class Prenotazione(Base):
    __tablename__ = "prenotazione"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_prenotazione: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    note_paziente: Mapped[Optional[str]] = mapped_column(String(255))
    stato_pren: Mapped[str] = mapped_column(String(20))

    id_paziente: Mapped[int] = mapped_column(
        ForeignKey("utente_paziente.id", ondelete="CASCADE")
    )
    id_ricetta_prestazione: Mapped[int] = mapped_column(
        ForeignKey("ricetta_prestazione.id", ondelete="RESTRICT")
    )
    id_slot: Mapped[int] = mapped_column(ForeignKey("slot.id", ondelete="RESTRICT"))

    paziente: Mapped["UtentePaziente"] = relationship(back_populates="prenotazioni")
    ricetta_prestazione: Mapped["RicettaPrestazione"] = relationship(
        back_populates="prenotazione"
    )
    slot: Mapped["Slot"] = relationship(back_populates="prenotazioni")
